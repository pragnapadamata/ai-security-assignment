"""
Q3 - CSV Data Import to a Database (larger version)

Reads ../data/users.csv (124 rows, with some messy rows on purpose),
cleans and validates each row, and inserts the good ones into SQLite.

What it handles:
  - extra spaces in names, upper-case emails  -> cleaned
  - invalid emails or empty names             -> skipped and reported
  - same email twice                          -> stored only once (UNIQUE)

Usage:
    python q3_csv_import.py
    python q3_csv_import.py --csv my_users.csv --db library.db
"""

import argparse
import csv
import logging
import re
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("users")

DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "users.csv"
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = {"name", "email"} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {missing}")
        return list(reader)


def validate(rows: list[dict]) -> tuple[list[dict], list[tuple[int, str]]]:
    good, bad = [], []
    for line_no, row in enumerate(rows, start=2):  # line 1 is the header
        name = " ".join((row.get("name") or "").split())
        email = (row.get("email") or "").strip().lower()
        if not name:
            bad.append((line_no, "empty name"))
        elif not EMAIL_RE.match(email):
            bad.append((line_no, f"invalid email '{email}'"))
        else:
            good.append({"name": name, "email": email})
    return good, bad


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def insert_users(conn: sqlite3.Connection, users: list[dict]) -> int:
    before = conn.total_changes
    with conn:
        conn.executemany("INSERT OR IGNORE INTO users (name, email) VALUES (:name, :email)", users)
    return conn.total_changes - before


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--db", default="library.db")
    args = parser.parse_args()

    rows = read_csv(args.csv)
    good, bad = validate(rows)

    conn = sqlite3.connect(args.db)
    try:
        init_db(conn)
        inserted = insert_users(conn, good)
        total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        sample = conn.execute("SELECT name, email FROM users ORDER BY name LIMIT 10").fetchall()
    finally:
        conn.close()

    print(f"\nRows in CSV        : {len(rows)}")
    print(f"Valid rows         : {len(good)}")
    print(f"Skipped (invalid)  : {len(bad)}")
    print(f"Inserted (new)     : {inserted}")
    print(f"Duplicates ignored : {len(good) - inserted}")
    print(f"Total users in DB  : {total}")
    for line_no, reason in bad:
        print(f"  - line {line_no}: {reason}")
    print("\nFirst 10 users:")
    for name, email in sample:
        print(f"  {name:<20} {email}")


if __name__ == "__main__":
    main()
