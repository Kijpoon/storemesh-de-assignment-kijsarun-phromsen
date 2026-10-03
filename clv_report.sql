select c.customer_id,
       c.full_name,
       count(o.order_id) as total_orders_placed,
       sum(o.usd_amount) as lifetime_value_usd,
       strftime('%Y-%m', c.signup_date) as customer_cohort
from dim_customers as c
left join fct_orders as o on c.customer_id =o.customer_id
group by c.customer_id,
         c.full_name,
         customer_cohort
order by lifetime_value_usd desc;
