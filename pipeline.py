# Import relevant package
import pandas as pd
import sqlite3
import re

# Extract Data from Database
def extract_data(db_path: str):
    conn = sqlite3.connect(db_path)

    df_customers = pd.read_sql_query("SELECT * FROM vw_raw_customers", conn)

    df_orders = pd.read_sql_query("SELECT * FROM vw_raw_orders", conn)

    conn.close()
    return df_customers, df_orders

