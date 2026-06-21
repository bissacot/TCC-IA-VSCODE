from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def export_excel(sales: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame, output_path: str) -> None:
    output_file = Path(output_path)
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        sales.to_excel(writer, sheet_name="sales", index=False)
        customers.to_excel(writer, sheet_name="customers", index=False)
        products.to_excel(writer, sheet_name="products", index=False)


def export_pdf(summary: dict[str, Any], output_path: str) -> None:
    output_file = Path(output_path)
    document = canvas.Canvas(str(output_file), pagesize=letter)
    document.setTitle("Sales Data Quality Report")
    document.setFont("Helvetica-Bold", 14)
    document.drawString(1 * inch, 10.5 * inch, "Sales Data Quality Report")
    document.setFont("Helvetica", 10)
    document.drawString(1 * inch, 10.1 * inch, f"Generated: {datetime.utcnow().isoformat()}Z")

    top = 9.7
    for report in summary.get("reports", []):
        document.drawString(1 * inch, top * inch, f"Entity: {report['entity']}")
        top -= 0.2
        document.drawString(1.2 * inch, top * inch, f"Processed: {report['processed_records']}")
        top -= 0.2
        document.drawString(1.2 * inch, top * inch, f"Invalid: {report['invalid_records']}")
        top -= 0.2
        document.drawString(1.2 * inch, top * inch, f"Duplicates: {report['duplicates_removed']}")
        top -= 0.2
        document.drawString(1.2 * inch, top * inch, f"Missing: {report['missing_values']}")
        top -= 0.4
        if top < 1.5:
            document.showPage()
            document.setFont("Helvetica", 10)
            top = 10.5

    document.drawString(1 * inch, top * inch, f"Total processed: {summary.get('total_processed', 0)}")
    document.drawString(1 * inch, (top - 0.2) * inch, f"Total invalid: {summary.get('total_invalid', 0)}")
    document.drawString(1 * inch, (top - 0.4) * inch, f"Total duplicates: {summary.get('total_duplicates', 0)}")
    document.drawString(1 * inch, (top - 0.6) * inch, f"Total missing: {summary.get('total_missing', 0)}")
    document.save()
