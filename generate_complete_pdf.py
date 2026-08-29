"""
Professional PDF Generator for Project 1A: Autonomous Financial Research Agent (ARA-1).
Compiles the complete system blueprint, architecture specs, 7-error forensic audit,
evaluation reports, 8 challenge reports, and trace gallery into a single institutional PDF.
"""

import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on cover page

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D"))
        
        # Running header
        self.drawString(54, 750, "QUANTUMEDGE RESEARCH | ARA-1 AUTONOMOUS FINANCIAL RESEARCH AGENT")
        self.setFont("Helvetica", 8)
        self.drawRightString(558, 750, "PROJECT 1A FINAL SUBMISSION")
        
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(54, 744, 558, 744)

        # Running footer
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(54, 32, "Confidential - Prepared for Zetheta Algorithms / QuantumEdge Research Assessment")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_text)
        self.restoreState()


def clean_markdown_text(text: str) -> str:
    """Cleans markdown syntax for ReportLab Paragraph compatibility."""
    # Escape XML entities
    text = text.replace("&", "&amp;")
    # Bold **text** -> <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italic *text* -> <i>text</i>
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    # Inline code `code` -> <font name="Courier" color="#1A365D">code</font>
    text = re.sub(r'`(.*?)`', r'<font name="Courier" color="#2B6CB0"><b>\1</b></font>', text)
    return text


def build_pdf(filename="Project1A-AshwinKumar-AutonomousFinancialResearchAgent-CompleteReport.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    c_navy = colors.HexColor("#1A365D")
    c_blue = colors.HexColor("#2B6CB0")
    c_charcoal = colors.HexColor("#2D3748")

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=c_navy,
        alignment=1, # Center
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=c_blue,
        alignment=1,
        spaceAfter=25
    )

    meta_style = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=c_charcoal,
        alignment=1
    )

    h1_style = ParagraphStyle(
        "CustomH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=c_navy,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "CustomH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_blue,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        "CustomH3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=c_charcoal,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_charcoal,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        "CustomCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1A202C"),
        backColor=colors.HexColor("#F7FAFC"),
        borderColor=colors.HexColor("#E2E8F0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=4, color=c_navy, spaceAfter=25))
    story.append(Paragraph("QUANTUMEDGE RESEARCH", ParagraphStyle("HeaderTop", fontName="Helvetica-Bold", fontSize=14, textColor=c_blue, alignment=1, spaceAfter=15)))
    story.append(Paragraph("PROJECT 1A: AUTONOMOUS FINANCIAL RESEARCH AGENT (ARA-1)", title_style))
    story.append(Paragraph("A Multi-Source Autonomous Intelligence Platform with Three-Layer Memory Hierarchy, 6-Tier Conflict Resolution, Fallback Resilience, and 20+ Quality Metric Benchmarking", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=30))
    
    cover_table_data = [
        [Paragraph("<b>Candidate Name:</b>", body_style), Paragraph("Ashwin Kumar", body_style)],
        [Paragraph("<b>Role / Specialization:</b>", body_style), Paragraph("Agentic AI Engineer / Quantitative System Architect", body_style)],
        [Paragraph("<b>Organization / Context:</b>", body_style), Paragraph("QuantumEdge Research / Zetheta Algorithms", body_style)],
        [Paragraph("<b>Project Code & Category:</b>", body_style), Paragraph("Project 1A | AI Application Technology (Agentic AI)", body_style)],
        [Paragraph("<b>Repository:</b>", body_style), Paragraph("https://github.com/AshwinKumar710/Project1A-AshwinKumar-AutonomousFinancialResearchAgent", body_style)],
        [Paragraph("<b>Quality Score:</b>", body_style), Paragraph("<b>95.5% / 100</b> (21/22 Institutional Metrics Passed)", body_style)],
        [Paragraph("<b>Hallucination Rate:</b>", body_style), Paragraph("<b>0.0%</b> (Zero ungrounded claims)", body_style)],
        [Paragraph("<b>Test Verification:</b>", body_style), Paragraph("<b>24/24 Unit & Integration Tests Passing (100%)</b>", body_style)],
        [Paragraph("<b>Submission Date:</b>", body_style), Paragraph("August 29, 2026", body_style)],
    ]
    t_cover = Table(cover_table_data, colWidths=[160, 344])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_cover)
    story.append(Spacer(1, 40))
    story.append(Paragraph("<i>This consolidated technical report compiles the complete system architecture blueprint, forensic audit of all 7 deliberate errors, empirical evaluation benchmarks, full outputs of all 8 progressive research challenges, and annotated agent execution traces.</i>", ParagraphStyle("CoverFooter", fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#718096"), alignment=1)))
    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("TABLE OF CONTENTS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceAfter=15))
    
    toc_items = [
        ("Section 1", "System Executive Overview & Capabilities", "Page 3"),
        ("Section 2", "12+ Page Final Architecture Specification", "Page 5"),
        ("Section 3", "Forensic Audit of 7 Deliberate Errors (ERROR_LOG.md)", "Page 11"),
        ("Section 4", "Final 22-Metric Quality Evaluation Report", "Page 14"),
        ("Section 5", "Progressive Challenge Outputs (Challenges 1 to 8)", "Page 17"),
        ("  - 5.1", "Challenge 1: Microsoft (MSFT) Fundamental Profile", "Page 17"),
        ("  - 5.2", "Challenge 2: Apple (AAPL) Earnings & Services Review", "Page 19"),
        ("  - 5.3", "Challenge 3: Tesla (TSLA) Risk Assessment & FSD Safety", "Page 21"),
        ("  - 5.4", "Challenge 4: Cloud Infrastructure AWS vs Azure vs GCP", "Page 23"),
        ("  - 5.5", "Challenge 5: Palantir (PLTR) Contradiction Resolution", "Page 25"),
        ("  - 5.6", "Challenge 6: US Banking Sector Disambiguation", "Page 27"),
        ("  - 5.7", "Challenge 7: Tech Sector Memory & Theme Synthesis", "Page 29"),
        ("  - 5.8", "Challenge 8: NVIDIA (NVDA) under 50% Tool Outage", "Page 31"),
        ("Section 6", "Curated Agent Reasoning Trace Gallery", "Page 33"),
        ("Section 7", "Stress Test Report & Token Usage Cost Analysis", "Page 36"),
        ("Section 8", "Prompt, Latency & Optimization Log", "Page 38"),
    ]
    toc_table = Table([[Paragraph(f"<b>{c1}</b>", body_style), Paragraph(c2, body_style), Paragraph(f"<b>{c3}</b>", body_style)] for c1, c2, c3 in toc_items], colWidths=[80, 360, 64])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#EDF2F7")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: README / EXECUTIVE OVERVIEW
    # =========================================================================
    def parse_and_append_markdown_file(filepath, main_title=None):
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if main_title:
            story.append(Paragraph(main_title, h1_style))
            story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceAfter=12))

        in_code_block = False
        code_lines = []
        in_table = False
        table_rows = []

        lines = content.split("\n")
        for line in lines:
            stripped = line.strip()
            
            # Code block toggle
            if stripped.startswith("```"):
                if in_code_block:
                    # End code block
                    code_text = "<br/>".join([clean_markdown_text(cl) for cl in code_lines])
                    story.append(Paragraph(code_text, code_style))
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # Tables
            if stripped.startswith("|") and stripped.endswith("|"):
                # Table row
                if "---" in stripped:
                    continue  # separator row
                cols = [clean_markdown_text(c.strip()) for c in stripped.split("|")[1:-1]]
                table_rows.append([Paragraph(c, body_style) for c in cols])
                in_table = True
                continue
            else:
                if in_table and table_rows:
                    col_count = len(table_rows[0])
                    avail_width = 504
                    w = avail_width / col_count
                    t = Table(table_rows, colWidths=[w]*col_count)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
                        ('PADDING', (0,0), (-1,-1), 4),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 6))
                    table_rows = []
                    in_table = False

            if not stripped:
                continue

            if stripped.startswith("# "):
                if not main_title:
                    story.append(Paragraph(clean_markdown_text(stripped[2:]), h1_style))
                    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceAfter=10))
            elif stripped.startswith("## "):
                story.append(Paragraph(clean_markdown_text(stripped[3:]), h2_style))
            elif stripped.startswith("### "):
                story.append(Paragraph(clean_markdown_text(stripped[4:]), h3_style))
            elif stripped.startswith("- ") or stripped.startswith("* "):
                story.append(Paragraph(f"&bull; {clean_markdown_text(stripped[2:])}", body_style))
            elif re.match(r'^\d+\.\s', stripped):
                story.append(Paragraph(clean_markdown_text(stripped), body_style))
            elif stripped.startswith(">"):
                story.append(Paragraph(f"<i>{clean_markdown_text(stripped[1:].strip())}</i>", ParagraphStyle("Quote", parent=body_style, backColor=colors.HexColor("#F7FAFC"), borderPadding=4)))
            else:
                story.append(Paragraph(clean_markdown_text(stripped), body_style))

        if in_table and table_rows:
            col_count = len(table_rows[0])
            avail_width = 504
            w = avail_width / col_count
            t = Table(table_rows, colWidths=[w]*col_count)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))

    # Append All Sections
    print("Compiling Section 1: README...")
    parse_and_append_markdown_file("README.md", "SECTION 1: SYSTEM OVERVIEW & ARCHITECTURE")
    story.append(PageBreak())

    print("Compiling Section 2: Architecture Specification...")
    parse_and_append_markdown_file("docs/architecture_specification_final.md", "SECTION 2: FINAL ARCHITECTURE SPECIFICATION")
    story.append(PageBreak())

    print("Compiling Section 3: Error Log...")
    parse_and_append_markdown_file("ERROR_LOG.md", "SECTION 3: FORENSIC AUDIT OF 7 DELIBERATE ERRORS")
    story.append(PageBreak())

    print("Compiling Section 4: Evaluation Report...")
    parse_and_append_markdown_file("docs/evaluation_report_final.md", "SECTION 4: QUALITY EVALUATION & BENCHMARKING REPORT")
    story.append(PageBreak())

    print("Compiling Section 5: Challenge Reports...")
    story.append(Paragraph("SECTION 5: PROGRESSIVE RESEARCH CHALLENGE REPORTS (C1 - C8)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceAfter=15))
    
    for i in range(1, 9):
        ch_path = f"results/challenge_{i}.md"
        if os.path.exists(ch_path):
            parse_and_append_markdown_file(ch_path)
            story.append(Spacer(1, 15))

    story.append(PageBreak())

    print("Compiling Section 6: Trace Gallery...")
    parse_and_append_markdown_file("docs/trace_gallery.md", "SECTION 6: ANNOTATED AGENT REASONING TRACE GALLERY")
    story.append(PageBreak())

    print("Compiling Section 7: Stress Test & Token Usage...")
    parse_and_append_markdown_file("results/stress_test_report.md", "SECTION 7: STRESS TEST & SYSTEM RESILIENCE REPORT")
    story.append(Spacer(1, 15))
    parse_and_append_markdown_file("results/token_usage_analysis.md", "TOKEN USAGE & COST EFFICIENCY ANALYSIS")
    story.append(PageBreak())

    print("Compiling Section 8: Optimization Log...")
    parse_and_append_markdown_file("docs/optimization_log.md", "SECTION 8: PROMPT, LATENCY & PERFORMANCE OPTIMIZATION LOG")

    print("Building final PDF document...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")

if __name__ == "__main__":
    build_pdf()
