from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
from pathlib import Path


def export_excel(df: pd.DataFrame, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)


def export_pdf_summary(summary: dict, path: str):
    c = canvas.Canvas(path, pagesize=letter)
    y = 750
    c.setFont("Helvetica", 12)
    c.drawString(50, y, "ETL Data Quality Report")
    y -= 30
    for k, v in summary.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 20
    c.save()
