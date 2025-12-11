# app/db/init_db.py

import sqlite3
from pathlib import Path

# app/db/app.db
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"


def init_db():
    print(f"Creating SQLite DB at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Drop tables if re-running (for dev only)
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS orders")

    # Example USERS table
    cur.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            city TEXT,
            created_at TEXT
        )
        """
    )

    # Example ORDERS table
    cur.execute(
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    # Seed users
    users = [
        ("Alice", "alice@example.com", "Kyoto", "2025-01-01"),
        ("Bob", "bob@example.com", "Tokyo", "2025-01-05"),
        ("Charlie", "charlie@example.com", "Osaka", "2025-01-10"),
    ]
    cur.executemany(
        "INSERT INTO users (name, email, city, created_at) VALUES (?, ?, ?, ?)",
        users,
    )

    # Seed orders
    orders = [
        (1, 1999.0, "paid", "2025-02-01"),
        (1, 3499.5, "paid", "2025-02-10"),
        (2, 999.0, "pending", "2025-03-02"),
        (3, 12000.0, "paid", "2025-03-15"),
        (2, 4500.0, "refunded", "2025-03-20"),
    ]
    cur.executemany(
        "INSERT INTO orders (user_id, amount, status, created_at) VALUES (?, ?, ?, ?)",
        orders,
    )

    conn.commit()
    conn.close()
    print("DB initialized with sample data.")


if __name__ == "__main__":
    init_db()
