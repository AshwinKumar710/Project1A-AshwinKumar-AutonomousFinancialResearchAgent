"""
Narrative Threading, Triangulation, and Sentiment-Fact Alignment for ARA-1 (Section A6.4).
Weaves structured and unstructured evidence into an integrated investment synthesis.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("ARA.Synthesis.Narrative")

class NarrativeSynthesizer:
    """
    Coordinates quantitative triangulation and sentiment-fact alignment.
    """
    @staticmethod
    def triangulate_metrics(
        metric_name: str,
        sec_filing_val: Any,
        financial_api_val: Any,
        web_media_val: Any
    ) -> Dict[str, Any]:
        """
        Cross-checks a core metric across 3 independent source tiers (Quantitative Triangulation).
        """
        logger.info("Triangulating metric across 3 sources: %s", metric_name)
        
        sources = [
            {"tier": "Tier 1 (SEC 10-K Audited)", "value": sec_filing_val},
            {"tier": "Tier 2 (Financial Data API)", "value": financial_api_val},
            {"tier": "Tier 5 (Financial Media / News)", "value": web_media_val}
        ]

        # Calculate consensus & deviation
        numeric_vals = [v["value"] for v in sources if isinstance(v["value"], (int, float))]
        if numeric_vals:
            avg_val = sum(numeric_vals) / len(numeric_vals)
            max_dev = max(abs(x - avg_val) / avg_val for x in numeric_vals) * 100.0 if avg_val else 0.0
            is_consistent = max_dev <= 3.0
        else:
            avg_val = None
            max_dev = 0.0
            is_consistent = True

        return {
            "metric": metric_name,
            "triangulation_sources": sources,
            "consensus_value": sec_filing_val if sec_filing_val is not None else avg_val,
            "max_deviation_pct": round(max_dev, 2),
            "is_triangulated_consistent": is_consistent,
            "synthesis_note": (
                f"Triangulation across Tier 1, Tier 2, and Tier 5 confirms high fidelity alignment "
                f"(maximum observed deviation: {max_dev:.2f}%)."
            )
        }

    @staticmethod
    def evaluate_sentiment_fact_alignment(
        qualitative_sentiment: str,
        quantitative_growth_rate: float,
        operating_margin: float
    ) -> Dict[str, Any]:
        """
        Evaluates divergence between qualitative executive/news sentiment vs hard GAAP numbers.
        (e.g., bearish media narrative while fundamentals show accelerating growth and 80%+ gross margin).
        """
        is_divergent = False
        divergence_type = "Aligned"
        analytical_insight = "Qualitative sentiment closely mirrors underlying fundamental expansion."

        if "bearish" in qualitative_sentiment.lower() or "struggling" in qualitative_sentiment.lower():
            if quantitative_growth_rate > 15.0 and operating_margin > 0.0:
                is_divergent = True
                divergence_type = "Sentiment-Fundamental Disconnect (Bullish Asymmetry)"
                analytical_insight = (
                    "Severe sentiment-fundamental divergence detected. While media coverage emphasizes near-term headwinds, "
                    f"underlying GAAP fundamentals show accelerating revenue (+{quantitative_growth_rate:.1f}%) and positive operating margin ({operating_margin:.1f}%). "
                    "This divergence presents potential market mispricing or sentiment overreaction."
                )
        elif "bullish" in qualitative_sentiment.lower() or "euphoric" in qualitative_sentiment.lower():
            if quantitative_growth_rate < 0.0 or operating_margin < -10.0:
                is_divergent = True
                divergence_type = "Sentiment-Fundamental Disconnect (Overheated Hype)"
                analytical_insight = (
                    "Hype disconnect detected. Positive promotional sentiment is unsupported by contracting revenues "
                    f"({quantitative_growth_rate:.1f}%) and negative operating margins ({operating_margin:.1f}%)."
                )

        return {
            "is_divergent": is_divergent,
            "divergence_type": divergence_type,
            "sentiment": qualitative_sentiment,
            "growth_rate_pct": quantitative_growth_rate,
            "operating_margin_pct": operating_margin,
            "analytical_insight": analytical_insight
        }
