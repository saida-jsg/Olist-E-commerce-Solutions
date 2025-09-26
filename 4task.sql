
-- 1. this previews first 10 rows from orders
SELECT * FROM olist_orders LIMIT 10;

-- 2. this gets delivered orders after 2018-01-01 sorted by delivery date
SELECT order_id, customer_id, order_status, order_delivered_customer_date
FROM olist_orders
WHERE order_status = 'delivered' AND order_delivered_customer_date > '2018-01-01'
ORDER BY order_delivered_customer_date ASC;

-- 3. aggregation: count orders per status
SELECT order_status, COUNT(*) AS total_orders
FROM olist_orders
GROUP BY order_status;

-- 4. aggregation with AVG: aerage payment value per payment type
SELECT payment_type, AVG(payment_value) AS avg_payment
FROM olist_order_payments
GROUP BY payment_type;

-- 5. aggregation with MIN/MAX: Earliest and latest purchase date
SELECT MIN(order_purchase_timestamp) AS first_order,
       MAX(order_purchase_timestamp) AS last_order
FROM olist_orders;

-- 6. JOIN example: Join orders with customers to get customer city/state
SELECT o.order_id, c.customer_city, c.customer_state, o.order_status
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id
LIMIT 10;

-- =====================================
-- c. Define 10 analytical topics for your project 
-- =====================================

-- 1. Total number of orders per year
SELECT DATE_PART('year', order_purchase_timestamp) AS year,
       COUNT(*) AS total_orders
FROM olist_orders
GROUP BY year
ORDER BY year;

-- 2. Average review score per product
SELECT oi.product_id, AVG(r.review_score) AS avg_score
FROM olist_order_items oi
JOIN olist_order_reviews r ON oi.order_id = r.order_id
GROUP BY oi.product_id
ORDER BY avg_score DESC;

-- 3. Top 10 states by number of customers
SELECT customer_state, COUNT(*) AS total_customers
FROM olist_customers
GROUP BY customer_state
ORDER BY total_customers DESC
LIMIT 10;

-- 4. Average payment value per installment count
SELECT payment_installments, AVG(payment_value) AS avg_payment
FROM olist_order_payments
GROUP BY payment_installments
ORDER BY payment_installments;

-- 5. Number of orders by delivery status (delivered, shipped, canceled, etc.)
SELECT order_status, COUNT(*) AS total
FROM olist_orders
GROUP BY order_status
ORDER BY total DESC;

-- 6. Average delivery time (customer date - purchase date)
SELECT AVG(order_delivered_customer_date - order_purchase_timestamp) AS avg_delivery_days
FROM olist_orders
WHERE order_status = 'delivered';

-- 7. Top 10 most sold products
SELECT oi.product_id, COUNT(*) AS total_sold
FROM olist_order_items oi
GROUP BY oi.product_id
ORDER BY total_sold DESC
LIMIT 10;

-- 8. Seller performance: total sales value per seller
SELECT oi.seller_id, SUM(oi.price) AS total_sales
FROM olist_order_items oi
GROUP BY oi.seller_id
ORDER BY total_sales DESC
LIMIT 10;

-- 9. Average freight value by state
SELECT c.customer_state, AVG(oi.freight_value) AS avg_freight
FROM olist_order_items oi
JOIN olist_orders o ON oi.order_id = o.order_id
JOIN olist_customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY avg_freight DESC;

-- 10. Number of reviews per score (distribution of ratings)
SELECT review_score, COUNT(*) AS review_count
FROM olist_order_reviews
GROUP BY review_score
ORDER BY review_score;
