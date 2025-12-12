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

    
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT,
            dob TEXT,
            email TEXT,
            metadata_json TEXT
        )
        """
    )

    # 🔹 ONE BIG SUMMARY FIELD
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clinical_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            summary_text TEXT NOT NULL,      
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
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


    # Sample medical data:
    sample_customers = [
        {
            "id": "CUST_001",
            "name": "Rahul Sharma",
            "dob": "1992-03-15",
            "email": "rahul@example.com",
            "metadata_json": '{"gender": "M", "blood_group": "B+"}',
        },
        {
            "id": "CUST_002",
            "name": "Ananya Singh",
            "dob": "1988-11-02",
            "email": "ananya@example.com",
            "metadata_json": '{"gender": "F", "blood_group": "O-"}',
        },
    ]

    sample_summaries = [
        {
            "customer_id": "CUST_001",
            "summary_text": """
Rahul Sharma (DOB: 1992-03-15) – Ongoing clinical summary:

- Primary diagnoses: Type 2 Diabetes Mellitus (diagnosed 2023), Essential Hypertension (diagnosed 2022).
- Recent visit date: 2025-11-20.
- Blood sugar: generally stable with minor post-prandial spikes. No episodes of severe hypoglycemia reported.
- Blood pressure: mildly elevated at last visit (~138/88 mmHg), better than 6 months ago.

Medications:
- Metformin 500 mg twice daily with meals.
- Amlodipine 5 mg once daily in the morning.

Lifestyle & adherence:
- Walks 30–40 minutes on most days, but inconsistent on weekends.
- Following a reduced-sugar diet but still consumes refined carbs 3–4 times/week.
- Adherent to medications >90% of the time by self-report.

Doctor’s recent guidance (2025-11-20):
- Continue the same medications and daily walking.
- Target: weight reduction of 3–4 kg over 3 months.
- Monitor fasting blood sugar at home twice weekly.
- Return for follow-up in 3 months or earlier if dizziness, chest pain, or visual changes occur.

No current red-flag symptoms (chest pain, severe shortness of breath, confusion, or persistent vision loss) reported.
            """.strip(),
        },
        {
            "customer_id": "CUST_002",
            "summary_text": """
Ananya Singh (DOB: 1988-11-02) – Ongoing clinical summary:

- Primary issue: Post-operative recovery after right knee arthroscopic surgery (2025-08).
- Current status (visit 2025-10-01): recovering well, mild pain after prolonged walking or stairs.

Rehab & medications:
- Physiotherapy sessions 3x/week focusing on range of motion and quadriceps strengthening.
- Uses short-acting pain medication only on days with intense physio or long walks.

Doctor’s recent guidance (2025-10-01):
- Continue physiotherapy for another 6–8 weeks.
- Avoid high-impact activity (running, jumping, sports) until cleared by orthopaedic review.
- Recommended low-impact activities such as cycling and swimming once pain permits.

No signs of infection (fever, redness, warmth, severe swelling) at the surgical site reported.
            """.strip(),
        },
    ]

    for c in sample_customers:
        cur.execute(
            """
            INSERT OR IGNORE INTO customers (id, name, dob, email, metadata_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (c["id"], c["name"], c["dob"], c["email"], c["metadata_json"]),
        )

    for s in sample_summaries:
        cur.execute(
            """
            INSERT INTO clinical_summaries (customer_id, summary_text)
            VALUES (?, ?)
            """,
            (s["customer_id"], s["summary_text"]),
        )


    conn.commit()
    conn.close()
    print("DB initialized with sample data.")


if __name__ == "__main__":
    init_db()
