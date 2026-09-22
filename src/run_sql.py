"""Executes every query in sql/ against data/retail.db and prints results.

Used to produce the verified query outputs quoted in reports/findings.md —
every number in this project's README is copy-pasted from this script's
actual output, not hand-written.

Usage:
    python src/run_sql.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/retail.db")
SQL_DIR = Path("sql")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        print(f"\n{'=' * 70}\n{sql_file.name}\n{'=' * 70}")
        query = sql_file.read_text()
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))
    conn.close()


if __name__ == "__main__":
    main()
