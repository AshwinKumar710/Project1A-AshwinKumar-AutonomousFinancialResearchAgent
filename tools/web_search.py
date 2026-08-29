"""
Web Search Tool for ARA-1.
Retrieves recent financial headlines, news snippets, and analyst commentary
across verified tier-5 and tier-6 web sources.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ARA.Tools.WebSearch")

MOCK_SEARCH_INDEX = {
    "MSFT": [
        {"title": "Microsoft Cloud and AI Drive FY24 Outperformance", "url": "https://www.reuters.com/technology/msft-fy24-earnings", "date": "2024-08-01", "snippet": "Microsoft reports full year 2024 cloud revenue surpassing $137B with Azure accelerating 29% constant currency, fueled by OpenAI enterprise integrations."},
        {"title": "Satya Nadella Details Copilot Monetization and CapEx Scaling", "url": "https://www.bloomberg.com/news/articles/nadella-ai-capex", "date": "2024-08-15", "snippet": "Microsoft expands data center capacity globally, planning over $50B in capital expenditures to meet generative AI compute demand."},
        {"title": "Microsoft Copilot Sees Enterprise Adoption Across Fortune 500", "url": "https://www.wsj.com/tech/microsoft-copilot-adoption", "date": "2024-09-02", "snippet": "More than 60% of the Fortune 500 now use Microsoft 365 Copilot, with average seat expansion rates exceeding 40% quarter-over-quarter."}
    ],
    "AAPL": [
        {"title": "Apple Q4 Earnings Beat Expectations on Services Strength", "url": "https://www.reuters.com/technology/apple-q4-results-2024", "date": "2024-11-02", "snippet": "Apple reported Q4 revenue of $94.9B with Services hitting record $25B, offsetting slight iPhone China weakness."},
        {"title": "Apple Intelligence Rollout Staggers Across Global Markets", "url": "https://www.ft.com/content/apple-intelligence-rollout", "date": "2024-11-10", "snippet": "Analysts debate the pacing of Apple's AI features in iOS 18.1 and the potential supercycle upgrade timing for iPhone 16/17."},
        {"title": "DOJ Antitrust Lawsuit Against Apple Enters Pre-Trial Phase", "url": "https://www.bloomberg.com/news/apple-antitrust-doj", "date": "2024-10-20", "snippet": "Department of Justice continues scrutiny of Apple's walled garden ecosystem and App Store developer fee structures."}
    ],
    "TSLA": [
        {"title": "Tesla Q3 Automotive Margins Recover on Lower Cost Per Vehicle", "url": "https://www.reuters.com/business/autos-transportation/tesla-q3-results", "date": "2024-10-24", "snippet": "Tesla shares surge 22% after reporting automotive gross margin ex-regulatory credits improved to 17.1% with COGS per vehicle dropping under $35,100."},
        {"title": "Elon Musk Outlines Cybercab and Unsupervised FSD Rollout by 2026", "url": "https://www.bloomberg.com/news/tesla-we-robot-event", "date": "2024-10-12", "snippet": "At the 'We, Robot' event in Burbank, Tesla unveiled the Cybercab autonomous taxi and Robovan, while reiterating autonomous FSD regulatory hurdles."},
        {"title": "NHTSA Opens Safety Probe into 2.4M Tesla Vehicles Over FSD Fog/Glare Crashes", "url": "https://www.wsj.com/business/autos/nhtsa-tesla-fsd-investigation", "date": "2024-10-18", "snippet": "Federal safety regulators launch preliminary evaluation following four collisions involving FSD in reduced visibility conditions."}
    ],
    "NVDA": [
        {"title": "NVIDIA Blackwell Architecture Ramps to Meet Unprecedented AI Demand", "url": "https://www.reuters.com/technology/nvidia-blackwell-gpu-demand", "date": "2024-11-15", "snippet": "CEO Jensen Huang confirms Blackwell B200 GPUs are in full production with customer demand described as extraordinary and outstripping supply for several quarters."},
        {"title": "Hyperscaler CapEx Surge Guarantees Robust NVIDIA Order Book", "url": "https://www.ft.com/content/hyperscaler-ai-capex-nvidia", "date": "2024-11-20", "snippet": "Big Tech cloud titans (Microsoft, Alphabet, Meta, Amazon) project over $200B in combined 2024/2025 CapEx, overwhelmingly directed towards NVIDIA AI compute clusters."},
        {"title": "Export Controls Reshape NVIDIA's China Strategy and Tailored Chips", "url": "https://www.wsj.com/tech/nvidia-china-export-restrictions", "date": "2024-10-05", "snippet": "NVIDIA navigates tightened US Department of Commerce restrictions on H20 chips designed for the Chinese market."}
    ],
    "PLTR": [
        {"title": "Palantir S&P 500 Inclusion Caps Historic Turnaround in Enterprise AI", "url": "https://www.reuters.com/business/palantir-sp500-inclusion", "date": "2024-09-10", "snippet": "Palantir joins the S&P 500 index after delivering four consecutive quarters of GAAP net income, driven by US commercial AIP growth."},
        {"title": "Palantir Commercial Bootcamp Strategy Accelerates Enterprise Deal Velocity", "url": "https://www.bloomberg.com/news/palantir-aip-bootcamps", "date": "2024-10-01", "snippet": "Enterprise customers sign production contracts within days of completing hands-on AIP bootcamps, expanding US commercial customer count by 83% YoY."},
        {"title": "Skeptics Question Palantir's Premium Valuation Multiple Above 80x P/E", "url": "https://www.wsj.com/market-data/palantir-valuation-debate", "date": "2024-10-15", "snippet": "Short-sellers and value analysts argue Palantir's forward multiple leaves little room for execution error despite accelerating defense and commercial backlog."}
    ],
    "BANKS": [
        {"title": "US Major Banks Navigate Net Interest Income Inflection and Basel III Endgame", "url": "https://www.bloomberg.com/news/us-banks-nii-basel", "date": "2024-10-15", "snippet": "JPMorgan Chase, Bank of America, and Citigroup report resilient credit quality and rebounding investment banking fees as Federal Reserve begins rate-cutting cycle."},
        {"title": "Regional Banks Stabilize Deposits Following 2023 SVB Crisis Shockwaves", "url": "https://www.reuters.com/business/finance/regional-banks-liquidity-2024", "date": "2024-09-25", "snippet": "FDIC reports commercial real estate (CRE) office exposure remains the primary credit risk, but liquidity cushions and core deposit costs have normalized."},
        {"title": "Investment Banking Revival Boosts Wall Street Advisory and Underwriting Revenues", "url": "https://www.ft.com/content/investment-banking-revival-2024", "date": "2024-10-22", "snippet": "M&A advisory and debt capital markets underwriting surge over 30% YoY across top tier investment banks (JPMorgan, Goldman Sachs, Morgan Stanley)."}
    ]
}

def execute_web_search(query: str, num_results: int = 5, date_range: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes web search for financial news, market commentary, and company developments.
    """
    logger.info("Executing web search: query='%s', num_results=%d", query, num_results)
    
    query_upper = query.upper()
    results: List[Dict[str, Any]] = []

    for key, items in MOCK_SEARCH_INDEX.items():
        if key in query_upper:
            results.extend(items)
            break

    if not results:
        # Check topic keywords
        if "BANK" in query_upper or "FINANCIAL" in query_upper:
            results = MOCK_SEARCH_INDEX["BANKS"]
        elif "CLOUD" in query_upper or "AWS" in query_upper or "AZURE" in query_upper:
            results = [
                {"title": "Cloud Infrastructure Market Share: AWS, Azure, GCP Battle for Generative AI Workloads", "url": "https://www.gartner.com/cloud-market-2024", "date": "2024-10-01", "snippet": "AWS maintains ~31% market share, Azure holds ~25% with rapid AI acceleration, and Google Cloud reaches ~11% market share and achieving operating profitability."},
                {"title": "Enterprise Cloud Spending Re-Accelerates After 2023 Optimization Wave", "url": "https://www.idc.com/cloud-spending-2024", "date": "2024-09-18", "snippet": "Enterprises transition from cost optimization to new AI workload deployment across hybrid and multi-cloud architectures."}
            ]
        else:
            results = [
                {"title": f"Market Analysis and Financial Updates: {query}", "url": f"https://www.bloomberg.com/search?q={query.replace(' ', '+')}", "date": "2024-10-01", "snippet": f"Comprehensive financial coverage, regulatory disclosures, and market dynamics related to {query}."},
                {"title": f"Industry Trends and Analyst Forecasts: {query}", "url": f"https://www.reuters.com/search/news?blob={query.replace(' ', '+')}", "date": "2024-09-20", "snippet": f"In-depth industry perspective, quarterly earnings sentiment, and macroeconomic context for {query}."}
            ]

    clipped_results = results[:num_results]
    return {
        "status": "success",
        "query": query,
        "results_count": len(clipped_results),
        "source_tier": "Tier 5 (Major Financial Media)",
        "results": clipped_results
    }
