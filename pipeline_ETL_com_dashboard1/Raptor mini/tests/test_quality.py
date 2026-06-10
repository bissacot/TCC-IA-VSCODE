import pandas as pd

from src.etl_app.transform import compile_quality_report


def test_compile_quality_report_has_expected_keys():
    sales = pd.DataFrame([{"sale_id": "S1", "quantity": 2}])
    customers = pd.DataFrame([{"customer_id": "C1", "customer_name": "Test"}])
    products = pd.DataFrame([{"product_id": "P1", "product_name": "Test", "category": "X", "unit_price": 1}])
    report = compile_quality_report(sales, customers, products, 0, 0, 0, 0)
    assert report["sales_processed"] == 1
    assert report["customers_processed"] == 1
    assert report["products_processed"] == 1
    assert report["invalid_records"] == 0
    assert "missing_values_percentage" in report
