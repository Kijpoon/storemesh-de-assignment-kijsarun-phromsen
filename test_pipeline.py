import pandas as pd
import pytest

from pipeline import transform_customers, transform_orders

def test_transform_customers():
    dummy_customer = pd.DataFrame({
        "customer_id": [1, 2, 3],
        "full_name": ["Jake", "Roger", "Becci"],
        "email": [None, "roger@example.com", "becci@example.com"],
        "phone": ["+1(417)2946090", "368-869-3049", "1(573)242-6353"],
        "signup_date": ["2023-03-16", "2023-04-25", "2023-01-30"]
    })

    test_customers = transform_customers(dummy_customer)

    assert test_customers["phone"].iloc[0] == "14172946090"
    assert test_customers["phone"].iloc[1] == "3688693049"
    assert test_customers["phone"].iloc[2] == "15732426353"
    assert test_customers["email"].iloc[0] == "unknown@domain.com"

def test_transform_orders():
    dummy_orders = pd.DataFrame({
        "order_id": [101, 102, 103, 104],
        "customer_id": [1, 2, 3, 4],
        "total_amount": [-100, 200, 300, 400],
        "order_date": ["2023-01-01", "2023-01-01", "2023-01-02", "2023-01-02"],
        "currency": ["USD", "EUR", None, "JPY"],
    })

    dummy_rate = pd.DataFrame({
        "currency": ["EUR", "JPY"],
        "rate_to_usd": [1.12, 0.0069],
        "date": ["2023-01-01", "2023-01-02"],
    })

    test_orders = transform_orders(dummy_orders, dummy_rate)

    assert len(test_orders) == 3
    assert 101 not in test_orders["order_id"].values

    assert test_orders.loc[test_orders["order_id"] == 103, "currency"].iloc[0] == "USD"
    assert test_orders.loc[test_orders["order_id"] == 103, "usd_amount"].iloc[0] == 300
    assert test_orders.loc[test_orders["order_id"] == 102, "usd_amount"].iloc[0] == pytest.approx(224.0)
    assert test_orders.loc[test_orders["order_id"] == 104, "usd_amount"].iloc[0] == pytest.approx(2.76)

    assert "rate_to_usd" not in test_orders.columns
    assert "date" not in test_orders.columns

def test_duplicate_customer_keeps_latest_signup():
    df = pd.DataFrame({
        "customer_id": [1, 1],
        "full_name": ["Kyle", "kyle"],
        "email": ["kyle@example.com", "kyle@example.com"],
        "phone": ["12336579080", "12336579080"],
        "signup_date": ["2023-01-01", "2023-06-01"],
    })
    result = transform_customers(df)
    assert len(result) == 1
    assert result["full_name"].iloc[0] == "kyle"
