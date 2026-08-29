"""
OpenAI Function-Calling Specification Schemas for all 12 ARA-1 Financial Tools.
"""

ALL_TOOL_SCHEMAS = {
    "sec_filing_search": {
        "name": "sec_filing_search",
        "description": "Search and retrieve official SEC EDGAR regulatory filings (10-K annual, 10-Q quarterly, 8-K current event, DEF 14A proxy) for a publicly traded company. Returns full audited financial disclosures, MD&A, and risk factors.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g. AAPL, MSFT, TSLA, NVDA)"
                },
                "filing_type": {
                    "type": "string",
                    "enum": ["10-K", "10-Q", "8-K", "DEF 14A"],
                    "description": "Type of regulatory filing to retrieve"
                },
                "year": {
                    "type": "integer",
                    "description": "Filing fiscal year (defaults to most recent)"
                },
                "section": {
                    "type": "string",
                    "enum": ["Item 1 (Business)", "Item 1A (Risk Factors)", "Item 7 (MD&A)", "Item 8 (Financial Statements)", "Full"],
                    "description": "Specific filing section to extract (default 'Full')"
                }
            },
            "required": ["ticker", "filing_type"]
        }
    },
    "financial_data_api": {
        "name": "financial_data_api",
        "description": "Retrieves structured audited financial statements and ratios (Income Statement, Balance Sheet, Cash Flow Statement, Key Ratios) across annual or quarterly periods.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "statement_type": {
                    "type": "string",
                    "enum": ["income_statement", "balance_sheet", "cash_flow", "ratios", "all"],
                    "description": "Type of financial statement or metric summary to retrieve"
                },
                "period": {
                    "type": "string",
                    "enum": ["annual", "quarterly"],
                    "description": "Reporting period frequency (default: 'annual')"
                },
                "years": {
                    "type": "integer",
                    "description": "Number of past years/periods of historical data (default: 3)"
                }
            },
            "required": ["ticker", "statement_type"]
        }
    },
    "web_search": {
        "name": "web_search",
        "description": "Executes broad web search across reputable financial media, analyst commentaries, and industry publications to capture recent events and emerging market developments.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string focused on financial/corporate topic"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of search results to return (default: 5, max: 10)"
                },
                "date_range": {
                    "type": "string",
                    "description": "Optional time filter (e.g. 'past_month', 'past_year')"
                }
            },
            "required": ["query"]
        }
    },
    "earnings_transcript": {
        "name": "earnings_transcript",
        "description": "Retrieves quarterly earnings call transcripts including management prepared remarks, operational highlights, guidance, and analyst Q&A sessions.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Company stock ticker symbol"
                },
                "quarter": {
                    "type": "string",
                    "enum": ["Q1", "Q2", "Q3", "Q4"],
                    "description": "Fiscal quarter"
                },
                "year": {
                    "type": "integer",
                    "description": "Fiscal year"
                }
            },
            "required": ["ticker", "quarter", "year"]
        }
    },
    "news_sentiment": {
        "name": "news_sentiment",
        "description": "Aggregates recent news articles for a company or sector and computes quantitative sentiment polarity, subjectivity, and tone alignment across sources.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Company ticker or topic name to analyze"
                },
                "num_articles": {
                    "type": "integer",
                    "description": "Number of articles to analyze (default: 5)"
                },
                "lookback_days": {
                    "type": "integer",
                    "description": "Time horizon in days (default: 30)"
                }
            },
            "required": ["query"]
        }
    },
    "vector_db_search": {
        "name": "vector_db_search",
        "description": "Searches the agent's persistent long-term semantic vector memory for previously stored research findings, filings, and analyst synthesis chunks.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Semantic search query to retrieve historical context"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top matching chunks to retrieve (default: 5)"
                },
                "ticker_filter": {
                    "type": "string",
                    "description": "Optional filter by company ticker"
                }
            },
            "required": ["query"]
        }
    },
    "vector_db_store": {
        "name": "vector_db_store",
        "description": "Stores newly synthesized research insights, facts, or document excerpts into long-term vector memory for cross-session cumulative learning.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Document text or analytical insight to embed and store"
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string"},
                        "source_type": {"type": "string"},
                        "date": {"type": "string"},
                        "confidence": {"type": "number"},
                        "verified": {"type": "boolean"}
                    },
                    "required": ["ticker", "source_type"]
                }
            },
            "required": ["content", "metadata"]
        }
    },
    "company_profile": {
        "name": "company_profile",
        "description": "Retrieves comprehensive core company metadata: corporate identity, sector, industry, market cap, executive leadership, business description, and key headquarters info.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Company stock ticker symbol"
                }
            },
            "required": ["ticker"]
        }
    },
    "peer_comparison": {
        "name": "peer_comparison",
        "description": "Identifies sector peers and generates a comparative financial matrix across valuation multiples, growth, profit margins, and balance sheet strength.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Primary company ticker symbol"
                },
                "num_peers": {
                    "type": "integer",
                    "description": "Number of peers to compare (default: 3)"
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of metrics (e.g. ['pe_ratio', 'ev_ebitda', 'revenue_growth', 'operating_margin', 'roe'])"
                }
            },
            "required": ["ticker"]
        }
    },
    "calculation_engine": {
        "name": "calculation_engine",
        "description": "Performs rigorous financial modeling calculations including Discounted Cash Flow (DCF), Weighted Average Cost of Capital (WACC), DuPont 3-stage / 5-stage decomposition, CAGR, and debt coverage ratios.",
        "parameters": {
            "type": "object",
            "properties": {
                "calculation_type": {
                    "type": "string",
                    "enum": ["dcf", "wacc", "dupont", "cagr", "ratios", "margin_trend"],
                    "description": "Type of financial formula or model to execute"
                },
                "inputs": {
                    "type": "object",
                    "description": "Key-value numerical inputs required for the model"
                }
            },
            "required": ["calculation_type", "inputs"]
        }
    },
    "fact_checker": {
        "name": "fact_checker",
        "description": "Cross-references a specific numerical or qualitative financial claim against authoritative primary sources, returning confidence scores, evidence snippets, and discrepancy flags.",
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The specific claim, statistic, or data point to verify"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of source documents or text snippets to check against"
                },
                "ticker": {
                    "type": "string",
                    "description": "Target company ticker"
                }
            },
            "required": ["claim"]
        }
    },
    "report_generator": {
        "name": "report_generator",
        "description": "Compiles and formats structured findings into an institutional-grade investment research report with standardized sections, executive summary, tables, and citation footnotes.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Research report title"
                },
                "template": {
                    "type": "string",
                    "enum": ["company_profile", "earnings_review", "risk_assessment", "comparative_analysis", "full_initiation", "sector_theme"],
                    "description": "Institutional template structure to apply"
                },
                "sections": {
                    "type": "object",
                    "description": "Dictionary of section names mapped to markdown content"
                },
                "metadata": {
                    "type": "object",
                    "description": "Author, date, ticker, target price, methodology notes"
                }
            },
            "required": ["title", "template", "sections"]
        }
    }
}

TOOL_REGISTRY_METADATA = {
    "version": "1.0.0",
    "total_tools": len(ALL_TOOL_SCHEMAS),
    "category_distribution": {
        "regulatory_and_primary": ["sec_filing_search", "earnings_transcript"],
        "quantitative_and_financial": ["financial_data_api", "calculation_engine", "peer_comparison"],
        "market_intelligence": ["web_search", "news_sentiment", "company_profile"],
        "memory_and_knowledge": ["vector_db_search", "vector_db_store"],
        "governance_and_reporting": ["fact_checker", "report_generator"]
    }
}
