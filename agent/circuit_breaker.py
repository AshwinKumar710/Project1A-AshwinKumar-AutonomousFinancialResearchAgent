"""
Circuit Breaker Implementation for ARA-1.
Protects external API endpoints from cascading failures and rate-limit thrashing.
Implements CLOSED, OPEN, and HALF_OPEN state machine with auto-recovery timeout.
"""

import time
import logging
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger("ARA.Resilience.CircuitBreaker")

class CircuitState(Enum):
    CLOSED = "CLOSED"         # Normal operation: requests pass through
    OPEN = "OPEN"             # Tripped: requests fail fast without calling external API
    HALF_OPEN = "HALF_OPEN"   # Probing: trial request allowed to verify service recovery


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted on an OPEN circuit."""
    def __init__(self, service_name: str, retry_after_sec: float):
        super().__init__(f"Circuit Breaker for '{service_name}' is OPEN. Retry in {retry_after_sec:.1f}s.")
        self.service_name = service_name
        self.retry_after_sec = retry_after_sec


class CircuitBreaker:
    """
    Tracks failure rates for a specific tool/service and manages trip state.
    """
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 3,
        recovery_timeout_sec: float = 15.0,
        half_open_max_trials: int = 1
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.half_open_max_trials = half_open_max_trials

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()
        self.trip_count = 0

    def record_success(self):
        """Notifies the circuit breaker of a successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("CircuitBreaker [%s]: Probe succeeded. Resetting state to CLOSED.", self.service_name)
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count += 1

    def record_failure(self, error: Optional[Exception] = None):
        """Notifies the circuit breaker of an operation failure."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.warning(
            "CircuitBreaker [%s]: Failure recorded (%d/%d). Error: %s",
            self.service_name, self.failure_count, self.failure_threshold, str(error)
        )

        if self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.trip_count += 1
                self.last_state_change = time.time()
                logger.error(
                    "CircuitBreaker [%s]: TRIP! Threshold reached. State changed to OPEN (trip_count=%d).",
                    self.service_name, self.trip_count
                )

    def allow_request(self) -> bool:
        """
        Determines whether an execution attempt is permitted.
        Transitions OPEN -> HALF_OPEN if recovery timeout has elapsed.
        """
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            elapsed = now - self.last_state_change
            if elapsed >= self.recovery_timeout_sec:
                logger.info(
                    "CircuitBreaker [%s]: Recovery timeout (%.1fs) elapsed. Transitioning OPEN -> HALF_OPEN probe.",
                    self.service_name, self.recovery_timeout_sec
                )
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            else:
                retry_after = self.recovery_timeout_sec - elapsed
                raise CircuitBreakerOpenException(self.service_name, retry_after)

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "trip_count": self.trip_count,
            "last_state_change": self.last_state_change
        }
