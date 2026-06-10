"""
Apache Airflow DAG for ETL pipeline scheduling.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from src.etl.pipeline import ETLPipeline
from src.utils.report_export import ReportGenerator, ExcelExporter, PDFReportGenerator


# Default arguments
default_args = {
    'owner': 'data_team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
}

# DAG definition
dag = DAG(
    'sales_etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline for sales data',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
)


def run_etl_pipeline():
    """Run ETL pipeline."""
    pipeline = ETLPipeline()
    result = pipeline.run()
    return result


def refresh_materialized_views():
    """Refresh materialized views."""
    hook = PostgresHook(postgres_conn_id='postgres_etl_db')
    hook.run('SELECT refresh_materialized_views();')


def generate_reports():
    """Generate quality and sales reports."""
    report_gen = ReportGenerator()
    excel_gen = ExcelExporter()
    pdf_gen = PDFReportGenerator()
    
    # Generate reports
    try:
        excel_gen.export_sales_data()
        excel_gen.export_summary_statistics()
        pdf_gen.generate_sales_report()
    except Exception as e:
        print(f"Error generating reports: {str(e)}")


# Task definitions
task_run_etl = PythonOperator(
    task_id='run_etl_pipeline',
    python_callable=run_etl_pipeline,
    dag=dag,
)

task_refresh_views = PythonOperator(
    task_id='refresh_materialized_views',
    python_callable=refresh_materialized_views,
    dag=dag,
)

task_generate_reports = PythonOperator(
    task_id='generate_reports',
    python_callable=generate_reports,
    dag=dag,
)

# Task dependencies
task_run_etl >> task_refresh_views >> task_generate_reports
