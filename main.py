import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
import re

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

        for col in df.columns:
            if "id" in col.lower():
                df = df.drop(columns=[col])

        return df
    except Exception as e:
        print("Error:", e)
        return None


def load_queries(filename="queries.sql"):
    """Read queries from a .sql file and split them by semicolon, ignoring comments."""
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r"--.*", "", content)

    queries = [q.strip() for q in content.split(";") if q.strip()]
    return queries


if __name__ == "__main__":
    print("Connected to PostgreSQL database:", DB_NAME)

    queries = load_queries("queries.sql")

    for i, query in enumerate(queries, 1):
        print(f"\n=== Query {i} Results ===")
        df = run_query(query)
        if df is not None:
            print(df.head(20))  
