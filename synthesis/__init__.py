"""
ARA-1 Multi-Source Synthesis Package.
Exposes ConflictResolver, NarrativeSynthesizer, and SynthesisEngine.
"""

from .conflict_resolver import ConflictResolver, ConflictResolutionRecord, SOURCE_TIER_HIERARCHY
from .narrative import NarrativeSynthesizer
from .engine import SynthesisEngine

__all__ = [
    "ConflictResolver",
    "ConflictResolutionRecord",
    "SOURCE_TIER_HIERARCHY",
    "NarrativeSynthesizer",
    "SynthesisEngine"
]
