# Import relevant package
from prefect import task, get_run_logger
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

    df_clean["currency"] = df_clean["currency"].fillna("USD")

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

def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.drop_duplicates(subset=['customer_id'], keep='last').reset_index(drop=True)

    df_clean["email"] = df_clean["email"].fillna("unknown@domain.com")

    df_clean["phone"] = df_clean["phone"].apply(lambda x: re.sub(r"\D", "", str(x)))

    return df_clean

@task(name="Load Dim Customers")
def load_customers_data(df_customers: pd.DataFrame):

    logger = get_run_logger()

    try:
        logger.info("Attempting to create and save data to analytics.db...")

        conn = sqlite3.connect("analytics.db")

        df_customers.to_sql("dim_customers", conn, if_exists="replace", index=False)

        conn.close()

        logger.info("Data successfully saved to analytics.db")

    except Exception as e:

        logger.warning(f"Database error encountered: {e}. Falling back to CSV.")

        df_customers.to_csv("clean_customers.csv", index=False)

        logger.info("Data successfully saved to clean_customers.csv")

