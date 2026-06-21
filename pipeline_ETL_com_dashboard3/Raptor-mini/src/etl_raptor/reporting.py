from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas


def save_excel_report(data_frames: dict[str, pd.DataFrame], output_path: Path) -> None:
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, df in data_frames.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def build_pdf_report(summary: dict[str, object], output_path: Path) -> None:
    canvas_obj = canvas.Canvas(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    text_obj = canvas_obj.beginText(72, 720)
    text_obj.setFont("Helvetica", 12)
    text_obj.textLine("Sales ETL Quality Report")
    text_obj.moveCursor(0, 24)
    for key, value in summary.items():
        text_obj.textLine(f"{key}: {value}")
    canvas_obj.drawText(text_obj)
    canvas_obj.showPage()
    canvas_obj.save()
