import sqlite3

conn = sqlite3.connect('budget.db')
c = conn.cursor()

c.execute("SELECT * FROM entries")
rows = c.fetchall()

for row in rows:
    print(row)

conn.close()
