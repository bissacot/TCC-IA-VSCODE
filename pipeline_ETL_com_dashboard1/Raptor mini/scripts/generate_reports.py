from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from fpdf import FPDF
from sqlalchemy import create_engine, text

from src.etl_app.config import settings
from src.etl_app.logger import get_logger

logger = get_logger(__name__)

REPORT_PATH = Path("reports")
PDF_PATH = REPORT_PATH / "sales_summary.pdf"


def build_summary(engine: Any) -> dict[str, object]:
    logger.info("Generating summary report data")
    query_metrics = text(
        "SELECT "
        "COALESCE(SUM(total_sale_value), 0) AS total_revenue, "
        "COUNT(*) AS sales_count, "
        "COALESCE(AVG(total_sale_value), 0) AS average_ticket, "
        "COUNT(DISTINCT customer_id) AS unique_customers "
        "FROM sales"
    )

    query_top_products = text(
        "SELECT p.product_name, p.category, SUM(s.quantity) AS units_sold, "
        "SUM(s.total_sale_value) AS revenue "
        "FROM sales s "
        "JOIN products p ON s.product_id = p.product_id "
        "GROUP BY p.product_id, p.product_name, p.category "
        "ORDER BY revenue DESC "
        "LIMIT 10"
    )

    with engine.connect() as connection:
        metrics = connection.execute(query_metrics).mappings().one()
        top_products = pd.read_sql(query_top_products, connection)

    return {
        "total_revenue": float(metrics["total_revenue"]),
        "sales_count": int(metrics["sales_count"]),
        "average_ticket": float(metrics["average_ticket"]),
        "unique_customers": int(metrics["unique_customers"]),
        "top_products": top_products,
    }


def write_pdf(summary: dict[str, object], output_path: Path = PDF_PATH) -> Path:
    REPORT_PATH.mkdir(parents=True, exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Sales Summary Report", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.ln(4)

    pdf.cell(0, 8, f"Total revenue: ${summary['total_revenue']:.2f}", ln=True)
    pdf.cell(0, 8, f"Number of sales: {summary['sales_count']}", ln=True)
    pdf.cell(0, 8, f"Average ticket: ${summary['average_ticket']:.2f}", ln=True)
    pdf.cell(0, 8, f"Unique customers: {summary['unique_customers']}", ln=True)
    pdf.ln(6)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Top 10 Products", ln=True)
    pdf.set_font("Arial", "", 10)

    pdf.cell(70, 8, "Product", border=1)
    pdf.cell(50, 8, "Category", border=1)
    pdf.cell(30, 8, "Revenue", border=1, align="R")
    pdf.cell(30, 8, "Units", border=1, align="R")
    pdf.ln()

    for _, row in summary["top_products"].iterrows():
        pdf.cell(70, 8, str(row["product_name"]), border=1)
        pdf.cell(50, 8, str(row["category"]), border=1)
        pdf.cell(30, 8, f"${row['revenue']:.2f}", border=1, align="R")
        pdf.cell(30, 8, str(int(row["units_sold"])), border=1, align="R")
        pdf.ln()

    pdf.output(str(output_path))
    logger.info("PDF report written to %s", output_path)
    return output_path


def main() -> None:
    engine = create_engine(settings.db_url)
    summary = build_summary(engine)
    write_pdf(summary)


if __name__ == "__main__":
    main()
