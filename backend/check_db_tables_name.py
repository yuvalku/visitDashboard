import sqlite3

DB_PATH = "data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:", tables)
cursor.execute("PRAGMA table_info(data);")
columns = cursor.fetchall()

print("Columns in 'data':")
for col in columns:
    print(col)

conn.close()
