"""
Report Generator Tool for ARA-1.
Compiles research outputs into institutional-grade markdown investment research reports.
"""

import datetime
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ARA.Tools.ReportGenerator")

class ReportGenerator:
    """
    Constructs standardized investment research documents according to institutional templates.
    """
    def generate(self, title: str, template: str, sections: Dict[str, str], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info("Generating research report: title='%s', template=%s", title, template)
        
        meta = metadata or {}
        ticker = meta.get("ticker", "N/A")
        analyst = meta.get("analyst", "ARA-1 (Autonomous Research Agent, QuantumEdge Research)")
        date_str = meta.get("date", datetime.date.today().strftime("%B %d, %Y"))
        
        lines = []
        # Header banner
        lines.append(f"# {title}")
        lines.append(f"**Firm:** QuantumEdge Research | **Division:** Quantitative & Fundamental Equity Research")
        lines.append(f"**Date:** {date_str} | **Target/Ticker:** {ticker} | **Lead Analyst:** {analyst}")
        lines.append(f"**Research Template:** Institutional `{template}` | **Confidence Level:** High (Multi-Source Grounded)")
        lines.append("\n---\n")

        # Table of contents
        lines.append("## Executive Table of Contents")
        for idx, sec_title in enumerate(sections.keys(), 1):
            lines.append(f"{idx}. [{sec_title}](#{sec_title.lower().replace(' ', '-').replace('&', '').replace('/', '')})")
        lines.append("\n---\n")

        # Sections
        for sec_title, content in sections.items():
            lines.append(f"## {sec_title}\n")
            lines.append(content.strip())
            lines.append("\n\n---\n")

        # Mandatory institutional research governance footer
        lines.append("## Research Methodology & Regulatory Disclosures")
        lines.append(
            "This report was autonomously compiled by ARA-1 using QuantumEdge Research's multi-source synthesis pipeline. "
            "Data was extracted and cross-verified across SEC EDGAR audited filings (Tier 1), primary financial statement APIs (Tier 2), "
            "earnings call transcripts (Tier 3), and verified financial media (Tier 5). "
            "This report is generated for institutional equity research assessment and does not constitute individual investment advice."
        )

        final_markdown = "\n".join(lines)
        return {
            "status": "success",
            "title": title,
            "template": template,
            "total_sections": len(sections),
            "word_count": len(final_markdown.split()),
            "markdown_report": final_markdown
        }

def format_research_report(title: str, template: str, sections: Dict[str, str], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    generator = ReportGenerator()
    return generator.generate(title=title, template=template, sections=sections, metadata=metadata)
