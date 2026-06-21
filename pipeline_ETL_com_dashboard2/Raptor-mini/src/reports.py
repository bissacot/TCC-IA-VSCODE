from __future__ import annotations
from pathlib import Path
from typing import Any
import pandas as pd
from fpdf import FPDF
from src.logger import logger


def export_to_excel(customers_df: pd.DataFrame, products_df: pd.DataFrame, sales_df: pd.DataFrame, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        customers_df.to_excel(writer, sheet_name="customers", index=False)
        products_df.to_excel(writer, sheet_name="products", index=False)
        sales_df.to_excel(writer, sheet_name="sales", index=False)
    logger.info("Exported transformed data to Excel: %s", path)


def generate_pdf_report(quality_report: dict[str, Any], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ETL Data Quality Report", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    for key, value in quality_report.items():
        pdf.cell(0, 8, f"{key.replace('_', ' ').title()}: {value}", ln=True)

    pdf.output(path)
    logger.info("Generated PDF report: %s", path)
