import sqlite3

conn = sqlite3.connect("geo.db")

conn.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        run_at        TEXT    NOT NULL,
        business      TEXT    NOT NULL,
        hits          INTEGER NOT NULL,
        total_queries INTEGER NOT NULL
    )
""")

conn.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at  TEXT    NOT NULL,
        name        TEXT,
        email       TEXT    NOT NULL,
        business    TEXT,
        score       TEXT
    )
""")

conn.commit()

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables in geo.db:", tables)

conn.close()