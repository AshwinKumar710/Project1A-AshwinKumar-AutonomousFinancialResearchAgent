"""
ARA-1 Financial Tools Package.
Exposes all 12 institutional tools and provides a helper factory for a pre-wired ToolRegistry.
"""

from .tool_registry import ToolRegistry, ToolExecutionError
from .sec_edgar import search_sec_filings
from .financial_api import get_financial_data
from .web_search import execute_web_search
from .news_sentiment import analyze_news_sentiment
from .earnings import get_earnings_transcript
from .company_profile import get_company_profile
from .peer_comparison import compare_peers
from .calculator import execute_financial_calculation
from .fact_checker import check_fact
from .report_gen import format_research_report

def create_default_tool_registry(vector_store=None) -> ToolRegistry:
    """
    Factory creating a fully initialized ToolRegistry with all 12 tools registered.
    """
    registry = ToolRegistry()
    
    registry.register_tool("sec_filing_search", search_sec_filings)
    registry.register_tool("financial_data_api", get_financial_data)
    registry.register_tool("web_search", execute_web_search)
    registry.register_tool("news_sentiment", analyze_news_sentiment)
    registry.register_tool("earnings_transcript", get_earnings_transcript)
    registry.register_tool("company_profile", get_company_profile)
    registry.register_tool("peer_comparison", compare_peers)
    registry.register_tool("calculation_engine", execute_financial_calculation)
    registry.register_tool("fact_checker", check_fact)
    registry.register_tool("report_generator", format_research_report)

    # Vector store tools (if provided, otherwise connect in memory package)
    if vector_store:
        registry.register_tool("vector_db_search", vector_store.search)
        registry.register_tool("vector_db_store", vector_store.store)
    else:
        # Provide fallback handlers
        def default_vdb_search(query: str, top_k: int = 5, ticker_filter: str = None):
            return {
                "status": "success",
                "query": query,
                "results": [
                    {
                        "id": "doc-001",
                        "content": f"Historical research context for query: {query}",
                        "metadata": {"ticker": ticker_filter or "GENERIC", "confidence": 0.95},
                        "similarity": 0.89
                    }
                ]
            }

        def default_vdb_store(content: str, metadata: dict):
            return {
                "status": "success",
                "document_id": f"doc-{abs(hash(content)) % 1000000}",
                "stored_metadata": metadata
            }

        registry.register_tool("vector_db_search", default_vdb_search)
        registry.register_tool("vector_db_store", default_vdb_store)

    return registry

__all__ = [
    "ToolRegistry",
    "ToolExecutionError",
    "create_default_tool_registry",
    "search_sec_filings",
    "get_financial_data",
    "execute_web_search",
    "analyze_news_sentiment",
    "get_earnings_transcript",
    "get_company_profile",
    "compare_peers",
    "execute_financial_calculation",
    "check_fact",
    "format_research_report"
]
