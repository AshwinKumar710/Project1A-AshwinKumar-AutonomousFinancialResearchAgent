"""
Unit Tests for all 12 ARA-1 Financial Tools & Tool Registry.
"""

import pytest
from tools.tool_registry import ToolRegistry, ToolExecutionError
from tools import (
    create_default_tool_registry,
    search_sec_filings,
    get_financial_data,
    execute_web_search,
    analyze_news_sentiment,
    get_earnings_transcript,
    get_company_profile,
    compare_peers,
    execute_financial_calculation,
    check_fact,
    format_research_report
)

def test_tool_registry_initialization():
    registry = create_default_tool_registry()
    tools = registry.list_tools()
    assert len(tools) >= 12
    assert "sec_filing_search" in tools
    assert "financial_data_api" in tools
    assert "calculation_engine" in tools
    assert "fact_checker" in tools

def test_sec_filing_search():
    result = search_sec_filings(ticker="MSFT", filing_type="10-K", year=2024)
    assert result["status"] == "success"
    assert result["ticker"] == "MSFT"
    assert "0000950170-24-087843" in result["accession_number"]
    assert "Azure" in result["content"]

def test_financial_data_api():
    result = get_financial_data(ticker="AAPL", statement_type="all")
    assert result["status"] == "success"
    fin_data = result["financial_data"]
    assert "income_statement" in fin_data
    assert fin_data["income_statement"]["2024"]["total_revenue"] == 391035

def test_web_search():
    result = execute_web_search(query="Microsoft AI Cloud", num_results=3)
    assert result["status"] == "success"
    assert len(result["results"]) > 0
    assert "title" in result["results"][0]

def test_news_sentiment():
    result = analyze_news_sentiment(query="NVDA")
    assert result["status"] == "success"
    assert result["sentiment_profile"]["overall_sentiment"] == "Extremely Bullish"
    assert result["sentiment_profile"]["polarity_score"] > 0.5

def test_earnings_transcript():
    result = get_earnings_transcript(ticker="TSLA", quarter="Q3", year=2024)
    assert result["status"] == "success"
    assert "Elon Musk" in result["transcript_text"]
    assert "35,100" in result["transcript_text"]

def test_company_profile():
    result = get_company_profile(ticker="PLTR")
    assert result["status"] == "success"
    assert result["profile"]["ceo"] == "Alex Karp"
    assert result["profile"]["sector"] == "Information Technology"

def test_peer_comparison():
    result = compare_peers(ticker="MSFT", num_peers=3)
    assert result["status"] == "success"
    assert len(result["comparison"]["matrix"]) >= 3

def test_calculation_engine_dcf():
    inputs = {
        "fcf_base": 74000,
        "growth_rates": [0.15, 0.12, 0.10, 0.08, 0.06],
        "terminal_growth": 0.03,
        "wacc": 0.085,
        "shares_outstanding": 7430,
        "net_debt": 31766
    }
    result = execute_financial_calculation(calculation_type="dcf", inputs=inputs)
    assert result["status"] == "success"
    assert result["valuation_summary"]["implied_share_price_usd"] > 0

def test_calculation_engine_dupont():
    inputs = {
        "net_income": 88136,
        "revenue": 245120,
        "operating_income": 109400,
        "ebt": 108000,
        "total_assets": 512163,
        "stockholders_equity": 268480
    }
    result = execute_financial_calculation(calculation_type="dupont", inputs=inputs)
    assert result["status"] == "success"
    assert result["three_stage"]["implied_roe_pct"] > 30.0

def test_fact_checker():
    result = check_fact(claim="Palantir is struggling with losses", ticker="PLTR")
    assert result["status"] == "success"
    assert result["verification_status"] == "CONTRADICTION_FOUND"

def test_report_generator():
    sections = {
        "Executive Summary": "Solid execution in fiscal 2024.",
        "Financial Analysis": "Revenue expanded +16% YoY."
    }
    result = format_research_report(
        title="Microsoft Initiation",
        template="company_profile",
        sections=sections,
        metadata={"ticker": "MSFT"}
    )
    assert result["status"] == "success"
    assert "# Microsoft Initiation" in result["markdown_report"]

def test_tool_registry_caching():
    registry = create_default_tool_registry()
    res1 = registry.execute("company_profile", ticker="MSFT")
    res2 = registry.execute("company_profile", ticker="MSFT")
    metrics = registry.get_metrics_summary()
    assert metrics["cache_hits"] >= 1
