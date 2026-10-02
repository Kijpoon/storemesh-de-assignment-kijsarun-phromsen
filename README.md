## Part 1: Data Exploration & Understanding
Based on the SQL exploration of the `vw_raw_customers` and `vw_raw_orders` tables, the following primary data quality issues were identified:

1. **Inconsistent Phone Formatting & Invalid Characters:** The `phone` column contains mixed formats, including letters (e.g., "Ext", "DINO"), country codes, parentheses, and missing standard separators.
2. **Missing Data (Nulls):** Critical fields have missing values, notably the `email` and `phone` column in the customers table, as well as `order_date` and `currency` in the orders table.
3. **Invalid Total Amounts:** The orders table contains records where `total_amount` is less than or equal to 0, which indicates system errors.
4. **Duplicate Records:** There are duplicate rows sharing the same `customer_id` and `order_id` that need to be deduplicated.