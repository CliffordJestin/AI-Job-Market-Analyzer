import sqlite3

conn = sqlite3.connect('jobs.db')
c = conn.cursor()

# Add location column
try:
    c.execute("ALTER TABLE jobs ADD COLUMN location TEXT;")
    print("✅ Added location column to jobs table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("⚠️ 'location' column already exists.")
    else:
        print(f"❌ Error adding location column: {e}")

# Add skills column
try:
    c.execute("ALTER TABLE jobs ADD COLUMN skills TEXT;")
    print("✅ Added skills column to jobs table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("⚠️ 'skills' column already exists.")
    else:
        print(f"❌ Error adding skills column: {e}")

# Commit and close
conn.commit()
conn.close()
