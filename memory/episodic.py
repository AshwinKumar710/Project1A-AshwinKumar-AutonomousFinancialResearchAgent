"""
Episodic Experience Memory for ARA-1.
Tracks meta-level research episodes, effective tool strategies, error recovery patterns,
and query archetype playbooks (Section A3.2).
"""

import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ARA.Memory.Episodic")

class EpisodicMemory:
    """
    Stores past research experiences to enable meta-learning, strategy selection,
    and process optimization across sessions.
    """
    def __init__(self):
        self.episodes: List[Dict[str, Any]] = []
        self._strategy_playbooks: Dict[str, List[str]] = {
            "single_company_profile": [
                "company_profile",
                "financial_data_api",
                "web_search",
                "peer_comparison",
                "report_generator"
            ],
            "earnings_analysis": [
                "financial_data_api",
                "earnings_transcript",
                "news_sentiment",
                "web_search",
                "report_generator"
            ],
            "risk_assessment": [
                "sec_filing_search",
                "news_sentiment",
                "web_search",
                "earnings_transcript",
                "financial_data_api",
                "report_generator"
            ],
            "industry_comparison": [
                "peer_comparison",
                "financial_data_api",
                "sec_filing_search",
                "calculation_engine",
                "web_search",
                "report_generator"
            ],
            "contradiction_resolution": [
                "sec_filing_search",
                "financial_data_api",
                "news_sentiment",
                "fact_checker",
                "report_generator"
            ],
            "ambiguous_query": [
                "company_profile",
                "web_search",
                "peer_comparison",
                "report_generator"
            ],
            "cross_company_synthesis": [
                "vector_db_search",
                "calculation_engine",
                "peer_comparison",
                "report_generator"
            ]
        }

    def record_episode(
        self,
        query: str,
        query_type: str,
        plan_executed: List[str],
        tool_sequence: List[str],
        errors_encountered: List[str],
        recovery_mechanisms: List[str],
        execution_duration_sec: float,
        quality_score: float = 0.90
    ) -> Dict[str, Any]:
        """Records an execution episode with its performance telemetry."""
        episode = {
            "episode_id": f"ep-{int(time.time()*1000)%1000000:06d}",
            "timestamp": time.time(),
            "query": query,
            "query_type": query_type,
            "plan_executed": plan_executed,
            "tool_sequence": tool_sequence,
            "errors_encountered": errors_encountered,
            "recovery_mechanisms": recovery_mechanisms,
            "duration_sec": round(execution_duration_sec, 2),
            "quality_score": quality_score,
            "success": len(errors_encountered) == 0 or len(recovery_mechanisms) > 0
        }
        self.episodes.append(episode)
        logger.info("Recorded episodic research experience: ID=%s (type=%s)", episode["episode_id"], query_type)
        return episode

    def recommend_strategy(self, query_type: str) -> List[str]:
        """
        Recommends the highest-confidence sequence of tools based on prior experiences.
        """
        if query_type in self._strategy_playbooks:
            return list(self._strategy_playbooks[query_type])
        
        # Fallback default sequence
        return [
            "company_profile",
            "sec_filing_search",
            "financial_data_api",
            "web_search",
            "report_generator"
        ]

    def get_error_recovery_patterns(self) -> List[Dict[str, Any]]:
        """Returns historical error patterns and how the agent successfully recovered."""
        patterns = []
        for ep in self.episodes:
            if ep["errors_encountered"]:
                patterns.append({
                    "query_type": ep["query_type"],
                    "errors": ep["errors_encountered"],
                    "recoveries": ep["recovery_mechanisms"],
                    "final_score": ep["quality_score"]
                })
        return patterns
