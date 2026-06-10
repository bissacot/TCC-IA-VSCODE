"""
Report generation utilities (PDF, Excel, etc.).
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib import colors
from sqlalchemy.orm import Session

from src.database.connection import DatabaseManager
from src.database.models import DataQualityMetric, Sale, Customer, Product
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class ReportGenerator:
    """Generate reports in various formats."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir or Path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session: Session = DatabaseManager.get_session()
        logger.info(f"Initialized report generator with output dir: {self.output_dir}")

    def generate_excel_report(
        self,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate Excel report with multiple sheets.

        Args:
            filename: Output filename

        Returns:
            Path to generated file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sales_report_{timestamp}.xlsx"

            output_path = self.output_dir / filename

            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                # Sales data
                sales_df = pd.read_sql(
                    """
                    SELECT s.*, c.name as customer_name, p.name as product_name 
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.customer_id
                    JOIN products p ON s.product_id = p.product_id
                    LIMIT 10000
                    """,
                    self.session.bind,
                )
                sales_df.to_excel(writer, sheet_name="Sales", index=False)

                # Customer data
                customers_df = pd.read_sql("SELECT * FROM customers LIMIT 5000", self.session.bind)
                customers_df.to_excel(writer, sheet_name="Customers", index=False)

                # Product data
                products_df = pd.read_sql("SELECT * FROM products", self.session.bind)
                products_df.to_excel(writer, sheet_name="Products", index=False)

                # Summary statistics
                summary_data = self._get_summary_statistics()
                summary_df = pd.DataFrame(
                    list(summary_data.items()),
                    columns=["Metric", "Value"]
                )
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

            logger.info(f"Excel report generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate Excel report: {str(e)}")
            raise

    def generate_pdf_report(
        self,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate PDF report with quality metrics and summary.

        Args:
            filename: Output filename

        Returns:
            Path to generated file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"quality_report_{timestamp}.pdf"

            output_path = self.output_dir / filename

            # Create PDF
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )

            story = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=30,
                alignment=1,  # Center alignment
            )

            # Title
            story.append(Paragraph("Sales Analytics - Data Quality Report", title_style))
            story.append(Spacer(1, 0.2 * inch))

            # Generation time
            story.append(Paragraph(
                f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.3 * inch))

            # Summary statistics
            summary = self._get_summary_statistics()
            story.append(Paragraph("Summary Statistics", styles['Heading2']))
            summary_table_data = [["Metric", "Value"]]
            for key, value in summary.items():
                summary_table_data.append([key, str(value)])

            summary_table = Table(summary_table_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3 * inch))

            # Data quality metrics
            story.append(PageBreak())
            story.append(Paragraph("Data Quality Metrics", styles['Heading2']))

            latest_metric = self.session.query(DataQualityMetric).order_by(
                DataQualityMetric.created_at.desc()
            ).first()

            if latest_metric:
                metric_data = [
                    ["Metric", "Value"],
                    ["Total Records Processed", str(latest_metric.total_records_processed)],
                    ["Invalid Records", str(latest_metric.invalid_records)],
                    ["Missing Values %", f"{latest_metric.missing_values_percentage:.2f}%"],
                    ["Duplicates Removed", str(latest_metric.duplicates_removed)],
                    ["Transformation Time (s)", f"{latest_metric.transformation_time_seconds:.2f}"],
                    ["Status", latest_metric.status],
                ]

                metric_table = Table(metric_data)
                metric_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(metric_table)

            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate PDF report: {str(e)}")
            raise

    def _get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics from database."""
        try:
            num_customers = self.session.query(Customer).count()
            num_products = self.session.query(Product).count()
            num_sales = self.session.query(Sale).count()

            # Revenue calculation
            sales_data = self.session.query(Sale).all()
            total_revenue = sum(sale.total_value for sale in sales_data)
            avg_sale_value = total_revenue / num_sales if num_sales > 0 else 0

            return {
                "Total Customers": num_customers,
                "Total Products": num_products,
                "Total Sales": num_sales,
                "Total Revenue": f"R$ {total_revenue:,.2f}",
                "Average Sale Value": f"R$ {avg_sale_value:,.2f}",
            }
        except Exception as e:
            logger.error(f"Failed to get summary statistics: {str(e)}")
            return {}

    def close(self) -> None:
        """Close database session."""
        if self.session:
            self.session.close()
