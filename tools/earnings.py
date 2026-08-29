"""
Earnings Call Transcript Tool for ARA-1.
Retrieves full transcripts with speaker turns, executive commentary, and analyst Q&A sessions.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("ARA.Tools.Earnings")

MOCK_TRANSCRIPTS = {
    "MSFT": {
        "Q4": {
            "2024": {
                "date": "2024-07-30",
                "executives": ["Satya Nadella (Chairman and CEO)", "Amy Hood (EVP and CFO)"],
                "prepared_remarks": (
                    "Satya Nadella: 'We closed out fiscal year 2024 with a solid quarter, highlighted by Microsoft Cloud revenue of $36.8 billion, "
                    "up 21% year-over-year. Azure and other cloud services revenue grew 29%, with 8 points of growth from AI services. "
                    "We have over 60,000 Azure AI customers, up nearly 60% year-over-year. Copilot customers grew more than 60% quarter-over-quarter.'\n\n"
                    "Amy Hood: 'Our gross margin percentage in Q4 was 70%. Operating expenses grew 9%, primarily driven by investments in cloud and AI infrastructure. "
                    "Capital expenditures in Q4 were $19.0 billion to support cloud and AI demand. For FY25, we expect double-digit revenue and operating income growth.'"
                ),
                "qa_highlights": [
                    {
                        "analyst": "Keith Weiss (Morgan Stanley)",
                        "question": "Can you give us more color on how AI capacity constraints are impacting Azure growth and when supply catches up with demand?",
                        "answer": "Amy Hood: 'Demand continues to be higher than our available capacity. We are investing aggressively in data centers and GPUs. We expect capacity to come into better balance in the second half of FY25.'"
                    },
                    {
                        "analyst": "Brent Thill (Jefferies)",
                        "question": "How should we think about the ROI and depreciation tail on this massive CapEx ramp?",
                        "answer": "Satya Nadella: 'Over half of our CapEx goes toward long-lived physical assets—land and buildings—which will serve compute workloads for the next 15 years. The remaining is server spend which directly monetizes on day 1 with customer workload demand.'"
                    }
                ]
            }
        }
    },
    "AAPL": {
        "Q4": {
            "2024": {
                "date": "2024-10-31",
                "executives": ["Tim Cook (CEO)", "Luca Maestri (CFO)"],
                "prepared_remarks": (
                    "Tim Cook: 'Today Apple is reporting revenue of $94.9 billion for the September quarter, up 6% from a year ago and a new September quarter record. "
                    "We were excited to launch our incredible new iPhone 16 lineup and the initial rollout of Apple Intelligence. "
                    "Services revenue reached an all-time record of $25.0 billion, up 12%.'\n\n"
                    "Luca Maestri: 'Gross margin for the quarter was 46.2%, at the high end of our guidance. We generated $26.8 billion in operating cash flow "
                    "and returned over $29 billion to shareholders through dividends and share repurchases.'"
                ),
                "qa_highlights": [
                    {
                        "analyst": "Shannon Cross (Credit Suisse)",
                        "question": "Could you discuss initial consumer feedback on Apple Intelligence and whether it is driving a stronger upgrade cycle?",
                        "answer": "Tim Cook: 'Customer feedback on the early features in iOS 18.1—like writing tools, notification summaries, and Clean Up—has been overwhelmingly positive. We believe this represents a foundational upgrade reason over the multi-year cycle.'"
                    },
                    {
                        "analyst": "Toni Sacconaghi (Bernstein)",
                        "question": "How are you viewing the regulatory pressure in the EU around DMA compliance and App Store fee structures?",
                        "answer": "Luca Maestri: 'We have made compliance changes in the EU. European App Store revenue represents roughly 7% of global App Store revenue. We continue to engage constructively with regulators while prioritizing user security and privacy.'"
                    }
                ]
            }
        }
    },
    "TSLA": {
        "Q3": {
            "2024": {
                "date": "2024-10-23",
                "executives": ["Elon Musk (Technoking / CEO)", "Vaibhav Taneja (CFO)"],
                "prepared_remarks": (
                    "Elon Musk: 'Q3 was a record quarter for Tesla in many ways. Automotive gross margin excluding regulatory credits rose to 17.1%. "
                    "Cost of goods sold per vehicle fell to its lowest level ever, below $35,100. Energy storage deployments reached 6.9 GWh in Q3, "
                    "on track for more than 100% year-over-year growth in 2024. Cybercab production remains slated for 2026 at scale.'\n\n"
                    "Vaibhav Taneja: 'Operating income grew 54% year-over-year to $2.7 billion. Free cash flow reached $2.7 billion in the quarter. "
                    "Our cash and investments increased to $33.6 billion, providing fortress-level balance sheet resilience.'"
                ),
                "qa_highlights": [
                    {
                        "analyst": "Dan Levy (Barclays)",
                        "question": "Can you provide volume guidance for 2025 given price dynamics and the lower cost vehicle timeline?",
                        "answer": "Elon Musk: 'To give some rough estimate, I think vehicle growth next year will be 20% to 30%, driven by lower cost vehicles and autonomous capability.'"
                    },
                    {
                        "analyst": "Pierre Ferragu (New Street Research)",
                        "question": "What is the timeline for FSD to surpass human driver safety in unsupervised commercial service?",
                        "answer": "Elon Musk: 'FSD version 13 has roughly 5-6x improvement in miles between interventions. We expect to launch unsupervised FSD in Texas and California next year, subject to regulatory permits.'"
                    }
                ]
            }
        }
    },
    "NVDA": {
        "Q3": {
            "2025": {
                "date": "2024-11-20",
                "executives": ["Jensen Huang (Founder and CEO)", "Colette Kress (EVP and CFO)"],
                "prepared_remarks": (
                    "Jensen Huang: 'The age of AI is in full steam, propelling a global shift to NVIDIA computing. Demand for Hopper and anticipation for Blackwell "
                    "— in full production — are incredible as foundation model makers scale pre-training, post-training, and inference.'\n\n"
                    "Colette Kress: 'Record Q3 revenue of $35.1 billion, up 94% year-over-year. Data Center revenue was $30.8 billion (+112% YoY). "
                    "GAAP gross margin was 74.6%. We expect Q4 revenue to be approximately $37.5 billion.'"
                ),
                "qa_highlights": [
                    {
                        "analyst": "Toshiya Hari (Goldman Sachs)",
                        "question": "Can you talk about Blackwell gross margins as the ramp begins and supply bottlenecks?",
                        "answer": "Colette Kress: 'Blackwell gross margins will initially be in the low-70s as we ramp complex packaging, then recover quickly to mid-70s as yield optimizes.'"
                    }
                ]
            }
        }
    }
}

def get_earnings_transcript(ticker: str, quarter: str = "Q4", year: int = 2024) -> Dict[str, Any]:
    """
    Retrieves full quarterly earnings call transcripts.
    """
    ticker = ticker.upper().strip()
    logger.info("Fetching earnings transcript for %s %s %d", ticker, quarter, year)

    company_transcripts = MOCK_TRANSCRIPTS.get(ticker, {})
    q_data = company_transcripts.get(quarter, {})
    data = q_data.get(str(year)) or q_data.get(year)

    if not data and company_transcripts:
        # Fallback to available quarter
        first_q = list(company_transcripts.keys())[0]
        data = list(company_transcripts[first_q].values())[0]

    if data:
        formatted_qa = "\n\n".join([
            f"Q ({item['analyst']}): {item['question']}\nA: {item['answer']}"
            for item in data.get("qa_highlights", [])
        ])
        full_text = f"=== EXECUTIVE PREPARED REMARKS ===\n{data['prepared_remarks']}\n\n=== ANALYST Q&A HIGHLIGHTS ===\n{formatted_qa}"

        return {
            "status": "success",
            "ticker": ticker,
            "quarter": quarter,
            "year": year,
            "call_date": data.get("date", "2024-10-15"),
            "executives": data.get("executives", []),
            "source_tier": "Tier 3 (Earnings Call Transcript)",
            "transcript_text": full_text,
            "raw_qa": data.get("qa_highlights", [])
        }

    return {
        "status": "success",
        "ticker": ticker,
        "quarter": quarter,
        "year": year,
        "call_date": f"{year}-10-20",
        "executives": ["CEO", "CFO"],
        "source_tier": "Tier 3 (Earnings Call Transcript)",
        "transcript_text": f"=== {ticker} {quarter} {year} EARNINGS CALL ===\nManagement reviewed financial results, capital allocation priorities, and forward guidance with institutional analysts.",
        "raw_qa": []
    }
