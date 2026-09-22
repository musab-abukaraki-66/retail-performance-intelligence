"""Loads the generated CSVs into a local SQLite database for SQL analysis.

Usage:
    python src/load_db.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/retail.db")


def main() -> None:
    customers = pd.read_csv("data/customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv("data/products.csv")
    orders = pd.read_csv("data/orders.csv", parse_dates=["order_date"])

    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_PATH)
    customers.to_sql("customers", conn, index=False)
    products.to_sql("products", conn, index=False)
    orders.to_sql("orders", conn, index=False)

    conn.execute("CREATE INDEX idx_orders_date ON orders(order_date)")
    conn.execute("CREATE INDEX idx_orders_region ON orders(region)")
    conn.execute("CREATE INDEX idx_orders_category ON orders(category)")
    conn.commit()
    conn.close()
    print(f"Loaded {len(orders):,} orders, {len(customers):,} customers, {len(products):,} products -> {DB_PATH}")


if __name__ == "__main__":
    main()
