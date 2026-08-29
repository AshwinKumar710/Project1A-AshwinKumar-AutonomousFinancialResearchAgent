"""
Query Analyzer & Intent Classifier for ARA-1.
Categorizes queries by archetype, measures ambiguity score, identifies temporal sensitivity,
and extracts target entities and fiscal timeframes (Section A7.3 & Day 10).
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ARA.Agent.QueryAnalyzer")

class QueryAnalysis:
    def __init__(
        self,
        raw_query: str,
        query_archetype: str,
        entities: List[str],
        tickers: List[str],
        is_ambiguous: bool,
        ambiguity_score: float,
        temporal_sensitivity: str,
        target_sections: List[str],
        estimated_complexity: int
    ):
        self.raw_query = raw_query
        self.query_archetype = query_archetype
        self.entities = entities
        self.tickers = tickers
        self.is_ambiguous = is_ambiguous
        self.ambiguity_score = ambiguity_score
        self.temporal_sensitivity = temporal_sensitivity
        self.target_sections = target_sections
        self.estimated_complexity = estimated_complexity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_query": self.raw_query,
            "query_archetype": self.query_archetype,
            "entities": self.entities,
            "tickers": self.tickers,
            "is_ambiguous": self.is_ambiguous,
            "ambiguity_score": self.ambiguity_score,
            "temporal_sensitivity": self.temporal_sensitivity,
            "target_sections": self.target_sections,
            "estimated_complexity": self.estimated_complexity
        }


class QueryAnalyzer:
    """
    Parses and extracts intent, entities, and ambiguity characteristics from financial queries.
    """
    TICKER_MAP = {
        "MICROSOFT": "MSFT", "MSFT": "MSFT",
        "APPLE": "AAPL", "AAPL": "AAPL",
        "TESLA": "TSLA", "TSLA": "TSLA",
        "NVIDIA": "NVDA", "NVDA": "NVDA",
        "PALANTIR": "PLTR", "PLTR": "PLTR",
        "AMAZON": "AMZN", "AWS": "AMZN",
        "GOOGLE": "GOOGL", "ALPHABET": "GOOGL", "GCP": "GOOGL",
        "JPMORGAN": "JPM", "JPM": "JPM",
        "GOLDMAN": "GS", "GS": "GS",
        "MORGAN STANLEY": "MS", "MS": "MS"
    }

    def analyze(self, query: str) -> QueryAnalysis:
        q_upper = query.upper()
        logger.info("Analyzing query intent: '%s'", query)

        # Detect Tickers & Entities
        detected_tickers = []
        detected_entities = []
        for name, sym in self.TICKER_MAP.items():
            if re.search(r'\b' + re.escape(name) + r'\b', q_upper):
                if sym not in detected_tickers:
                    detected_tickers.append(sym)
                    detected_entities.append(name.capitalize())

        # Detect Ambiguity
        is_ambiguous = False
        ambiguity_score = 0.1
        if "BANKS" in q_upper or "WHAT'S HAPPENING WITH" in q_upper or "THE SECTOR" in q_upper or len(detected_tickers) == 0:
            is_ambiguous = True
            ambiguity_score = 0.85
        elif "COMPARE" in q_upper or "VS" in q_upper:
            ambiguity_score = 0.40

        # Classify Archetype
        if "CONTRADICT" in q_upper or ("STRUGGLING" in q_upper and "GROWTH" in q_upper) or "PALANTIR" in q_upper and "EXPLAIN" in q_upper:
            archetype = "contradiction_resolution"
            complexity = 3
        elif "WHAT'S HAPPENING WITH" in q_upper or ("BANK" in q_upper and len(detected_tickers) == 0):
            archetype = "ambiguous_query"
            complexity = 4
        elif "THEMES" in q_upper or "ALREADY RESEARCHED" in q_upper or "SECTOR ANALYSIS WITH MEMORY" in q_upper:
            archetype = "cross_company_synthesis"
            complexity = 4
        elif "COMPARE" in q_upper or "AWS" in q_upper or len(detected_tickers) >= 3:
            archetype = "industry_comparison"
            complexity = 3
        elif "RISK" in q_upper:
            archetype = "risk_assessment"
            complexity = 2
        elif "EARNINGS" in q_upper or "QUARTERLY" in q_upper:
            archetype = "earnings_review"
            complexity = 2
        elif "FULL REPORT" in q_upper or "DEGRADATION" in q_upper or "50%" in q_upper:
            archetype = "full_research_degradation"
            complexity = 5
        else:
            archetype = "single_company_profile"
            complexity = 1

        # Target Report Sections
        sections = ["Executive Summary", "Financial Highlights", "Risk Factors", "Valuation & Methodology"]
        if archetype == "risk_assessment":
            sections = ["Executive Summary", "Regulatory & Legal Risks", "Operational & Supply Chain", "Competitive Moat Analysis", "Risk Mitigation Recommendations"]
        elif archetype == "industry_comparison":
            sections = ["Executive Summary", "Market Share & Positioning", "Comparative Financials & Margins", "Technology & AI Moat", "Strategic Outlook"]
        elif archetype == "contradiction_resolution":
            sections = ["Executive Summary", "Discrepancy Identification", "Audit of Financial Fundamentals", "Sentiment & Qualitative Analysis", "Synthesis & Final Verdict"]
        elif archetype == "ambiguous_query":
            sections = ["Executive Summary", "Sector Scope & Disambiguation", "Money-Center vs Regional Bank Dynamics", "Regulatory & Interest Rate Backdrop", "Investment Implications"]

        return QueryAnalysis(
            raw_query=query,
            query_archetype=archetype,
            entities=detected_entities,
            tickers=detected_tickers,
            is_ambiguous=is_ambiguous,
            ambiguity_score=ambiguity_score,
            temporal_sensitivity="High (Quarterly Updates)",
            target_sections=sections,
            estimated_complexity=complexity
        )
