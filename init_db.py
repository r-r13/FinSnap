import sqlite3

conn = sqlite3.connect('budget.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_type TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        notes TEXT
    )
''')

conn.commit()
conn.close()

print("Database and table created successfully.")
