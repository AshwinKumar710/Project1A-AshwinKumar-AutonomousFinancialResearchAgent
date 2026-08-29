"""
Financial Data API Tool for ARA-1.
Retrieves structured financial statements (Income Statement, Balance Sheet, Cash Flow)
and Key Performance Indicators / Ratios for fundamental equity analysis.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ARA.Tools.FinancialAPI")

# Benchmark financial datasets
FINANCIAL_DATA_STORE = {
    "MSFT": {
        "income_statement": {
            "2024": {"total_revenue": 245120, "cogs": 74103, "gross_profit": 171017, "operating_income": 109400, "net_income": 88136, "diluted_eps": 11.80},
            "2023": {"total_revenue": 211915, "cogs": 65863, "gross_profit": 146052, "operating_income": 88523, "net_income": 72361, "diluted_eps": 9.68},
            "2022": {"total_revenue": 198270, "cogs": 62650, "gross_profit": 135620, "operating_income": 83383, "net_income": 72738, "diluted_eps": 9.65}
        },
        "balance_sheet": {
            "2024": {"cash_and_equivalents": 75548, "short_term_investments": 42000, "total_assets": 512163, "total_debt": 107314, "stockholders_equity": 268480, "current_ratio": 1.25, "debt_to_equity": 0.40},
            "2023": {"cash_and_equivalents": 34704, "short_term_investments": 76558, "total_assets": 411976, "total_debt": 99500, "stockholders_equity": 206223, "current_ratio": 1.77, "debt_to_equity": 0.48}
        },
        "cash_flow": {
            "2024": {"operating_cash_flow": 118548, "capital_expenditures": 55700, "free_cash_flow": 74071, "dividends_paid": 21800, "share_repurchases": 17300},
            "2023": {"operating_cash_flow": 87582, "capital_expenditures": 28107, "free_cash_flow": 59475, "dividends_paid": 19800, "share_repurchases": 22245}
        },
        "ratios": {
            "pe_ratio": 35.4,
            "forward_pe": 30.8,
            "ev_ebitda": 24.2,
            "price_to_sales": 13.1,
            "gross_margin": 69.8,
            "operating_margin": 44.6,
            "net_profit_margin": 36.0,
            "roe": 36.2,
            "roa": 19.1,
            "fcf_yield": 2.4,
            "revenue_growth_yoy": 15.7
        }
    },
    "AAPL": {
        "income_statement": {
            "2024": {"total_revenue": 391035, "cogs": 210352, "gross_profit": 180683, "operating_income": 123216, "net_income": 93736, "diluted_eps": 6.08},
            "2023": {"total_revenue": 383285, "cogs": 214137, "gross_profit": 169148, "operating_income": 114301, "net_income": 96995, "diluted_eps": 6.13},
            "2022": {"total_revenue": 394328, "cogs": 223546, "gross_profit": 170782, "operating_income": 119437, "net_income": 99803, "diluted_eps": 6.11}
        },
        "balance_sheet": {
            "2024": {"cash_and_equivalents": 29943, "marketable_securities": 126000, "total_assets": 364980, "total_debt": 106629, "stockholders_equity": 66880, "current_ratio": 0.89, "debt_to_equity": 1.59},
            "2023": {"cash_and_equivalents": 29965, "marketable_securities": 132000, "total_assets": 352583, "total_debt": 111088, "stockholders_equity": 62146, "current_ratio": 0.99, "debt_to_equity": 1.79}
        },
        "cash_flow": {
            "2024": {"operating_cash_flow": 118254, "capital_expenditures": 9450, "free_cash_flow": 108804, "dividends_paid": 15200, "share_repurchases": 95000},
            "2023": {"operating_cash_flow": 110543, "capital_expenditures": 10959, "free_cash_flow": 99584, "dividends_paid": 15025, "share_repurchases": 77550}
        },
        "ratios": {
            "pe_ratio": 33.2,
            "forward_pe": 28.5,
            "ev_ebitda": 23.5,
            "price_to_sales": 8.7,
            "gross_margin": 46.2,
            "operating_margin": 31.5,
            "net_profit_margin": 24.0,
            "roe": 147.2,
            "roa": 26.3,
            "fcf_yield": 3.2,
            "revenue_growth_yoy": 2.0
        }
    },
    "TSLA": {
        "income_statement": {
            "2023": {"total_revenue": 96773, "cogs": 79113, "gross_profit": 17660, "operating_income": 8891, "net_income": 14997, "diluted_eps": 4.30},
            "2022": {"total_revenue": 81462, "cogs": 60609, "gross_profit": 20853, "operating_income": 13656, "net_income": 12583, "diluted_eps": 3.62},
            "2021": {"total_revenue": 53823, "cogs": 40217, "gross_profit": 13606, "operating_income": 6523, "net_income": 5519, "diluted_eps": 1.87}
        },
        "balance_sheet": {
            "2023": {"cash_and_investments": 29094, "total_assets": 106618, "total_debt": 5245, "stockholders_equity": 62634, "current_ratio": 1.73, "debt_to_equity": 0.08}
        },
        "cash_flow": {
            "2023": {"operating_cash_flow": 13256, "capital_expenditures": 8898, "free_cash_flow": 4358, "dividends_paid": 0, "share_repurchases": 0}
        },
        "ratios": {
            "pe_ratio": 68.5,
            "forward_pe": 55.2,
            "ev_ebitda": 38.4,
            "price_to_sales": 7.4,
            "gross_margin": 18.2,
            "operating_margin": 9.2,
            "net_profit_margin": 15.5,
            "roe": 26.8,
            "roa": 15.2,
            "fcf_yield": 0.7,
            "revenue_growth_yoy": 18.8
        }
    },
    "NVDA": {
        "income_statement": {
            "2024": {"total_revenue": 60922, "cogs": 16621, "gross_profit": 44301, "operating_income": 32972, "net_income": 29760, "diluted_eps": 11.93},
            "2023": {"total_revenue": 26974, "cogs": 11618, "gross_profit": 15356, "operating_income": 4224, "net_income": 4368, "diluted_eps": 1.74}
        },
        "balance_sheet": {
            "2024": {"cash_and_investments": 25984, "total_assets": 65728, "total_debt": 11056, "stockholders_equity": 42978, "current_ratio": 4.17, "debt_to_equity": 0.26}
        },
        "cash_flow": {
            "2024": {"operating_cash_flow": 28090, "capital_expenditures": 1154, "free_cash_flow": 26936, "share_repurchases": 9500, "dividends_paid": 395}
        },
        "ratios": {
            "pe_ratio": 48.2,
            "forward_pe": 32.1,
            "ev_ebitda": 36.8,
            "price_to_sales": 26.5,
            "gross_margin": 72.7,
            "operating_margin": 54.1,
            "net_profit_margin": 48.8,
            "roe": 91.5,
            "roa": 55.4,
            "fcf_yield": 1.6,
            "revenue_growth_yoy": 125.9
        }
    },
    "PLTR": {
        "income_statement": {
            "2023": {"total_revenue": 2225, "cogs": 434, "gross_profit": 1791, "operating_income": 119.9, "net_income": 209.8, "diluted_eps": 0.09},
            "2022": {"total_revenue": 1906, "cogs": 409, "gross_profit": 1497, "operating_income": -161.2, "net_income": -373.7, "diluted_eps": -0.18}
        },
        "balance_sheet": {
            "2023": {"cash_and_equivalents": 3672, "total_assets": 4450, "total_debt": 0, "stockholders_equity": 3410, "current_ratio": 5.5, "debt_to_equity": 0.0}
        },
        "cash_flow": {
            "2023": {"operating_cash_flow": 687, "adjusted_free_cash_flow": 731, "capital_expenditures": 12}
        },
        "ratios": {
            "pe_ratio": 85.0,
            "forward_pe": 62.0,
            "ev_ebitda": 45.0,
            "price_to_sales": 18.2,
            "gross_margin": 80.5,
            "operating_margin": 5.4,
            "net_profit_margin": 9.4,
            "roe": 6.8,
            "roa": 5.1,
            "fcf_yield": 2.1,
            "revenue_growth_yoy": 16.7
        }
    }
}

def get_financial_data(ticker: str, statement_type: str = "all", period: str = "annual", years: int = 3) -> Dict[str, Any]:
    """
    Retrieve structured financial statements and key ratios.
    """
    ticker = ticker.upper().strip()
    logger.info("Fetching financial data: ticker=%s, statement_type=%s, period=%s, years=%d", ticker, statement_type, period, years)
    
    company = FINANCIAL_DATA_STORE.get(ticker)
    if company:
        if statement_type == "all":
            payload = company
        elif statement_type in company:
            payload = {statement_type: company[statement_type]}
        else:
            payload = company.get("ratios", {})

        return {
            "status": "success",
            "ticker": ticker,
            "statement_type": statement_type,
            "period": period,
            "currency": "USD",
            "units": "Millions (except per share data)",
            "source_tier": "Tier 2 (Audited Financial Data API)",
            "financial_data": payload
        }

    # Generic realistic tech/industrial fallback
    return {
        "status": "success",
        "ticker": ticker,
        "statement_type": statement_type,
        "period": period,
        "currency": "USD",
        "units": "Millions",
        "source_tier": "Tier 2 (Financial Data API)",
        "financial_data": {
            "income_statement": {
                "2024": {"total_revenue": 15000, "gross_profit": 9000, "operating_income": 3500, "net_income": 2800},
                "2023": {"total_revenue": 13200, "gross_profit": 7800, "operating_income": 2900, "net_income": 2300}
            },
            "ratios": {
                "pe_ratio": 24.5,
                "gross_margin": 60.0,
                "operating_margin": 23.3,
                "net_profit_margin": 18.7,
                "revenue_growth_yoy": 13.6
            }
        }
    }
