"""PDF and Excel report generation."""

from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import json
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from src.utils.logger import logger
from src.utils.exceptions import ETLException
from src.loaders.database import DatabaseManager
from src.utils.config import DatabaseConfig


class ReportGenerator:
    """Generates PDF and Excel reports."""
    
    def __init__(self, db_config: DatabaseConfig):
        """
        Initialize report generator.
        
        Args:
            db_config: Database configuration
        """
        self.db_manager = DatabaseManager(db_config)
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_pdf_report(
        self,
        filename: str = "sales_report.pdf",
        quality_report_path: Optional[str] = None
    ) -> str:
        """
        Generate PDF report.
        
        Args:
            filename: Output filename
            quality_report_path: Path to quality report JSON
        
        Returns:
            Path to generated PDF
        """
        try:
            logger.info(f"Generating PDF report: {filename}")
            
            report_path = self.output_dir / filename
            doc = SimpleDocTemplate(str(report_path), pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("Sales Analytics Report", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Report Info
            report_info = f"""
            <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>Report Type:</b> Sales Analysis<br/>
            """
            story.append(Paragraph(report_info, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            
            # Load KPI data
            kpi_query = """
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(total_value) as total_revenue,
                    AVG(total_value) as avg_ticket,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    COUNT(DISTINCT product_id) as unique_products
                FROM sales
            """
            
            kpi_data = self.db_manager.execute_query(kpi_query)
            kpi = kpi_data[0] if kpi_data else {}
            
            summary_text = f"""
            <b>Total Sales:</b> {kpi.get('total_sales', 0):,}<br/>
            <b>Total Revenue:</b> ${kpi.get('total_revenue', 0):,.2f}<br/>
            <b>Average Ticket Size:</b> ${kpi.get('avg_ticket', 0):.2f}<br/>
            <b>Unique Customers:</b> {kpi.get('unique_customers', 0):,}<br/>
            <b>Unique Products:</b> {kpi.get('unique_products', 0):,}<br/>
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Data Quality Report
            if quality_report_path and Path(quality_report_path).exists():
                story.append(PageBreak())
                story.append(Paragraph("Data Quality Report", styles['Heading2']))
                
                with open(quality_report_path, 'r') as f:
                    quality_data = json.load(f)
                
                quality_text = f"""
                <b>Total Records Processed:</b> {quality_data.get('total_records_processed', 0):,}<br/>
                <b>Invalid Records:</b> {quality_data.get('total_invalid_records', 0):,}<br/>
                <b>Duplicates Removed:</b> {quality_data.get('duplicates_removed', 0):,}<br/>
                """
                story.append(Paragraph(quality_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {report_path}")
            return str(report_path)
        
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise ETLException(f"PDF generation error: {str(e)}")
    
    def generate_excel_report(
        self,
        filename: str = "sales_report.xlsx"
    ) -> str:
        """
        Generate Excel report with multiple sheets.
        
        Args:
            filename: Output filename
        
        Returns:
            Path to generated Excel file
        """
        try:
            logger.info(f"Generating Excel report: {filename}")
            
            report_path = self.output_dir / filename
            
            with pd.ExcelWriter(str(report_path), engine='openpyxl') as writer:
                # Sales data
                sales_query = """
                    SELECT 
                        s.sale_id,
                        s.sale_date,
                        c.name as customer,
                        c.state,
                        p.name as product,
                        p.category,
                        s.quantity,
                        s.unit_price,
                        s.total_value
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.customer_id
                    JOIN products p ON s.product_id = p.product_id
                    ORDER BY s.sale_date DESC
                    LIMIT 10000
                """
                
                sales_df = pd.DataFrame(self.db_manager.execute_query(sales_query))
                sales_df.to_excel(writer, sheet_name='Sales', index=False)
                
                # Customers data
                customers_query = "SELECT * FROM customers LIMIT 5000"
                customers_df = pd.DataFrame(self.db_manager.execute_query(customers_query))
                customers_df.to_excel(writer, sheet_name='Customers', index=False)
                
                # Products data
                products_query = "SELECT * FROM products LIMIT 5000"
                products_df = pd.DataFrame(self.db_manager.execute_query(products_query))
                products_df.to_excel(writer, sheet_name='Products', index=False)
                
                # Summary statistics
                summary_query = """
                    SELECT 
                        p.category,
                        COUNT(*) as sales_count,
                        SUM(s.total_value) as total_revenue,
                        AVG(s.total_value) as avg_value,
                        COUNT(DISTINCT s.customer_id) as customers
                    FROM sales s
                    JOIN products p ON s.product_id = p.product_id
                    GROUP BY p.category
                    ORDER BY total_revenue DESC
                """
                
                summary_df = pd.DataFrame(self.db_manager.execute_query(summary_query))
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            logger.info(f"Excel report generated: {report_path}")
            return str(report_path)
        
        except Exception as e:
            logger.error(f"Excel generation failed: {str(e)}")
            raise ETLException(f"Excel generation error: {str(e)}")
    
    def close(self):
        """Close database connections."""
        self.db_manager.close()
