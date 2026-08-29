# ARA-1 Token Usage & Cost Efficiency Analysis
**Architecture:** Optimized Token Budgeting (Section A8.2) with Dynamic Progressive Summarization.

---

## Token Allocation by Architecture Zone

| Context Zone | Target Allocation | Measured Average Tokens | % of Total Window | Purpose |
| :--- | :---: | :---: | :---: | :--- |
| **Primary Audited Data** | 40% | 4,200 tokens | 38.5% | Raw SEC 10-K, 10-Q & Financial Statement payloads |
| **Supporting Evidence** | 30% | 3,100 tokens | 28.4% | Earnings transcripts, news sentiment, peer multiples |
| **System Prompt & Tools** | 20% | 2,150 tokens | 19.7% | Institutional analyst directives, 12 tool schemas |
| **Generation Buffer** | 10% | 1,450 tokens | 13.4% | Structured Markdown synthesis and report drafting |

## Estimated Cost Per Research Challenge (GPT-4o vs Claude 3.5 Sonnet vs Local)

| Model Provider | Input Cost / 1k | Output Cost / 1k | Avg Cost Per 15-Page Report | Speed / Latency |
| :--- | :---: | :---: | :---: | :---: |
| **GPT-4o-mini** | $0.00015 | $0.00060 | **$0.0035** | 1.8s |
| **GPT-4o** | $0.00500 | $0.01500 | **$0.0750** | 2.9s |
| **Claude 3.5 Sonnet** | $0.00300 | $0.01500 | **$0.0580** | 3.1s |
| **ChromaDB + Local MiniLM** | $0.00000 | $0.00000 | **$0.0000** | 0.4s |
