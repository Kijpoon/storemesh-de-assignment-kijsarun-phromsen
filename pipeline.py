# Import relevant package
from prefect import task, get_run_logger, flow
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

# Transform Orders Data
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

# Transform Customers Data
def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    df['signup_date'] = pd.to_datetime(df['signup_date'])

    df_clean = df.sort_values(by=['customer_id', 'signup_date']).drop_duplicates(subset=['customer_id'], keep='last').reset_index(drop=True)

    df_clean["email"] = df_clean["email"].fillna("unknown@domain.com")

    df_clean["phone"] = df_clean["phone"].apply(lambda x: re.sub(r"\D", "", str(x)))

    return df_clean

# Create New Database and Load Data into Database
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

@task(name="Load Fct Orders")
def load_orders_data(df_orders: pd.DataFrame):
    logger = get_run_logger()
    try:
        logger.info("Attempting to create and save data to analytics.db...")

        conn = sqlite3.connect("analytics.db")

        df_orders.to_sql("fct_orders", conn, if_exists="replace", index=False)

        conn.close()

        logger.info("Data successfully saved to analytics.db")

    except Exception as e:

        logger.warning(f"Database error encountered: {e}. Falling back to CSV.")

        df_orders.to_csv("clean_fct_orders.csv", index=False)

        logger.info("Data successfully saved to clean_fct_orders.csv")

@flow(name="StoreMesh ETL Pipeline")
def main_etl_flow():
    # 1. Extract
    raw_customers, raw_orders, raw_rates = extract_data("shopdata.db")

    # 2. Transform
    clean_customers = transform_customers(raw_customers)
    clean_orders = transform_orders(raw_orders, raw_rates)

    # 3. Load
    dim_customers = load_customers_data(clean_customers)
    fct_orders = load_orders_data(clean_orders)

if __name__ == "__main__":
    main_etl_flow()

