from __future__ import annotations

from typing import Dict
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from loguru import logger


def make_quality_report(reports: Dict[str, dict], out_pdf: str | None = None) -> dict:
    # Aggregate
    summary = {}
    for k, v in reports.items():
        summary[k] = v
    if out_pdf:
        c = canvas.Canvas(out_pdf, pagesize=letter)
        text = c.beginText(40, 750)
        text.textLine("Data Quality Report")
        for k, v in summary.items():
            text.textLine(f"Section: {k}")
            for kk, vv in v.items():
                text.textLine(f"  {kk}: {vv}")
        c.drawText(text)
        c.showPage()
        c.save()
        logger.info("Saved PDF report to {}", out_pdf)
    return summary


def export_excel(df: pd.DataFrame, path: str):
    df.to_excel(path, index=False)
    logger.info("Exported Excel to {}", path)
