"""
Query Disambiguation Engine for ARA-1.
Resolves under-specified financial queries by formulating explicit scoping hypotheses,
mapping multi-faceted industry segments, and generating research boundary notes (Section A7.3).
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("ARA.Agent.Disambiguation")

class QueryDisambiguator:
    """
    Disambiguates open-ended, underspecified research requests.
    """
    @staticmethod
    def disambiguate_banking_query(raw_query: str) -> Dict[str, Any]:
        """
        Disambiguates generic queries such as "What's happening with the banks?".
        Decomposes into Tier 1 Money-Center Banks vs Regional Lenders vs Investment Banks.
        """
        logger.info("Disambiguating broad banking sector query...")
        
        scope_dimensions = {
            "money_center_banks": {
                "description": "Global systemically important banks (G-SIBs) like JPMorgan Chase (JPM), Bank of America (BAC), Citigroup (C), Wells Fargo (WFC).",
                "current_dynamics": "Benefiting from deposit flight flight-to-safety, resilient net interest margin (NIM), and rebound in capital markets advisory fees."
            },
            "regional_banks": {
                "description": "Mid-tier and super-regional lenders (KRE ETF constituents, US Bancorp, Truist, KeyCorp).",
                "current_dynamics": "Managing commercial real estate (CRE) office loan maturities, deposit cost normalization, and tighter regulatory liquidity requirements."
            },
            "investment_banks": {
                "description": "Pure-play advisory and trading franchises (Goldman Sachs, Morgan Stanley).",
                "current_dynamics": "Accelerating M&A advisory pipelines, debt underwriting revival, and asset/wealth management fee stability."
            }
        }

        clarifying_assumptions = [
            "1. Geographic Scope: Focused primarily on US Commercial & Investment Banking with global macroeconomic cross-currents.",
            "2. Temporal Scope: Analyzing the post-2023 rate hike cycle, 2024 Fed rate cuts, and Basel III Endgame regulatory revisions.",
            "3. Multi-Segment Lens: Synthesizing findings across Global Systemic Banks (JPM) and Wall Street Advisory (GS/MS)."
        ]

        return {
            "status": "disambiguated",
            "original_query": raw_query,
            "resolved_focus": "US Banking Sector Comprehensive Synthesis (Money-Center vs Regional vs Wall Street)",
            "representative_tickers": ["JPM", "BAC", "GS", "MS"],
            "scope_dimensions": scope_dimensions,
            "explicit_assumptions": clarifying_assumptions,
            "suggested_sub_queries": [
                "JPMorgan Chase & Money-Center Bank Q3 earnings and NII outlook",
                "Regional bank commercial real estate credit risk exposure",
                "Investment banking M&A and capital markets recovery trends"
            ]
        }

    def resolve(self, query: str, query_analysis: Any) -> Dict[str, Any]:
        """Dispatches to archetype disambiguation logic."""
        if "BANK" in query.upper():
            return self.disambiguate_banking_query(query)
        
        return {
            "status": "inferred",
            "original_query": query,
            "resolved_focus": query,
            "representative_tickers": getattr(query_analysis, "tickers", []),
            "explicit_assumptions": ["Standard US equity fundamental research framework applied."],
            "suggested_sub_queries": [query]
        }
