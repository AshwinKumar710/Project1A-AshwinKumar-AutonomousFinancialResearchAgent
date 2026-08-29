"""
Unit Tests for Synthesis Engine, Conflict Resolution, and Evaluation Metrics.
"""

import pytest
from synthesis.conflict_resolver import ConflictResolver
from synthesis.narrative import NarrativeSynthesizer
from synthesis.engine import SynthesisEngine
from evaluation.metrics import ResearchEvaluator
from evaluation.dashboard import EvaluationDashboard

def test_conflict_resolution_hierarchy():
    resolver = ConflictResolver()
    source_sec = {"source": "SEC 10-K Audited Filing", "tier": 1, "value": 245120, "date": "2024-07-30"}
    source_news = {"source": "Tech Blog Unverified", "tier": 6, "value": 230000, "date": "2024-07-28"}

    res = resolver.resolve_metric_conflict("Microsoft Revenue", source_sec, source_news)
    assert res.resolved_value == 245120
    assert "Tier 1" in res.resolution_strategy
    assert res.confidence_score >= 0.95

def test_sentiment_fact_divergence():
    syn = NarrativeSynthesizer()
    res = syn.evaluate_sentiment_fact_alignment(
        qualitative_sentiment="Bearish media headlines claiming enterprise slowdown",
        quantitative_growth_rate=24.5,
        operating_margin=42.0
    )
    assert res["is_divergent"] is True
    assert "Disconnect" in res["divergence_type"]

def test_evaluation_metrics_and_dashboard():
    evaluator = ResearchEvaluator()
    sample_trace = {
        "steps": [{"action": "sec_filing_search"}, {"action": "financial_data_api"}, {"action": "web_search"}, {"action": "peer_comparison"}],
        "total_duration_sec": 1.25,
        "errors": []
    }
    sample_report = (
        "# Investment Report: Microsoft (MSFT)\n"
        "## Executive Summary\n"
        "Revenue for FY24 reached $245,120M (up from $211,915M in FY23) with Gross Margin of 69.8% and Operating Income of $109,400M. "
        "Audited Tier 1 SEC EDGAR 10-K filing confirms ground truth across all primary sources.\n\n"
        "## Financial Analysis\n"
        "Net income reached $88,136M, Diluted EPS $11.80. Operating cash flow $118,548M, Free cash flow $74,071M. DuPont ROE 36.2%.\n\n"
        "## Comprehensive Risk Assessment\n"
        "Risk Factor 1: Hyperscaler AI CapEx expansion and ROI timeline.\n"
        "Risk Factor 2: Cloud infrastructure competition from AWS and Google Cloud.\n"
        "Risk Factor 3: Regulatory compliance and cybersecurity disclosures.\n\n"
        "## Valuation & Forward Guidance\n"
        "5-year DCF yields an implied fair value per share of $430.00. FY25 forward revenue projected to grow double-digits."
    )
    eval_res = evaluator.evaluate(sample_report, sample_trace)
    assert eval_res["overall_quality_score"] >= 90.0
    assert eval_res["metrics_passed"] >= 20

    dashboard = EvaluationDashboard()
    md = dashboard.generate_markdown_report(eval_res, "Microsoft Profile Benchmark")
    assert "ARA-1 Quality Metrics Evaluation Dashboard" in md
    assert "Passed / Total" in md
