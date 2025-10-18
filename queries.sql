-- 1. First 10 rows from orders with customer info (INNER JOIN)
SELECT o.order_id, o.order_status, o.order_purchase_timestamp, 
       c.customer_city, c.customer_state, 
       p.payment_type, p.payment_value
FROM olist_orders o
INNER JOIN olist_customers c ON o.customer_id = c.customer_id
INNER JOIN olist_order_payments p ON o.order_id = p.order_id
LIMIT 10;


-- 2. Delivered orders after 2018-01-01 with payment info (INNER JOIN)
SELECT o.order_id, o.order_delivered_customer_date, 
       p.payment_type, p.payment_value,
       r.review_score
FROM olist_orders o
INNER JOIN olist_order_payments p ON o.order_id = p.order_id
LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered' 
  AND o.order_delivered_customer_date > '2018-01-01'
ORDER BY o.order_delivered_customer_date ASC;


-- 3. Orders per status with % share (GROUP BY + subquery)
SELECT order_status, COUNT(*) AS total_orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS percentage_share
FROM olist_orders
GROUP BY order_status
ORDER BY total_orders DESC;

-- 4. Average payment per type with min/max values (aggregation)
SELECT payment_type, 
       AVG(payment_value) AS avg_payment,
       MIN(payment_value) AS min_payment,
       MAX(payment_value) AS max_payment
FROM olist_order_payments
GROUP BY payment_type
ORDER BY avg_payment DESC;

-- 5. First and last order per year (GROUP BY + MIN/MAX)
SELECT DATE_PART('year', order_purchase_timestamp) AS year,
       MIN(order_purchase_timestamp) AS first_order,
       MAX(order_purchase_timestamp) AS last_order
FROM olist_orders
GROUP BY year
ORDER BY year;

-- 6. Orders and customer states (LEFT JOIN: include orders without matching customers)
SELECT o.order_id, o.order_status, c.customer_state
FROM olist_orders o
LEFT JOIN olist_customers c ON o.customer_id = c.customer_id
LIMIT 15;

-- 7. Total orders per year (GROUP BY + COUNT)
SELECT DATE_PART('year', o.order_purchase_timestamp) AS year,
       COUNT(DISTINCT o.order_id) AS total_orders,
       SUM(oi.price) AS total_revenue,
       ROUND(AVG(p.payment_value), 2) AS avg_payment
FROM olist_orders o
JOIN olist_order_items oi ON o.order_id = oi.order_id
JOIN olist_order_payments p ON o.order_id = p.order_id
GROUP BY year
ORDER BY year;

-- 8. Average review score per product (INNER JOIN)
SELECT p.product_category_name,
       AVG(r.review_score) AS avg_score,
       COUNT(r.review_id) AS total_reviews,
       SUM(oi.price) AS total_revenue
FROM olist_order_items oi
INNER JOIN olist_order_reviews r ON oi.order_id = r.order_id
INNER JOIN olist_products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
HAVING COUNT(r.review_id) > 20
ORDER BY avg_score DESC
LIMIT 10;


-- 9. Top 10 states by number of customers (simple GROUP BY)
SELECT c.customer_state,
       COUNT(DISTINCT c.customer_id) AS total_customers,
       ROUND(AVG(r.review_score), 2) AS avg_review
FROM olist_customers c
JOIN olist_orders o ON c.customer_id = o.customer_id
LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id
GROUP BY c.customer_state
ORDER BY total_customers DESC
LIMIT 10;


-- 10. Payment value by installment count (with filtering)
SELECT payment_installments, ROUND(AVG(payment_value), 2) AS avg_payment, COUNT(*) AS num_payments
FROM olist_order_payments
WHERE payment_installments <= 12
GROUP BY payment_installments
ORDER BY payment_installments;

-- 11. Orders by delivery status (basic distribution)
SELECT order_status, COUNT(*) AS total
FROM olist_orders
GROUP BY order_status
ORDER BY total DESC;

-- 12. Average delivery time in days (only delivered)
SELECT ROUND(AVG(EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp))/86400), 2) AS avg_delivery_days
FROM olist_orders
WHERE order_status = 'delivered';

-- 13. Top 10 most sold products with total revenue (INNER JOIN)
SELECT oi.product_id,
       COUNT(*) AS total_sold,
       SUM(oi.price) AS revenue,
       SUM(oi.freight_value) AS total_freight
FROM olist_order_items oi
JOIN olist_orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY oi.product_id
ORDER BY total_sold DESC
LIMIT 10;


-- 14. Seller performance (LEFT JOIN: include sellers with no sales)
SELECT s.seller_id, 
       COALESCE(SUM(oi.price), 0) AS total_sales,
       COUNT(DISTINCT oi.order_id) AS total_orders,
       ROUND(AVG(r.review_score), 2) AS avg_review
FROM olist_sellers s
LEFT JOIN olist_order_items oi ON s.seller_id = oi.seller_id
LEFT JOIN olist_orders o ON oi.order_id = o.order_id
LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id
GROUP BY s.seller_id
ORDER BY total_sales DESC
LIMIT 10;


-- 15. Freight value per state (JOIN with customers)
SELECT c.customer_state, ROUND(AVG(oi.freight_value), 2) AS avg_freight
FROM olist_order_items oi
INNER JOIN olist_orders o ON oi.order_id = o.order_id
INNER JOIN olist_customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY avg_freight DESC;

-- 16. Reviews per score (distribution)
SELECT review_score, COUNT(*) AS review_count
FROM olist_order_reviews
GROUP BY review_score
ORDER BY review_score;

-- 17. Orders with and without reviews (FULL OUTER JOIN)
SELECT COUNT(o.order_id) FILTER (WHERE r.review_id IS NULL) AS orders_without_reviews,
       COUNT(o.order_id) FILTER (WHERE r.review_id IS NOT NULL) AS orders_with_reviews
FROM olist_orders o
FULL OUTER JOIN olist_order_reviews r ON o.order_id = r.order_id;

-- 18. Monthly sales trend (time series)
SELECT DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
       SUM(oi.price) AS total_sales,
       ROUND(AVG(r.review_score), 2) AS avg_review
FROM olist_orders o
JOIN olist_order_items oi ON o.order_id = oi.order_id
LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;
