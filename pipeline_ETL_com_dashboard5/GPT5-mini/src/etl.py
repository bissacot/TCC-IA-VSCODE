from .extract import extract_sales_from_csv, extract_customers_from_json, extract_products_from_api
from .transform import transform_sales, transform_customers, transform_products
from .load import load_customers, load_products, load_sales
from .db import init_db
from .logger import get_logger

logger = get_logger(__name__)


def run_etl(do_init_db: bool = False) -> dict:
    if do_init_db:
        init_db()

    # Extract
    sales_raw = extract_sales_from_csv()
    customers_raw = extract_customers_from_json()
    products_raw = extract_products_from_api()

    # Transform
    sales, sales_quality = transform_sales(sales_raw)
    customers, cust_quality = transform_customers(customers_raw)
    products, prod_quality = transform_products(products_raw)

    # Load
    c = load_customers(customers)
    p = load_products(products)
    s = load_sales(sales)

    report = {
        'sales_quality': sales_quality,
        'customers_quality': cust_quality,
        'products_quality': prod_quality,
        'loaded': {'customers': c, 'products': p, 'sales': s}
    }

    logger.info('ETL completed: %s', report)
    return report


if __name__ == '__main__':
    run_etl(do_init_db=True)
