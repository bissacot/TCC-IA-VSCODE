from typing import Any
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .logger import get_logger

logger = get_logger(__name__)


def export_to_excel(df: pd.DataFrame, path: str) -> None:
    df.to_excel(path, index=False)
    logger.info('Exported Excel to %s', path)


def export_kpis_pdf(kpis: dict, path: str) -> None:
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont('Helvetica-Bold', 14)
    c.drawString(50, y, 'Sales KPIs')
    y -= 30
    c.setFont('Helvetica', 10)
    for k, v in kpis.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 20
    c.save()
    logger.info('Generated PDF report %s', path)
