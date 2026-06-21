import pandas as pd
from src.transform import transform_sales


def test_transform_sales_basic():
    df = pd.DataFrame([
        {'sale_id':'1','customer_id':'c1','product_id':'p1','sale_date':'2023-01-10','quantity':2,'unit_price':10},
        {'sale_id':'2','customer_id':'c2','product_id':'p2','sale_date':'2023-02-15','quantity':1,'unit_price':20}
    ])
    transformed, quality = transform_sales(df)
    assert quality['original_count'] == 2
    assert 'total_value' in transformed.columns
    assert len(transformed) == 2
