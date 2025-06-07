import sqlite3
import pandas as pd

# Connect to your database
conn = sqlite3.connect("jobs.db")

# Load some rows
df = pd.read_sql_query("SELECT * FROM jobs LIMIT 10", conn)

# Show the output
print(df)

conn.close()
