#!/usr/bin/env python
"""
Main entry point for running the ETL pipeline.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.etl.pipeline import ETLPipeline
from src.utils.config import Config
from src.utils.logger import get_logger
from src.utils.sample_data import SampleDataGenerator
from src.utils.report_export import ReportGenerator, ExcelExporter, PDFReportGenerator


logger = get_logger()


def setup_sample_data():
    """Generate and setup sample data."""
    logger.info("Setting up sample data...")
    SampleDataGenerator.generate_all_sample_data()
    logger.info("Sample data setup complete!")


def run_pipeline():
    """Run the ETL pipeline."""
    logger.info("Starting ETL pipeline...")
    pipeline = ETLPipeline()
    result = pipeline.run()
    return result


def generate_reports():
    """Generate all reports."""
    logger.info("Generating reports...")
    report_gen = ReportGenerator()
    excel_gen = ExcelExporter()
    pdf_gen = PDFReportGenerator()
    
    try:
        excel_gen.export_sales_data()
        excel_gen.export_summary_statistics()
        if Config.PDF_REPORT_ENABLED:
            pdf_gen.generate_sales_report()
        logger.info("Reports generated successfully!")
    except Exception as e:
        logger.error(f"Error generating reports: {str(e)}")
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Sales ETL Pipeline')
    parser.add_argument('command', choices=['setup', 'run', 'reports', 'all'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    # Ensure directories exist
    Config.ensure_directories()
    
    try:
        if args.command == 'setup':
            setup_sample_data()
        elif args.command == 'run':
            run_pipeline()
        elif args.command == 'reports':
            generate_reports()
        elif args.command == 'all':
            setup_sample_data()
            run_pipeline()
            generate_reports()
        else:
            print("Unknown command")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
