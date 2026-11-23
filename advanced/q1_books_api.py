"""
Q1 - API Data Retrieval and Storage (larger version)

Fetches books from a REST API, validates them, stores them in SQLite
without duplicates, and prints a neat table with a few stats.

If the API is not reachable, it falls back to ../data/books.json (60 books),
so the script always runs.

Usage:
    python q1_books_api.py
    python q1_books_api.py --api-url https://your-api/books --db library.db
"""

import argparse
import json
import logging
import sqlite3
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("books")

DEFAULT_API = "https://example.com/api/books"
FALLBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "books.json"


def make_session() -> requests.Session:
    """Session that retries a few times on network / server errors."""
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


def fetch_books(api_url: str) -> list[dict]:
    try:
        resp = make_session().get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        log.info("Fetched %d books from API", len(data))
        return data
    except (requests.RequestException, ValueError) as e:
        log.warning("API not reachable (%s). Using %s", e.__class__.__name__, FALLBACK_FILE.name)
        return json.loads(FALLBACK_FILE.read_text())


def clean_book(raw: dict) -> dict | None:
    """Accepts 'year' or 'publication_year'. Skips broken records."""
    title = str(raw.get("title", "")).strip()
    author = str(raw.get("author", "")).strip()
    year = raw.get("publication_year", raw.get("year"))
    if not title or not author:
        return None
    try:
        year = int(year) if year is not None else None
    except (TypeError, ValueError):
        year = None
    return {"title": title, "author": author, "year": year}


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            title  TEXT NOT NULL,
            author TEXT NOT NULL,
            year   INTEGER,
            UNIQUE(title, author)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_books_year ON books(year)")


def save_books(conn: sqlite3.Connection, books: list[dict]) -> int:
    before = conn.total_changes
    with conn:  # one transaction
        conn.executemany(
            "INSERT OR IGNORE INTO books (title, author, year) VALUES (:title, :author, :year)",
            books,
        )
    return conn.total_changes - before


def show_books(conn: sqlite3.Connection, limit: int = 20) -> None:
    rows = conn.execute(
        "SELECT id, title, author, year FROM books ORDER BY year DESC LIMIT ?", (limit,)
    ).fetchall()
    print(f"\n{'ID':<5}{'Title':<22}{'Author':<22}{'Year':<6}")
    print("-" * 55)
    for r in rows:
        print(f"{r[0]:<5}{r[1][:20]:<22}{r[2][:20]:<22}{r[3] or '-':<6}")

    total, oldest, newest = conn.execute("SELECT COUNT(*), MIN(year), MAX(year) FROM books").fetchone()
    print(f"\nTotal books: {total} | Oldest: {oldest} | Newest: {newest}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch books from an API into SQLite")
    parser.add_argument("--api-url", default=DEFAULT_API)
    parser.add_argument("--db", default="library.db")
    args = parser.parse_args()

    raw_books = fetch_books(args.api_url)
    books = [b for b in (clean_book(r) for r in raw_books) if b]
    log.info("%d valid, %d skipped", len(books), len(raw_books) - len(books))

    conn = sqlite3.connect(args.db)
    try:
        init_db(conn)
        inserted = save_books(conn, books)
        log.info("Inserted %d new books (duplicates ignored)", inserted)
        show_books(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
