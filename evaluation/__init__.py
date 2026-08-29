"""
ARA-1 Evaluation Framework Package.
"""

from .metrics import ResearchEvaluator, QualityMetricResult
from .dashboard import EvaluationDashboard

__all__ = [
    "ResearchEvaluator",
    "QualityMetricResult",
    "EvaluationDashboard"
]
