-- View all data in the record
select *
from vw_raw_customers;

select *
from vw_raw_orders;

select *
from vw_exchange_rates;

-- Check for missing email & phone number (Null) in vw_raw_customers table
select *
from vw_raw_customers
where email is null or phone is null;

-- Check for missing data in vw_raw_orders table

select *
from vw_raw_orders
where order_date is null
        or currency is null;

-- Check duplicate row in vw_raw_customers table
select customer_id, count(*) as customer_count
from vw_raw_customers
group by customer_id
having customer_count > 1;

-- Check duplicate row in in vw_raw_orders table
select order_id, count(*) as order_count
from vw_raw_orders
group by order_id
having order_count > 1;

-- Check total amount <= 0 in vw_raw_orders table
select *
from vw_raw_orders
where total_amount <= 0;

-- Check for invalid phone numbers containing letters
select *
from vw_raw_customers
where phone glob '*[A-Za-z]*';

-- Check for phone numbers containing non-numeric characters (formatting issues)
select *
from vw_raw_customers
where phone glob '*[^0-9]*';