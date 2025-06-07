# db_utils.py

import sqlite3

def create_database(drop_existing=False):
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()

    if drop_existing:
        c.execute("DROP TABLE IF EXISTS jobs;")
        print("🗑️ Dropped existing 'jobs' table.")

    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            experience TEXT,
            salary TEXT,
            location TEXT,
            description TEXT,
            url TEXT UNIQUE,
            role TEXT,
            skills TEXT
        );
    """)
    print("✅ 'jobs' table created.")

    conn.commit()
    conn.close()

def insert_job(job_data):
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()

    try:
        c.execute("""
            INSERT OR IGNORE INTO jobs (title, company, experience, salary, location, description, url, role, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            job_data["title"],
            job_data["company"],
            job_data["experience"],
            job_data["salary"],
            job_data["location"],
            job_data["description"],
            job_data["url"],
            job_data["role"],
            job_data["skills"]
        ))
        conn.commit()
    except Exception as e:
        print(f"❌ Error inserting job: {e}")
    finally:
        conn.close()
