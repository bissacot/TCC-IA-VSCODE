"""
Report and export generation utilities.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from src.database.connection import DatabaseConnection
from src.utils.config import Config
from src.utils.logger import get_logger


logger = get_logger()


class ReportGenerator:
    """Generate various reports from processed data."""

    def __init__(self):
        self.db = DatabaseConnection()
        self.logger = get_logger()

    def generate_quality_report_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML quality report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Quality Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                .metric {{ display: inline-block; margin: 10px 20px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                .metric-label {{ font-size: 14px; color: #666; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                table, th, td {{ border: 1px solid #ddd; }}
                th {{ background-color: #007bff; color: white; padding: 10px; }}
                td {{ padding: 8px; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .summary {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Data Quality Report</h1>
            <p>Generated: {report_data.get('report_timestamp')}</p>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <div class="metric">
                    <div class="metric-label">Total Records Processed</div>
                    <div class="metric-value">{report_data.get('total_records_processed', 0):,}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Valid Records</div>
                    <div class="metric-value">{report_data.get('valid_records', 0):,}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Invalid Records</div>
                    <div class="metric-value">{report_data.get('invalid_records', 0):,}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Duplicates Removed</div>
                    <div class="metric-value">{report_data.get('duplicates_removed', 0):,}</div>
                </div>
            </div>
            
            <h2>Data Quality Metrics</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Valid Records</td>
                    <td>{report_data.get('valid_records', 0):,}</td>
                </tr>
                <tr>
                    <td>Invalid Records</td>
                    <td>{report_data.get('invalid_records', 0):,}</td>
                </tr>
                <tr>
                    <td>Missing Values Count</td>
                    <td>{report_data.get('missing_values_count', 0):,}</td>
                </tr>
                <tr>
                    <td>Missing Values Percentage</td>
                    <td>{report_data.get('missing_values_percentage', 0):.2f}%</td>
                </tr>
                <tr>
                    <td>Data Type Errors</td>
                    <td>{report_data.get('data_type_errors', 0):,}</td>
                </tr>
                <tr>
                    <td>Date Conversion Errors</td>
                    <td>{report_data.get('date_conversion_errors', 0):,}</td>
                </tr>
                <tr>
                    <td>Processing Time</td>
                    <td>{report_data.get('processing_time_seconds', 0):.2f}s</td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html_content

    def save_quality_report(self, report_data: Dict[str, Any]) -> str:
        """Save quality report as HTML."""
        try:
            Path(Config.REPORT_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f"quality_report_{timestamp}.html"
            report_path = Path(Config.REPORT_OUTPUT_DIR) / report_filename
            
            html_content = self.generate_quality_report_html(report_data)
            
            with open(report_path, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"Quality report saved: {report_path}")
            return str(report_path)
        except Exception as e:
            self.logger.error(f"Error saving quality report: {str(e)}")
            raise


class ExcelExporter:
    """Export data to Excel files."""

    def __init__(self):
        self.db = DatabaseConnection()
        self.logger = get_logger()

    def export_sales_data(self) -> str:
        """Export sales data to Excel."""
        try:
            self.db.connect()
            
            # Query data
            query = """
                SELECT 
                    s.sale_id, s.customer_id, c.name as customer_name,
                    s.product_id, p.name as product_name, p.category,
                    s.quantity, s.unit_price, s.total_value,
                    s.sale_date, s.state, s.payment_method
                FROM sales s
                JOIN customers c ON s.customer_id = c.customer_id
                JOIN products p ON s.product_id = p.product_id
                ORDER BY s.sale_date DESC
                LIMIT 10000
            """
            
            results = self.db.execute_query(query)
            df = pd.DataFrame(results)
            
            # Create Excel file
            Path(Config.EXCEL_EXPORT_DIR).mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"sales_export_{timestamp}.xlsx"
            export_path = Path(Config.EXCEL_EXPORT_DIR) / export_filename
            
            with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Sales', index=False)
            
            self.logger.info(f"Sales data exported: {export_path}")
            return str(export_path)
        
        except Exception as e:
            self.logger.error(f"Error exporting sales data: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def export_summary_statistics(self) -> str:
        """Export summary statistics to Excel."""
        try:
            self.db.connect()
            
            Path(Config.EXCEL_EXPORT_DIR).mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"summary_statistics_{timestamp}.xlsx"
            export_path = Path(Config.EXCEL_EXPORT_DIR) / export_filename
            
            with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                # Sales by month
                monthly = self.db.execute_query("""
                    SELECT * FROM monthly_revenue ORDER BY year DESC, month DESC
                """)
                pd.DataFrame(monthly).to_excel(writer, sheet_name='Monthly Revenue', index=False)
                
                # Product performance
                products = self.db.execute_query("""
                    SELECT * FROM product_performance ORDER BY total_revenue DESC
                """)
                pd.DataFrame(products).to_excel(writer, sheet_name='Product Performance', index=False)
                
                # State distribution
                states = self.db.execute_query("""
                    SELECT * FROM state_sales_distribution ORDER BY total_revenue DESC
                """)
                pd.DataFrame(states).to_excel(writer, sheet_name='State Distribution', index=False)
                
                # Category performance
                categories = self.db.execute_query("""
                    SELECT * FROM category_performance ORDER BY total_revenue DESC
                """)
                pd.DataFrame(categories).to_excel(writer, sheet_name='Category Performance', index=False)
            
            self.logger.info(f"Summary statistics exported: {export_path}")
            return str(export_path)
        
        except Exception as e:
            self.logger.error(f"Error exporting summary statistics: {str(e)}")
            raise
        finally:
            self.db.disconnect()


class PDFReportGenerator:
    """Generate PDF reports from sales data."""

    def __init__(self):
        self.db = DatabaseConnection()
        self.logger = get_logger()

    def generate_sales_report(self) -> str:
        """Generate comprehensive sales PDF report."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            
            self.db.connect()
            
            Path(Config.REPORT_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f"sales_report_{timestamp}.pdf"
            report_path = Path(Config.REPORT_OUTPUT_DIR) / report_filename
            
            # Create PDF
            doc = SimpleDocTemplate(str(report_path), pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#007bff'),
                spaceAfter=30,
            )
            elements.append(Paragraph("Sales Report", title_style))
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            elements.append(Spacer(1, 0.3 * inch))
            
            # Summary statistics
            summary_query = """
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(total_value) as total_revenue,
                    AVG(total_value) as avg_sale_value,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM sales
            """
            summary = self.db.execute_query(summary_query)[0]
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Sales', f"{summary['total_sales']:,}"],
                ['Total Revenue', f"${summary['total_revenue']:,.2f}"],
                ['Average Sale Value', f"${summary['avg_sale_value']:,.2f}"],
                ['Unique Customers', f"{summary['unique_customers']:,}"],
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Build PDF
            doc.build(elements)
            
            self.logger.info(f"PDF report generated: {report_path}")
            return str(report_path)
        
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            raise
        finally:
            self.db.disconnect()
