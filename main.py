import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def run_query(query):
    """Execute a SQL query and return results as a pandas DataFrame."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("Error:", e)
        return None


if __name__ == "__main__":
    print("Connected to PostgreSQL database:", DB_NAME)

    query1 = "SELECT * FROM olist_orders LIMIT 10;"
    print("\n=== First 10 Orders ===")
    print(run_query(query1))

    query2 = """
    SELECT order_status, COUNT(*) AS total_orders
    FROM olist_orders
    GROUP BY order_status
    ORDER BY total_orders DESC;
    """
    print("\nOrders by status")
    print(run_query(query2))

    query3 = """
    SELECT oi.product_id, AVG(r.review_score) AS avg_score
    FROM olist_order_items oi
    JOIN olist_order_reviews r ON oi.order_id = r.order_id
    GROUP BY oi.product_id
    ORDER BY avg_score DESC
    LIMIT 5;
    """
    print("\nTop 5 Products by average review score")
    print(run_query(query3))
