"""
Central Tool Registry for ARA-1.
Manages tool definitions, OpenAI-compliant schema exposure, execution routing,
rate limiting, result caching, execution telemetry, and simulated failure injection.
"""

import time
import json
import logging
import hashlib
from typing import Dict, Any, Callable, Optional, List
from .schemas.tool_schemas import ALL_TOOL_SCHEMAS

logger = logging.getLogger("ARA.ToolRegistry")

class ToolExecutionError(Exception):
    """Raised when tool execution encounters an unrecoverable failure."""
    def __init__(self, tool_name: str, message: str, raw_error: Optional[Exception] = None):
        super().__init__(f"Tool [{tool_name}] failed: {message}")
        self.tool_name = tool_name
        self.message = message
        self.raw_error = raw_error


class ToolRegistry:
    """
    Central registry that catalogs, validates, and dispatches tool executions.
    """
    def __init__(self, cache_ttl_seconds: int = 3600):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = dict(ALL_TOOL_SCHEMAS)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl: int = cache_ttl_seconds
        
        # Telemetry & Call metrics
        self._metrics: Dict[str, Dict[str, Any]] = {}
        for tool_name in self._schemas:
            self._metrics[tool_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "cache_hits": 0,
                "total_latency_ms": 0.0,
                "last_call_timestamp": None
            }
            
        # Simulated failure parameters for stress tests and Challenge 8
        self._simulated_failure_rate: float = 0.0
        self._simulated_failure_tools: List[str] = []

    def register_tool(self, name: str, handler: Callable, schema: Optional[Dict[str, Any]] = None):
        """Registers a Python function handler for a tool."""
        self._tools[name] = handler
        if schema:
            self._schemas[name] = schema
        elif name not in self._schemas:
            raise ValueError(f"Schema for tool '{name}' must be provided if not present in default schemas.")
        
        if name not in self._metrics:
            self._metrics[name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "cache_hits": 0,
                "total_latency_ms": 0.0,
                "last_call_timestamp": None
            }
        logger.debug("Registered tool: %s", name)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns tool schemas in OpenAI function-calling format."""
        return [
            {"type": "function", "function": schema}
            for schema in self._schemas.values()
        ]

    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        return self._schemas.get(name)

    def list_tools(self) -> List[str]:
        return list(self._schemas.keys())

    def set_simulated_failures(self, failure_rate: float, target_tools: Optional[List[str]] = None):
        """Enables simulated probabilistic tool failure for degradation benchmarking."""
        self._simulated_failure_rate = max(0.0, min(1.0, failure_rate))
        self._simulated_failure_tools = target_tools or list(self._schemas.keys())
        logger.info(
            "Simulated failures active: rate=%.2f on tools=%s",
            self._simulated_failure_rate, self._simulated_failure_tools
        )

    def _compute_cache_key(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        serialized = json.dumps({"tool": tool_name, "args": kwargs}, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def execute(self, tool_name: str, bypass_cache: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Executes a registered tool with validation, caching, telemetry, and error handling.
        """
        if tool_name not in self._tools:
            # Check if we have a registered tool handler
            raise ToolExecutionError(tool_name, f"Tool '{tool_name}' is not registered in runtime executor.")

        metric = self._metrics[tool_name]
        metric["total_calls"] += 1
        metric["last_call_timestamp"] = time.time()

        # Check Simulated Failure
        if self._simulated_failure_rate > 0.0 and tool_name in self._simulated_failure_tools:
            import random
            if random.random() < self._simulated_failure_rate:
                metric["failed_calls"] += 1
                logger.warning("Simulated 503 Service Unavailable failure triggered for tool: %s", tool_name)
                raise ToolExecutionError(
                    tool_name,
                    f"SIMULATED_OUTAGE: 503 Service Unavailable / Rate Limit Exceeded on {tool_name}"
                )

        # Check Cache
        cache_key = self._compute_cache_key(tool_name, kwargs)
        now = time.time()
        if not bypass_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["timestamp"] < self._cache_ttl:
                metric["cache_hits"] += 1
                metric["successful_calls"] += 1
                logger.debug("Cache hit for tool: %s", tool_name)
                return entry["result"]

        # Validate required arguments
        schema = self._schemas.get(tool_name, {})
        required_args = schema.get("parameters", {}).get("required", [])
        missing_args = [arg for arg in required_args if arg not in kwargs or kwargs[arg] is None]
        if missing_args:
            metric["failed_calls"] += 1
            raise ToolExecutionError(tool_name, f"Missing required arguments: {missing_args}")

        # Execute
        start_time = time.perf_counter()
        try:
            handler = self._tools[tool_name]
            result = handler(**kwargs)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            
            metric["successful_calls"] += 1
            metric["total_latency_ms"] += latency_ms

            # Wrap in structured result if not already a dict
            if not isinstance(result, dict):
                structured_result = {
                    "status": "success",
                    "tool": tool_name,
                    "data": result,
                    "execution_time_ms": round(latency_ms, 2)
                }
            else:
                structured_result = result
                if "status" not in structured_result:
                    structured_result["status"] = "success"
                structured_result["execution_time_ms"] = round(latency_ms, 2)

            # Store in cache
            self._cache[cache_key] = {
                "timestamp": now,
                "result": structured_result
            }
            return structured_result

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            metric["failed_calls"] += 1
            metric["total_latency_ms"] += latency_ms
            logger.error("Error executing %s: %s", tool_name, str(e))
            if isinstance(e, ToolExecutionError):
                raise e
            raise ToolExecutionError(tool_name, str(e), raw_error=e)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Returns consolidated metrics across all tools."""
        total_calls = sum(m["total_calls"] for m in self._metrics.values())
        successful_calls = sum(m["successful_calls"] for m in self._metrics.values())
        failed_calls = sum(m["failed_calls"] for m in self._metrics.values())
        cache_hits = sum(m["cache_hits"] for m in self._metrics.values())
        total_latency = sum(m["total_latency_ms"] for m in self._metrics.values())
        
        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "cache_hits": cache_hits,
            "average_latency_ms": round(total_latency / total_calls, 2) if total_calls > 0 else 0.0,
            "per_tool_metrics": self._metrics
        }
