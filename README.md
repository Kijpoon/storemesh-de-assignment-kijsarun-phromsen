# StoreMesh Data Engineering Assignment

An end-to-end Data Engineering pipeline designed to extract raw e-commerce data, transform it through rigorous data quality rules, and load it into an analytical SQLite database. This project also includes automated unit tests and an analytical SQL query to calculate Customer Lifetime Value (CLV).

## Part 1: Data Exploration & Understanding
Based on the initial SQL exploration (`exploration.sql`) of the `vw_raw_customers` and `vw_raw_orders` views, several data quality issues were identified:

1. **Inconsistent Phone Formatting:** The `phone` column contains mixed formats, letters (e.g., "Ext"), country codes, and parentheses. (Note: Extraction logic strips all non-numeric characters. If a phone number includes an extension like "Ext 123", it is currently compressed into the numeric string. Further business logic clarification would be needed for extension handling).
2. **Missing Data (Nulls):** 
   - Customers: 3 of 12 customers have missing contact info: 1 is missing only email, 1 is missing only phone, and 1 is missing both.
   - Orders: 1 rows have a NULL order_date and 2 rows have a NULL currency.
3. **Invalid Total Amounts:** Found 3 records in the orders table where `total_amount <= 0`.
4. **Duplicate Records:** 
   - Customers: 2 customer_id values appear more than once (2 extra rows in total).
   - Orders: [No duplicates found in orders].

## Part 2: ETL Pipeline
The pipeline (`pipeline.py`) resolves the identified issues using Python and Pandas, orchestrated by Prefect:
- Deduplicates customers by keeping the row with the most recent `signup_date`.
- Standardizes phone numbers to contain only digits.
- Filters out orders with invalid amounts (`total_amount <= 0`).
- Fills missing `currency` values with 'USD' as the default baseline.
- Converts transaction currencies to USD using the provided exchange rates.

## Part 3: Unit Testing
test_pipeline.py uses pytest with in-memory DataFrames, so no database connection is needed. It covers the phone standardizer, customer deduplication, and currency conversion, including edge cases such as missing emails and total_amount <= 0.

## Part 4: Data Analytics
clv_report.sql is a single query over dim_customers and fct_orders that returns customer_id, full_name, total_orders_placed, lifetime_value_usd, and customer_cohort (YYYY-MM of signup), ranked by lifetime_value_usd in descending order.

## Tech Stack
* **Language**: Python 3
* **Data Processing**: Pandas
* **Orchestration**: Prefect (Configured for local ephemeral run)
* **Database**: SQLite3
* **Testing**: Pytest
* **Query Language**: SQL

## Project Structure
```text
storemesh-de-assignment/
├── exploration.sql      # Data Exploration to uncover anomalies 
├── pipeline.py          # Main ETL script (Extract, Transform, Load)
├── test_pipeline.py     # Unit tests for data cleaning logic
├── clv_report.sql       # SQL script for Customer Lifetime Value analysis
├── analytics.db         # Output SQLite database (Generated after running pipeline)
├── README.md            # Project documentation
└── requirements.txt     # Python dependencies
```

## How to Run
### 1. Setup Environment: 
- Ensure you have `Python 3.12+` installed. It is recommended to use a virtual environment.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 2. Run the ETL Pipeline: 
- Execute the main pipeline to generate the `analytics.db` file. 
*(Note: Prefect is configured to run in ephemeral mode, requiring no external server setup).*
```bash
python3 pipeline.py
```
### 3. Run Unit Tests: 
- Validate the transformation logic (e.g., phone standardizer and currency conversion) using dummy data.
```bash
pytest test_pipeline.py -v
```
### 4. Generate CLV Report (SQL): 
- Run the analytical query against the generated database to view the Customer Lifetime Value.
```bash
sqlite3 analytics.db < clv_report.sql
```

## Assumptions & Design Decisions
* **Handling Missing Data:** Customers with missing phone numbers are retained (as Null) rather than dropped, preserving their transaction history for analytical purposes. Missing email addresses are systematically imputed with the placeholder `unknown@domain.com` to maintain data completeness.
* **Customer Deduplication Tie-Breaker:** As specified in the requirements, duplicated `customer_id` records are resolved by assuming the most recent `signup_date` is the correct and updated record. This is implemented by sorting the dataset chronologically by `signup_date` before deduplication.
* **Missing Order Dates & Exchange Rates:** If an order is missing a `currency`, an `order_date`, or lacks a corresponding daily rate in the exchange table, the system defaults the conversion rate to `1.0` (treated as USD). While this ensures the record is retained for CLV calculation, it introduces a known risk of slight revenue inaccuracy for non-USD transactions missing a valid date or rate.
* **CLV Query JOIN Logic:** A `LEFT JOIN` is used between `dim_customers` and `fct_orders` to ensure all registered customers appear in the final report, even if their total lifetime order amount is 0.

## Author
**Kijsarun Phromsen (Poom)**
* **Email:** [korawith.kho@outlook.com]
* **GitHub:** [https://github.com/Kijpoon]
* **LinkedIn:** [https://linkedin.com/in/kijsarun-phromsen-403922235]