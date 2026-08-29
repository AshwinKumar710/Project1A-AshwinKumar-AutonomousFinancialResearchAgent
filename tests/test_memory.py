"""
Unit Tests for ARA-1 Three-Layer Memory Hierarchy.
"""

import pytest
from memory.vector_store import VectorStore, FinancialChunker
from memory.context_manager import ContextManager, TokenBudgeter
from memory.episodic import EpisodicMemory

def test_financial_chunker_sec():
    text = "=== Item 1 (Business) ===\nMicrosoft provides software.\n\n=== Item 1A (Risk Factors) ===\nCompetition is intense."
    chunks = FinancialChunker.chunk_sec_filing(text, ticker="MSFT")
    assert len(chunks) >= 2
    assert chunks[0]["ticker"] == "MSFT"

def test_vector_store_store_and_search():
    store = VectorStore(embedding_dim=64)
    store.store(
        content="Tesla energy storage deployments doubled to 14.7 GWh in fiscal 2023.",
        metadata={"ticker": "TSLA", "source_type": "10-K", "confidence": 0.95}
    )
    store.store(
        content="Apple services revenue reached an all-time record of $96.2 billion.",
        metadata={"ticker": "AAPL", "source_type": "10-K", "confidence": 0.95}
    )

    search_res = store.search(query="Tesla energy storage", top_k=2)
    assert search_res["status"] == "success"
    assert len(search_res["matches"]) >= 1
    assert search_res["matches"][0]["ticker"] == "TSLA"

def test_context_manager_progressive_summarization():
    ctx = ContextManager(max_active_steps=5)
    ctx.initialize_session("Analyze TSLA risk factors")
    
    for i in range(8):
        ctx.add_trace(
            thought=f"Reasoning step {i+1}",
            action=f"tool_call_{i+1}",
            observation=f"Observation output for step {i+1}"
        )
    
    working_ctx = ctx.get_working_context()
    assert len(working_ctx["active_trace_scratchpad"]) <= 5
    assert len(working_ctx["summarized_past_steps"]) > 0

def test_episodic_memory_recommendation():
    ep_mem = EpisodicMemory()
    tools = ep_mem.recommend_strategy("risk_assessment")
    assert "sec_filing_search" in tools
    assert "news_sentiment" in tools

    ep = ep_mem.record_episode(
        query="Analyze Tesla risks",
        query_type="risk_assessment",
        plan_executed=["Step 1", "Step 2"],
        tool_sequence=tools,
        errors_encountered=[],
        recovery_mechanisms=[],
        execution_duration_sec=2.1,
        quality_score=0.95
    )
    assert ep["success"] is True
    assert len(ep_mem.episodes) == 1
