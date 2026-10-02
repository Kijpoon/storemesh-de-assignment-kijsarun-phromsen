# Import relevant package
import pandas as pd
import sqlite3
import re

# Extract Data from Database
def extract_data(db_path: str):
    conn = sqlite3.connect(db_path)

    df_customers = pd.read_sql_query("SELECT * FROM vw_raw_customers", conn)

    df_orders = pd.read_sql_query("SELECT * FROM vw_raw_orders", conn)

    df_rates = pd.read_sql_query("SELECT * "
                                 "FROM vw_exchange_rates", conn)

    conn.close()
    return df_customers, df_orders, df_rates

def transform_orders(df_order: pd.DataFrame, df_rate: pd.DataFrame) -> pd.DataFrame:

    df_clean = df_order[df_order["total_amount"] > 0].copy()

    df_merge = pd.merge(
        df_clean,
        df_rate,
        left_on=["order_date", "currency"],
        right_on=["date", "currency"],
        how="left"
    )

    df_merge["rate_to_usd"] = df_merge["rate_to_usd"].fillna(1.0)

    df_merge["usd_amount"] = df_merge["total_amount"] * df_merge["rate_to_usd"]

    df_merge = df_merge.drop(columns=["date", "rate_to_usd"])

    return df_merge

