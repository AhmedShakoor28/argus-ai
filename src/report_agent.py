"""
Report Agent
------------
Takes the final_report dict produced by main.py's run_pipeline() and
renders it as a clean, shareable PDF incident report.

Usage (standalone):
    python src/report_agent.py --input report.json --output report.pdf

Usage (from main.py):
    from report_agent import ReportAgent
    ReportAgent().generate(final_report, "reports/incident_2026_08_25.pdf")
"""

import argparse
import json
import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


STATUS_COLORS = {
    "confirmed": colors.HexColor("#C0392B"),          # red
    "suspect_but_plausible": colors.HexColor("#D68910"),  # amber
    "unconfirmed": colors.HexColor("#7F8C8D"),         # grey
}


class ReportAgent:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name="ArgusTitle", parent=self.styles["Title"], fontSize=22, spaceAfter=4
        ))
        self.styles.add(ParagraphStyle(
            name="ArgusSubtitle", parent=self.styles["Normal"], fontSize=10,
            textColor=colors.HexColor("#555555"), spaceAfter=18
        ))
        self.styles.add(ParagraphStyle(
            name="SectionHeading", parent=self.styles["Heading2"],
            spaceBefore=16, spaceAfter=8, textColor=colors.HexColor("#1A1A1A")
        ))
        self.styles.add(ParagraphStyle(
            name="Body", parent=self.styles["Normal"], fontSize=10, leading=14
        ))
        self.styles.add(ParagraphStyle(
            name="Flag", parent=self.styles["Normal"], fontSize=9, leading=13,
            textColor=colors.HexColor("#B9770E"), leftIndent=10
        ))

    def _status_badge(self, status):
        color = STATUS_COLORS.get(status, colors.black)
        label = status.replace("_", " ").upper()
        return Paragraph(
            f'<font color="{color.hexval()}"><b>{label}</b></font>',
            self.styles["Body"]
        )

    def generate(self, final_report, output_path):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        doc = SimpleDocTemplate(
            output_path, pagesize=letter,
            topMargin=0.75 * inch, bottomMargin=0.75 * inch
        )
        story = []

        # --- Header ---
        story.append(Paragraph("Argus-AI Incident Report", self.styles["ArgusTitle"]))
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        story.append(Paragraph(
            f"Generated {generated_at} &middot; City: {final_report.get('city', 'N/A')} "
            f"&middot; Source image: {os.path.basename(str(final_report.get('image', 'N/A')))}",
            self.styles["ArgusSubtitle"]
        ))

        status = final_report.get("status", "unknown")
        triggered = final_report.get("triggered_types", [])

        if status == "no_disaster_detected" or not triggered:
            story.append(Paragraph(
                "No disaster conditions detected above threshold. "
                "No verification or response recommendation was generated.",
                self.styles["Body"]
            ))
            doc.build(story)
            return output_path

        # --- Summary table ---
        summary_data = [["Disaster Type", "Status", "Verification Plausible"]]
        for dtype, result in final_report.get("results", {}).items():
            plausible = result.get("verification", {}).get("plausible", True)
            summary_data.append([
                dtype.capitalize(),
                result.get("result_status", "unknown").replace("_", " ").upper(),
                "Yes" if plausible else "No"
            ])

        table = Table(summary_data, colWidths=[1.8 * inch, 2.2 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 14))

        # --- Per-disaster detail sections ---
        for dtype, result in final_report.get("results", {}).items():
            story.append(Paragraph(f"{dtype.capitalize()} Detection", self.styles["SectionHeading"]))
            story.append(self._status_badge(result.get("result_status", "unknown")))
            story.append(Spacer(1, 6))

            for flag in result.get("caution_flags", []):
                story.append(Paragraph(f"&#9888; {flag}", self.styles["Flag"]))
            if result.get("caution_flags"):
                story.append(Spacer(1, 8))

            verification = result.get("verification", {})
            weather = verification.get("weather", {})
            if weather and "error" not in weather:
                story.append(Paragraph(
                    f"<b>Weather:</b> {weather.get('condition', 'N/A')} "
                    f"({weather.get('description', '')}), "
                    f"{weather.get('temp_c', 'N/A')}&deg;C, "
                    f"{weather.get('humidity', 'N/A')}% humidity, "
                    f"{weather.get('rain_last_hour_mm', 0)}mm rain (last hr)",
                    self.styles["Body"]
                ))
            reasons = verification.get("reasons", [])
            if reasons:
                story.append(Paragraph(
                    "<b>Verification notes:</b> " + "; ".join(reasons),
                    self.styles["Body"]
                ))
            story.append(Spacer(1, 8))

            recommendation = result.get("response", {}).get("recommendation", "")
            if recommendation:
                story.append(Paragraph("<b>Recommended Response:</b>", self.styles["Body"]))
                # Reportlab Paragraph can't render markdown headers/lists well —
                # keep line breaks, strip markdown bold/hash markers for clean PDF text.
                clean = (
                    recommendation.replace("### ", "").replace("## ", "")
                    .replace("**", "")
                )
                for line in clean.split("\n"):
                    line = line.strip()
                    if line:
                        story.append(Paragraph(line, self.styles["Body"]))
                story.append(Spacer(1, 6))

            sources = result.get("response", {}).get("sources", [])
            if sources:
                unique_sources = sorted(set(os.path.basename(s) for s in sources))
                story.append(Paragraph(
                    f"<i>Sources: {', '.join(unique_sources)}</i>",
                    self.styles["ArgusSubtitle"]
                ))

            story.append(Spacer(1, 10))

        doc.build(story)
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate a PDF report from an Argus-AI final_report JSON file.")
    parser.add_argument("--input", required=True, help="Path to a final_report JSON file (saved via main.py --output).")
    parser.add_argument("--output", default=None, help="Path for the output PDF (default: same name, .pdf extension).")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        final_report = json.load(f)

    output_path = args.output or os.path.splitext(args.input)[0] + ".pdf"
    agent = ReportAgent()
    path = agent.generate(final_report, output_path)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    main()