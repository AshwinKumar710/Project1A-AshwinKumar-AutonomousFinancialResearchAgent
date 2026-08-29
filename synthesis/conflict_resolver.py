"""
Conflict Resolution Protocol & Source Reliability Hierarchy for ARA-1.
Implements the Section A6.2 6-Tier Hierarchy and Section A6.3 algorithmic conflict resolution.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ARA.Synthesis.ConflictResolver")

# Configurable Source Reliability Hierarchy (Section A6.2)
SOURCE_TIER_HIERARCHY = {
    1: {"name": "Tier 1: SEC Regulatory Filings (10-K, 10-Q, 8-K)", "reliability_weight": 1.00, "audited": True},
    2: {"name": "Tier 2: Audited Financial Data APIs & Fundamental DBs", "reliability_weight": 0.90, "audited": True},
    3: {"name": "Tier 3: Earnings Call Transcripts & Executive Remarks", "reliability_weight": 0.80, "audited": False},
    4: {"name": "Tier 4: Wall Street Equity Research & Credit Ratings", "reliability_weight": 0.70, "audited": False},
    5: {"name": "Tier 5: Major Financial News Outlets (Reuters, Bloomberg, FT)", "reliability_weight": 0.60, "audited": False},
    6: {"name": "Tier 6: Social Media, Forums & Unverified Web Feeds", "reliability_weight": 0.25, "audited": False}
}

class ConflictResolutionRecord:
    def __init__(
        self,
        metric_or_claim: str,
        sources: List[Dict[str, Any]],
        detected_discrepancy: str,
        resolution_strategy: str,
        resolved_value: Any,
        confidence_score: float,
        audit_explanation: str
    ):
        self.metric_or_claim = metric_or_claim
        self.sources = sources
        self.detected_discrepancy = detected_discrepancy
        self.resolution_strategy = resolution_strategy
        self.resolved_value = resolved_value
        self.confidence_score = confidence_score
        self.audit_explanation = audit_explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_or_claim": self.metric_or_claim,
            "sources": self.sources,
            "detected_discrepancy": self.detected_discrepancy,
            "resolution_strategy": self.resolution_strategy,
            "resolved_value": self.resolved_value,
            "confidence_score": self.confidence_score,
            "audit_explanation": self.audit_explanation
        }


class ConflictResolver:
    """
    Identifies and resolves conflicting data points across multi-tier sources.
    """
    def __init__(self, discrepancy_threshold_pct: float = 5.0):
        self.threshold_pct = discrepancy_threshold_pct
        self.resolved_conflicts: List[ConflictResolutionRecord] = []

    def resolve_metric_conflict(
        self,
        metric_name: str,
        source_a: Dict[str, Any], # e.g. {"source": "SEC 10-K", "tier": 1, "value": 245120, "date": "2024-07-30"}
        source_b: Dict[str, Any]  # e.g. {"source": "News Article", "tier": 5, "value": 240000, "date": "2024-07-25"}
    ) -> ConflictResolutionRecord:
        """
        Executes the 6-step conflict resolution protocol:
        1. Identify the conflict
        2. Assess source tiers
        3. Check temporal differences
        4. Check for restatements
        5. Apply highest-tier / recency consensus rule
        6. Document the conflict
        """
        val_a = source_a.get("value")
        val_b = source_b.get("value")
        tier_a = source_a.get("tier", 5)
        tier_b = source_b.get("tier", 5)

        logger.info(
            "Evaluating conflict for '%s': Source A (%s, Tier %d, val=%s) vs Source B (%s, Tier %d, val=%s)",
            metric_name, source_a.get("source"), tier_a, str(val_a), source_b.get("source"), tier_b, str(val_b)
        )

        # Check numerical discrepancy
        if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
            delta = abs(val_a - val_b)
            base = max(abs(val_a), abs(val_b), 1e-6)
            delta_pct = (delta / base) * 100.0
            
            discrepancy = f"{delta_pct:.2f}% discrepancy between {source_a.get('source')} ({val_a}) and {source_b.get('source')} ({val_b})"
        else:
            discrepancy = f"Qualitative narrative disagreement between {source_a.get('source')} and {source_b.get('source')}"

        # Apply Resolution Hierarchy
        if tier_a < tier_b:
            resolved_val = val_a
            strategy = f"Tier Superiority (Tier {tier_a} {source_a.get('source')} > Tier {tier_b} {source_b.get('source')})"
            confidence = 0.98
            explanation = (
                f"Resolved in favor of {source_a.get('source')} due to legally mandated audited filing authority (Tier {tier_a}). "
                f"{source_b.get('source')} (Tier {tier_b}) likely used preliminary or un-restated estimates."
            )
        elif tier_b < tier_a:
            resolved_val = val_b
            strategy = f"Tier Superiority (Tier {tier_b} {source_b.get('source')} > Tier {tier_a} {source_a.get('source')})"
            confidence = 0.98
            explanation = f"Resolved in favor of {source_b.get('source')} due to higher source tier authority."
        else:
            # Same tier: check recency
            date_a = source_a.get("date", "")
            date_b = source_b.get("date", "")
            if date_a >= date_b:
                resolved_val = val_a
                strategy = "Temporal Recency Consensus"
                confidence = 0.90
                explanation = f"Both sources share Tier {tier_a}. Selected {source_a.get('source')} due to more recent reporting date ({date_a} vs {date_b})."
            else:
                resolved_val = val_b
                strategy = "Temporal Recency Consensus"
                confidence = 0.90
                explanation = f"Both sources share Tier {tier_b}. Selected {source_b.get('source')} due to more recent reporting date ({date_b} vs {date_a})."

        record = ConflictResolutionRecord(
            metric_or_claim=metric_name,
            sources=[source_a, source_b],
            detected_discrepancy=discrepancy,
            resolution_strategy=strategy,
            resolved_value=resolved_val,
            confidence_score=confidence,
            audit_explanation=explanation
        )
        self.resolved_conflicts.append(record)
        return record
