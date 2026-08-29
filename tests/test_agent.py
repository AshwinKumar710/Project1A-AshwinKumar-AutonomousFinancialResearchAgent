"""
Unit Tests for ARA-1 Agent Core, Circuit Breaker, Query Disambiguation, and Fallbacks.
"""

import pytest
import time
from agent.core import AutonomousResearchAgent
from agent.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpenException
from agent.error_handler import ErrorManager, RetryPolicy
from agent.query_analyzer import QueryAnalyzer
from agent.disambiguation import QueryDisambiguator
from agent.parser import ReActParser

def test_circuit_breaker_tripping_and_recovery():
    cb = CircuitBreaker(service_name="test_service", failure_threshold=2, recovery_timeout_sec=0.2)
    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True

    # Record 2 failures -> trip
    cb.record_failure(Exception("Fail 1"))
    cb.record_failure(Exception("Fail 2"))
    assert cb.state == CircuitState.OPEN

    # In open state, request should be denied
    with pytest.raises(CircuitBreakerOpenException):
        cb.allow_request()

    # Wait for recovery timeout
    time.sleep(0.25)
    assert cb.allow_request() is True # Transitions to HALF_OPEN
    assert cb.state == CircuitState.HALF_OPEN

    # Record success -> resets to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED

def test_query_analyzer_and_disambiguation():
    analyzer = QueryAnalyzer()
    
    # Single company
    res1 = analyzer.analyze("Create a comprehensive profile of Microsoft")
    assert res1.query_archetype == "single_company_profile"
    assert "MSFT" in res1.tickers

    # Ambiguous banking
    res2 = analyzer.analyze("What's happening with the banks?")
    assert res2.is_ambiguous is True
    assert res2.query_archetype == "ambiguous_query"

    disambiguator = QueryDisambiguator()
    dis_res = disambiguator.resolve("What's happening with the banks?", res2)
    assert dis_res["status"] == "disambiguated"
    assert "money_center_banks" in dis_res["scope_dimensions"]

def test_react_parser():
    text = (
        "Thought: I should search for SEC filings.\n"
        "Action: sec_filing_search\n"
        "Action Input: {\"ticker\": \"AAPL\", \"filing_type\": \"10-K\"}"
    )
    thought, action, args = ReActParser.parse_action(text)
    assert "search for SEC" in thought
    assert action == "sec_filing_search"
    assert args["ticker"] == "AAPL"

def test_autonomous_agent_end_to_end():
    agent = AutonomousResearchAgent()
    result = agent.execute_research("Create a profile of Microsoft Corporation")
    assert result["status"] == "success"
    assert len(result["report_markdown"]) > 500
    assert result["metrics"]["tool_calls_count"] >= 3
    assert result["metrics"]["errors_count"] == 0
