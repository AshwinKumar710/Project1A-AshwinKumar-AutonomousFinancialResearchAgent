"""
Fallback Chains & Graceful Degradation Router for ARA-1.
Defines multi-tier alternate tools and data transformation pipelines (Section A4.3)
to ensure continuous execution even during partial or severe API outages.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from .error_handler import ErrorManager

logger = logging.getLogger("ARA.Resilience.FallbackChains")

class FallbackExecutionChain:
    """
    Manages structured fallback routing for tools with circuit breaker protection.
    """
    def __init__(self, tool_registry, error_manager: Optional[ErrorManager] = None):
        self.tool_registry = tool_registry
        self.error_manager = error_manager or ErrorManager()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Initialize circuit breaker for each known tool
        for tool_name in self.tool_registry.list_tools():
            self.circuit_breakers[tool_name] = CircuitBreaker(service_name=tool_name)

        # Configured fallback chains (Priority order: Primary -> Fallback 1 -> Fallback 2 -> Memory/Cached)
        self.fallback_map: Dict[str, List[Dict[str, Any]]] = {
            "financial_data_api": [
                {
                    "fallback_tool": "sec_filing_search",
                    "param_mapper": lambda kwargs: {"ticker": kwargs.get("ticker"), "filing_type": "10-K", "section": "Item 8 (Financial Statements)"},
                    "description": "Extract raw financial statements from SEC 10-K regulatory filing."
                },
                {
                    "fallback_tool": "web_search",
                    "param_mapper": lambda kwargs: {"query": f"{kwargs.get('ticker')} financial statements revenue net income 2024"},
                    "description": "Search verified financial press releases and earnings summaries via web search."
                },
                {
                    "fallback_tool": "vector_db_search",
                    "param_mapper": lambda kwargs: {"query": f"{kwargs.get('ticker')} financial performance", "ticker_filter": kwargs.get("ticker")},
                    "description": "Retrieve previously cached financial statements from semantic vector memory."
                }
            ],
            "sec_filing_search": [
                {
                    "fallback_tool": "financial_data_api",
                    "param_mapper": lambda kwargs: {"ticker": kwargs.get("ticker"), "statement_type": "all"},
                    "description": "Fallback to structured financial database for fundamental statements."
                },
                {
                    "fallback_tool": "web_search",
                    "param_mapper": lambda kwargs: {"query": f"{kwargs.get('ticker')} SEC {kwargs.get('filing_type', '10-K')} risk factors MD&A"},
                    "description": "Retrieve summarized SEC regulatory highlights via financial web search."
                }
            ],
            "earnings_transcript": [
                {
                    "fallback_tool": "web_search",
                    "param_mapper": lambda kwargs: {"query": f"{kwargs.get('ticker')} earnings call transcript {kwargs.get('quarter', 'Q4')} {kwargs.get('year', 2024)} prepared remarks"},
                    "description": "Search financial news for earnings call executive quotes and Q&A transcripts."
                },
                {
                    "fallback_tool": "news_sentiment",
                    "param_mapper": lambda kwargs: {"query": f"{kwargs.get('ticker')} earnings call sentiment"},
                    "description": "Extract earnings sentiment tone and management guidance signals."
                }
            ],
            "news_sentiment": [
                {
                    "fallback_tool": "web_search",
                    "param_mapper": lambda kwargs: {"query": f"{kwargs.get('query')} news sentiment analysis 2024"},
                    "description": "Retrieve recent news articles directly via web search and evaluate tone."
                }
            ],
            "peer_comparison": [
                {
                    "fallback_tool": "financial_data_api",
                    "param_mapper": lambda kwargs: {"ticker": kwargs.get("ticker"), "statement_type": "ratios"},
                    "description": "Compute single-company ratios and compare against industry baseline."
                }
            ]
        }

    def execute_with_fallback(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Attempts execution on primary tool; if it fails or circuit breaker is open,
        cascades down the configured fallback chain.
        """
        cb = self.circuit_breakers.get(tool_name)
        primary_failed = False
        primary_error_msg = ""

        # Step 1: Attempt primary tool if circuit breaker allows
        try:
            if cb and cb.allow_request():
                result = self.tool_registry.execute(tool_name, **kwargs)
                if cb:
                    cb.record_success()
                return result
        except Exception as e:
            primary_failed = True
            primary_error_msg = str(e)
            if cb:
                cb.record_failure(e)
            logger.warning(
                "Primary tool [%s] failed: %s. Initiating fallback chain...",
                tool_name, primary_error_msg
            )

        # Step 2: Cascade through fallbacks
        fallbacks = self.fallback_map.get(tool_name, [])
        for idx, fb_config in enumerate(fallbacks, 1):
            fb_tool = fb_config["fallback_tool"]
            fb_cb = self.circuit_breakers.get(fb_tool)
            try:
                if fb_cb and not fb_cb.allow_request():
                    continue

                mapped_params = fb_config["param_mapper"](kwargs)
                logger.info(
                    "Executing Fallback Tier %d for [%s] -> Tool: [%s] (Params: %s)",
                    idx, tool_name, fb_tool, mapped_params
                )
                
                fb_result = self.tool_registry.execute(fb_tool, **mapped_params)
                if fb_cb:
                    fb_cb.record_success()

                # Annotate result with fallback provenance
                if isinstance(fb_result, dict):
                    fb_result["fallback_used"] = True
                    fb_result["original_tool"] = tool_name
                    fb_result["fallback_tier"] = idx
                    fb_result["fallback_description"] = fb_config["description"]
                    fb_result["confidence_penalty"] = 0.05 * idx # Modest penalty for fallback
                
                return fb_result

            except Exception as fb_err:
                logger.warning("Fallback Tier %d [%s] failed: %s", idx, fb_tool, str(fb_err))
                if fb_cb:
                    fb_cb.record_failure(fb_err)
                continue

        # Step 3: Complete degradation if all fallbacks fail
        logger.error("All fallback tiers exhausted for tool [%s]. Recording graceful degradation.", tool_name)
        self.error_manager.record_degradation(
            section_name=f"Tool_{tool_name}",
            missing_source=tool_name,
            impact=f"Could not retrieve fresh primary data via {tool_name} or fallbacks.",
            mitigation="Section annotated with missing data notice; no synthetic data hallucinated."
        )

        return {
            "status": "degraded",
            "tool": tool_name,
            "error": primary_error_msg or "All fallback tools unavailable",
            "message": "DATA_UNAVAILABLE: Tool execution gracefully degraded without fabrication.",
            "confidence_score": 0.0
        }
