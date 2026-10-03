import pandas as pd
import pytest

from pipeline import transform_customers, transform_orders

def test_transform_customers():
    dummy_customer = pd.DataFrame({
        "customer_id": [1, 2, 3],
        "full_name": ["Jake", "Roger", "Becci"],
        "email": [None, "roger@example.com", "becci@example.com"],
        "phone": ["+1(417)2946090", "368-869-3049", "1(573)242-6353"]
    })

    test_customers = transform_customers(dummy_customer)

    assert test_customers["phone"].iloc[0] == "14172946090"
    assert test_customers["phone"].iloc[1] == "3688693049"
    assert test_customers["phone"].iloc[2] == "15732426353"
    assert test_customers["email"].iloc[0] == "unknown@domain.com"