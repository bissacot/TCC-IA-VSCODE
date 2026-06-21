import pandas as pd
from src.transform import transform_sales


def test_transform_sales_basic():
    df = pd.DataFrame([
        {'sale_id':'1','customer_id':'c1','product_id':'p1','quantity':2,'unit_price':10,'sale_date':'2023-01-15','state':'CA'},
        {'sale_id':'2','customer_id':'c2','product_id':'p2','quantity':1,'unit_price':5,'sale_date':'2023-02-01','state':'NY'},
        {'sale_id':'2','customer_id':'c2','product_id':'p2','quantity':1,'unit_price':5,'sale_date':'2023-02-01','state':'NY'},
    ])

    cleaned, report = transform_sales(df)
    assert report['duplicates_removed'] == 1
    assert report['processed_records'] == 2
    assert 'total_value' in cleaned.columns
