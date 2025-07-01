import pandas as pd

# Load the cleaned job data
df = pd.read_csv("cleaned_jobs.csv")

# Drop rows with missing salary
salary_df = df[df['avg_salary'].notna()].copy()

# Show basic salary stats
print("🔍 Salary Summary (in ₹):")
print(salary_df['posted_date_cleaned'].describe())

# Convert to LPA for average display


# Show top 10 rows with role and salary
print("\n🧪 Sample Jobs with Salary:")
print(salary_df[['role', 'posted_date_cleaned']].head(10))
