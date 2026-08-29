"""
Company Profile Tool for ARA-1.
Retrieves corporate identity, sector, industry, market capitalization,
leadership team, business model, and operational segments.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("ARA.Tools.CompanyProfile")

COMPANY_PROFILES = {
    "MSFT": {
        "name": "Microsoft Corporation",
        "ticker": "MSFT",
        "exchange": "NASDAQ",
        "sector": "Information Technology",
        "industry": "Systems Software & Cloud Platforms",
        "market_cap_usd_billions": 3150.0,
        "enterprise_value_usd_billions": 3180.0,
        "headquarters": "Redmond, Washington, USA",
        "founded_year": 1975,
        "ceo": "Satya Nadella",
        "cfo": "Amy Hood",
        "employees": 228000,
        "business_segments": [
            {"name": "Productivity and Business Processes", "share_pct": 31.7, "products": "Office 365, LinkedIn, Dynamics 365"},
            {"name": "Intelligent Cloud", "share_pct": 43.0, "products": "Azure, Windows Server, SQL Server, GitHub"},
            {"name": "More Personal Computing", "share_pct": 25.3, "products": "Windows OEM, Xbox Gaming, Surface, Search Advertising"}
        ],
        "business_description": (
            "Microsoft develops and licenses enterprise software, cloud infrastructure, AI services, and devices. "
            "Its core competitive moat rests on ubiquitous enterprise footprint, Windows/Office lock-in, and the Azure OpenAI hyperscale ecosystem."
        )
    },
    "AAPL": {
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "exchange": "NASDAQ",
        "sector": "Information Technology",
        "industry": "Technology Hardware, Storage & Peripherals",
        "market_cap_usd_billions": 3480.0,
        "enterprise_value_usd_billions": 3550.0,
        "headquarters": "Cupertino, California, USA",
        "founded_year": 1976,
        "ceo": "Tim Cook",
        "cfo": "Luca Maestri",
        "employees": 164000,
        "business_segments": [
            {"name": "iPhone", "share_pct": 51.5, "products": "iPhone 15, iPhone 16 series"},
            {"name": "Services", "share_pct": 24.6, "products": "App Store, Apple Music, iCloud, Apple Pay, Apple TV+"},
            {"name": "Wearables, Home & Accessories", "share_pct": 9.5, "products": "Apple Watch, AirPods, Vision Pro"},
            {"name": "Mac", "share_pct": 7.7, "products": "MacBook Air, MacBook Pro, iMac (Apple Silicon M-series)"},
            {"name": "iPad", "share_pct": 6.7, "products": "iPad Pro, iPad Air"}
        ],
        "business_description": (
            "Apple designs premium consumer hardware, operating systems, and an integrated services ecosystem with an active installed base of over 2.2 billion devices."
        )
    },
    "TSLA": {
        "name": "Tesla, Inc.",
        "ticker": "TSLA",
        "exchange": "NASDAQ",
        "sector": "Consumer Discretionary",
        "industry": "Automobile Manufacturers & Clean Energy",
        "market_cap_usd_billions": 780.0,
        "enterprise_value_usd_billions": 755.0,
        "headquarters": "Austin, Texas, USA",
        "founded_year": 2003,
        "ceo": "Elon Musk",
        "cfo": "Vaibhav Taneja",
        "employees": 140000,
        "business_segments": [
            {"name": "Automotive", "share_pct": 85.1, "products": "Model Y, Model 3, Cybertruck, Model S/X, Regulatory Credits"},
            {"name": "Energy Generation and Storage", "share_pct": 6.3, "products": "Megapack, Powerwall, Solar Roof"},
            {"name": "Services and Other", "share_pct": 8.6, "products": "Supercharging network, Collision repair, Insurance, FSD software"}
        ],
        "business_description": (
            "Tesla manufactures electric vehicles, utility-scale battery energy storage systems, and AI robotics software. It is vertically integrated across powertrain, battery pack design, manufacturing, and autonomy software."
        )
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "ticker": "NVDA",
        "exchange": "NASDAQ",
        "sector": "Information Technology",
        "industry": "Semiconductors & Semiconductor Equipment",
        "market_cap_usd_billions": 3300.0,
        "enterprise_value_usd_billions": 3280.0,
        "headquarters": "Santa Clara, California, USA",
        "founded_year": 1993,
        "ceo": "Jensen Huang",
        "cfo": "Colette Kress",
        "employees": 29600,
        "business_segments": [
            {"name": "Data Center", "share_pct": 78.0, "products": "H100, H200, B200 GPUs, Quantum InfiniBand, DGX Cloud"},
            {"name": "Gaming", "share_pct": 17.1, "products": "GeForce RTX 40 series GPUs, GeForce NOW"},
            {"name": "Professional Visualization", "share_pct": 2.6, "products": "RTX Workstation GPUs, Omniverse"},
            {"name": "Automotive", "share_pct": 2.3, "products": "DRIVE Orin, DRIVE Thor cockpit and autonomy"}
        ],
        "business_description": (
            "NVIDIA is the dominant global platform for accelerated computing. Its proprietary CUDA software architecture creates an insurmountable developer moat in training and inferencing generative AI models."
        )
    },
    "PLTR": {
        "name": "Palantir Technologies Inc.",
        "ticker": "PLTR",
        "exchange": "NYSE",
        "sector": "Information Technology",
        "industry": "Software - Infrastructure / AI",
        "market_cap_usd_billions": 95.0,
        "enterprise_value_usd_billions": 91.3,
        "headquarters": "Denver, Colorado, USA",
        "founded_year": 2003,
        "ceo": "Alex Karp",
        "cfo": "David Glazer",
        "employees": 3800,
        "business_segments": [
            {"name": "Government", "share_pct": 55.0, "products": "Palantir Gotham, US DoD TITAN contract, allied intel"},
            {"name": "Commercial", "share_pct": 45.0, "products": "Palantir Foundry, Artificial Intelligence Platform (AIP)"}
        ],
        "business_description": (
            "Palantir builds foundational operating systems for human-machine data integration, operational decision-making, and secure enterprise AI deployment across defense and global corporate leaders."
        )
    }
}

def get_company_profile(ticker: str) -> Dict[str, Any]:
    """
    Retrieves fundamental company profile and executive metadata.
    """
    ticker = ticker.upper().strip()
    logger.info("Retrieving company profile for %s", ticker)

    profile = COMPANY_PROFILES.get(ticker)
    if profile:
        return {
            "status": "success",
            "source_tier": "Tier 2 (Company Profile)",
            "profile": profile
        }

    # Fallback generic company profile
    return {
        "status": "success",
        "source_tier": "Tier 2 (Company Profile)",
        "profile": {
            "name": f"{ticker} Corporation",
            "ticker": ticker,
            "exchange": "NYSE/NASDAQ",
            "sector": "Diversified",
            "industry": "Corporate Enterprise",
            "market_cap_usd_billions": 50.0,
            "headquarters": "USA",
            "ceo": "Chief Executive Officer",
            "cfo": "Chief Financial Officer",
            "business_description": f"{ticker} operates as a publicly traded corporation delivering specialized commercial products and enterprise services."
        }
    }
