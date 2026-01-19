"""
PDF report generator module.

Uses ReportLab to create professional PDF reports from enriched CRM data.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from claude_enrichment import EnrichedReport
from config import OutputConfig

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generates professional PDF reports from enriched CRM data."""

    def __init__(self, config: OutputConfig):
        """Initialize the PDF generator."""
        self.config = config
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=self.styles["Title"],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor("#1a365d"),
            )
        )

        # Section header style
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading1"],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=12,
                textColor=colors.HexColor("#2c5282"),
                borderWidth=1,
                borderColor=colors.HexColor("#e2e8f0"),
                borderPadding=5,
            )
        )

        # Subsection style
        self.styles.add(
            ParagraphStyle(
                name="SubsectionHeader",
                parent=self.styles["Heading2"],
                fontSize=13,
                spaceBefore=15,
                spaceAfter=8,
                textColor=colors.HexColor("#4a5568"),
            )
        )

        # Body text style
        self.styles.add(
            ParagraphStyle(
                name="ReportBody",
                parent=self.styles["Normal"],
                fontSize=10,
                spaceBefore=6,
                spaceAfter=6,
                leading=14,
                textColor=colors.HexColor("#2d3748"),
            )
        )

        # Metric value style
        self.styles.add(
            ParagraphStyle(
                name="MetricValue",
                parent=self.styles["Normal"],
                fontSize=18,
                textColor=colors.HexColor("#2b6cb0"),
                alignment=1,  # Center
            )
        )

        # Metric label style
        self.styles.add(
            ParagraphStyle(
                name="MetricLabel",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#718096"),
                alignment=1,  # Center
            )
        )

        # Footer style
        self.styles.add(
            ParagraphStyle(
                name="Footer",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=colors.HexColor("#a0aec0"),
                alignment=1,
            )
        )

    def generate_report(self, report: EnrichedReport, output_path: Path | None = None) -> Path:
        """Generate the PDF report."""
        if output_path is None:
            output_path = self.config.report_path

        logger.info(f"Generating PDF report: {output_path}")

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # Build the document content
        story = []

        # Title page
        story.extend(self._create_title_page(report))
        story.append(PageBreak())

        # Executive Summary
        story.extend(self._create_section("Executive Summary", report.executive_summary))
        story.append(PageBreak())

        # Pipeline Analysis
        story.extend(self._create_section("Pipeline Analysis", report.pipeline_analysis))

        # Client Insights
        story.extend(self._create_section("Client Insights", report.client_insights))
        story.append(PageBreak())

        # Staffing Overview
        story.extend(self._create_section("Staffing Overview", report.staffing_overview))

        # Margin Analysis
        story.extend(self._create_section("Margin Analysis", report.margin_analysis))
        story.append(PageBreak())

        # Recommendations
        story.extend(self._create_section("Strategic Recommendations", report.recommendations))

        # Data Summary appendix
        story.append(PageBreak())
        story.extend(self._create_data_summary(report.raw_data))

        # Build the PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

        logger.info(f"PDF report generated successfully: {output_path}")
        return output_path

    def _create_title_page(self, report: EnrichedReport) -> list:
        """Create the title page elements."""
        elements = []

        # Add some space at top
        elements.append(Spacer(1, 1.5 * inch))

        # Title
        elements.append(
            Paragraph("Force Multiply", self.styles["ReportTitle"])
        )
        elements.append(
            Paragraph("CRM Intelligence Report", self.styles["SectionHeader"])
        )

        elements.append(Spacer(1, 0.5 * inch))

        # Report date
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(
            Paragraph(f"Generated: {date_str}", self.styles["ReportBody"])
        )

        elements.append(Spacer(1, 1 * inch))

        # Summary metrics table
        raw_data = report.raw_data
        summary = raw_data.get("summary", {})

        metrics_data = [
            [
                self._metric_cell(str(summary.get("total_accounts", 0)), "Accounts"),
                self._metric_cell(str(summary.get("total_contacts", 0)), "Contacts"),
                self._metric_cell(str(summary.get("total_opportunities", 0)), "Opportunities"),
            ],
            [
                self._metric_cell(str(summary.get("total_projects", 0)), "Projects"),
                self._metric_cell(str(summary.get("total_engagements", 0)), "Engagements"),
                self._metric_cell("-", ""),
            ],
        ]

        # Create metrics table
        metrics_table = Table(
            metrics_data,
            colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch],
            rowHeights=[0.9 * inch, 0.9 * inch],
        )
        metrics_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
                ]
            )
        )
        elements.append(metrics_table)

        elements.append(Spacer(1, 1 * inch))

        # AI-powered badge
        elements.append(
            Paragraph(
                "AI-Powered Analysis by Claude",
                self.styles["MetricLabel"],
            )
        )

        return elements

    def _metric_cell(self, value: str, label: str) -> list:
        """Create a metric cell with value and label."""
        return [
            Paragraph(value, self.styles["MetricValue"]),
            Paragraph(label, self.styles["MetricLabel"]),
        ]

    def _create_section(self, title: str, content: str) -> list:
        """Create a report section with title and content."""
        elements = []

        # Section header
        elements.append(Paragraph(title, self.styles["SectionHeader"]))

        # Process content - split into paragraphs
        paragraphs = content.strip().split("\n\n")
        for para in paragraphs:
            # Clean up the paragraph
            para = para.strip()
            if para:
                # Handle markdown-style headers
                if para.startswith("##"):
                    para = para.lstrip("#").strip()
                    elements.append(Paragraph(para, self.styles["SubsectionHeader"]))
                elif para.startswith("#"):
                    para = para.lstrip("#").strip()
                    elements.append(Paragraph(para, self.styles["SubsectionHeader"]))
                elif para.startswith("**") and para.endswith("**"):
                    # Bold text as subsection
                    para = para.strip("*").strip()
                    elements.append(Paragraph(para, self.styles["SubsectionHeader"]))
                elif para.startswith("[Priority:"):
                    # Recommendation format
                    elements.append(Spacer(1, 6))
                    elements.append(Paragraph(f"<b>{para}</b>", self.styles["ReportBody"]))
                elif para.startswith("-") or para.startswith("*"):
                    # Bullet point - handle as single paragraph with preserved formatting
                    lines = para.split("\n")
                    for line in lines:
                        line = line.strip().lstrip("-*").strip()
                        if line:
                            elements.append(
                                Paragraph(f"    - {line}", self.styles["ReportBody"])
                            )
                else:
                    # Regular paragraph
                    # Escape any special characters for ReportLab
                    para = para.replace("&", "&amp;")
                    para = para.replace("<", "&lt;")
                    para = para.replace(">", "&gt;")
                    elements.append(Paragraph(para, self.styles["ReportBody"]))

        elements.append(Spacer(1, 12))
        return elements

    def _create_data_summary(self, data: dict[str, Any]) -> list:
        """Create a data summary appendix."""
        elements = []

        elements.append(Paragraph("Appendix: Data Summary", self.styles["SectionHeader"]))

        # Accounts summary
        accounts = data.get("accounts", [])
        if accounts:
            elements.append(Paragraph("Accounts", self.styles["SubsectionHeader"]))

            # Create accounts table
            table_data = [["Name", "Type", "Industry", "NDA", "MSA"]]
            for acc in accounts[:15]:  # Limit to 15 rows
                table_data.append(
                    [
                        acc.get("name", "")[:30],
                        acc.get("account_type", "-") or "-",
                        acc.get("industry", "-") or "-",
                        "Yes" if acc.get("nda_signed") else "No",
                        "Yes" if acc.get("msa_signed") else "No",
                    ]
                )

            table = Table(table_data, colWidths=[2 * inch, 1.2 * inch, 1.5 * inch, 0.6 * inch, 0.6 * inch])
            table.setStyle(self._get_table_style())
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Opportunities summary
        opportunities = data.get("opportunities", [])
        if opportunities:
            elements.append(Paragraph("Opportunities", self.styles["SubsectionHeader"]))

            table_data = [["Name", "Account", "Stage", "Amount", "Close Date"]]
            for opp in opportunities[:15]:
                amount = opp.get("amount")
                amount_str = f"${amount:,.0f}" if amount else "-"
                table_data.append(
                    [
                        opp.get("name", "")[:25],
                        (opp.get("account_name") or "-")[:20],
                        opp.get("stage", "-") or "-",
                        amount_str,
                        opp.get("close_date", "-") or "-",
                    ]
                )

            table = Table(table_data, colWidths=[1.8 * inch, 1.4 * inch, 1.2 * inch, 0.9 * inch, 0.9 * inch])
            table.setStyle(self._get_table_style())
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Engagements summary
        engagements = data.get("engagements", [])
        if engagements:
            elements.append(Paragraph("Contractor Engagements", self.styles["SubsectionHeader"]))

            table_data = [["Contractor", "Client", "Role", "Status", "Margin"]]
            for eng in engagements[:15]:
                margin = eng.get("margin_percent")
                margin_str = f"{margin:.1f}%" if margin is not None else "-"
                table_data.append(
                    [
                        (eng.get("contractor_name") or "-")[:20],
                        (eng.get("client_account_name") or "-")[:18],
                        (eng.get("engagement_role") or "-")[:15],
                        (eng.get("engagement_status") or "-")[:12],
                        margin_str,
                    ]
                )

            table = Table(table_data, colWidths=[1.5 * inch, 1.4 * inch, 1.2 * inch, 1 * inch, 0.8 * inch])
            table.setStyle(self._get_table_style())
            elements.append(table)

        return elements

    def _get_table_style(self) -> TableStyle:
        """Get standard table style."""
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7fafc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f7fafc"), colors.white]),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ]
        )

    def _add_footer(self, canvas, doc) -> None:
        """Add footer to each page."""
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#a0aec0"))

        # Page number
        page_num = canvas.getPageNumber()
        text = f"Force Multiply CRM Report - Page {page_num}"
        canvas.drawCentredString(letter[0] / 2, 0.5 * inch, text)

        canvas.restoreState()
