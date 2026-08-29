"""
Error Handling & Retry Layer for ARA-1.
Implements exponential backoff with jitter (Section A4.3), error classification,
and transparent degradation logging.
"""

import time
import random
import logging
from enum import Enum
from typing import Dict, Any, Callable, List, Optional

logger = logging.getLogger("ARA.Resilience.ErrorHandler")

class ErrorCategory(Enum):
    API_UNAVAILABLE = "API_UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    AUTH_FAILURE = "AUTH_FAILURE"
    MALFORMED_DATA = "MALFORMED_DATA"
    REASONING_ERROR = "REASONING_ERROR"
    UNKNOWN = "UNKNOWN"


class DegradationNote:
    """Records degraded research areas to guarantee no fabricated fillers."""
    def __init__(self, section_name: str, missing_source: str, impact: str, mitigation: str):
        self.section_name = section_name
        self.missing_source = missing_source
        self.impact = impact
        self.mitigation = mitigation
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section": self.section_name,
            "missing_source": self.missing_source,
            "impact": self.impact,
            "mitigation": self.mitigation,
            "timestamp": self.timestamp
        }


class RetryPolicy:
    """
    Executes operations with exponential backoff and randomized jitter.
    Formula: delay = initial_delay * (backoff_factor ** attempt) + uniform(0, max_jitter)
    """
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay_sec: float = 0.5,
        backoff_factor: float = 2.0,
        max_jitter_sec: float = 0.3
    ):
        self.max_retries = max_retries
        self.initial_delay_sec = initial_delay_sec
        self.backoff_factor = backoff_factor
        self.max_jitter_sec = max_jitter_sec

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    logger.error("Retry exhaustion after %d attempts. Error: %s", self.max_retries, str(e))
                    raise e
                
                # Calculate exponential backoff + jitter
                delay = (self.initial_delay_sec * (self.backoff_factor ** attempt)) + random.uniform(0, self.max_jitter_sec)
                logger.warning("Attempt %d failed: %s. Retrying in %.2fs...", attempt + 1, str(e), delay)
                time.sleep(delay)


class ErrorManager:
    """
    Coordinates retries, error diagnostics, and degradation tracking.
    """
    def __init__(self):
        self.retry_policy = RetryPolicy()
        self.degradation_log: List[DegradationNote] = []
        self.error_history: List[Dict[str, Any]] = []

    def classify_error(self, error: Exception) -> ErrorCategory:
        err_msg = str(error).lower()
        if "503" in err_msg or "unavailable" in err_msg or "connection refused" in err_msg:
            return ErrorCategory.API_UNAVAILABLE
        if "rate limit" in err_msg or "429" in err_msg or "too many requests" in err_msg:
            return ErrorCategory.RATE_LIMITED
        if "timeout" in err_msg or "timed out" in err_msg:
            return ErrorCategory.TIMEOUT
        if "401" in err_msg or "403" in err_msg or "unauthorized" in err_msg or "api key" in err_msg:
            return ErrorCategory.AUTH_FAILURE
        if "json" in err_msg or "decode" in err_msg or "missing key" in err_msg:
            return ErrorCategory.MALFORMED_DATA
        return ErrorCategory.UNKNOWN

    def record_degradation(self, section: str = "", missing_source: str = "", impact: str = "", mitigation: str = "", section_name: str = ""):
        sec = section_name or section or "General_Section"
        note = DegradationNote(sec, missing_source, impact, mitigation)
        self.degradation_log.append(note)
        logger.info("Graceful degradation recorded for section '%s': %s", sec, impact)

    def get_degradation_report(self) -> List[Dict[str, Any]]:
        return [note.to_dict() for note in self.degradation_log]
