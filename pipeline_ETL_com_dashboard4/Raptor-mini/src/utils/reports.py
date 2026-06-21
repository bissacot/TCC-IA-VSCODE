from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_to_excel(data: dict[str, pd.DataFrame], output_path: Path) -> None:
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def export_to_pdf(html_content: str, output_path: Path) -> None:
    import pdfkit

    pdfkit.from_string(html_content, str(output_path))


def quality_html_report(report: dict[str, object]) -> str:
    sections = ["<h1>Data Quality Report</h1>"]
    for dataset_name, metrics in report.items():
        sections.append(f"<h2>{dataset_name.title()}</h2>")
        sections.append("<ul>")
        for label, value in metrics.items():
            sections.append(f"<li><strong>{label.replace('_', ' ').title()}:</strong> {value}</li>")
        sections.append("</ul>")
    return "\n".join(sections)
