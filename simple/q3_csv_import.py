import csv
import sqlite3

# Step 1: read the users from the CSV file
users = []
with open("users.csv") as file:
    reader = csv.DictReader(file)
    for row in reader:
        users.append(row)

# Step 2: save the users in SQLite
conn = sqlite3.connect("library.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, email TEXT)")

for user in users:
    cur.execute("INSERT INTO users VALUES (?, ?)",
                (user["name"], user["email"]))
conn.commit()

# Step 3: show the users
print("Users in the database:")
for row in cur.execute("SELECT * FROM users"):
    print(row[0], "-", row[1])

conn.close()
