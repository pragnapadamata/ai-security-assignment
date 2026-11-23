import requests
import sqlite3

# Step 1: get the books from the API
response = requests.get("https://example.com/api/books")
books = response.json()

# books look like this:
# [{"title": "The Shadow", "author": "Pragna", "year": 2026},
#  {"title": "Do or Die", "author": "Manogna", "year": 2025}]

# Step 2: save the books in SQLite
conn = sqlite3.connect("library.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS books (title TEXT, author TEXT, year INTEGER)")

for book in books:
    cur.execute("INSERT INTO books VALUES (?, ?, ?)",
                (book["title"], book["author"], book["year"]))
conn.commit()

# Step 3: show the books
print("Hi Mia and Sia, here are the books:")
for row in cur.execute("SELECT * FROM books"):
    print(row[0], "by", row[1], "-", row[2])

conn.close()
