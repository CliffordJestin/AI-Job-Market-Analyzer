import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

df=pd.read_csv("cleaned_jobs.csv")

print("\n📊 Experience (years):")
print(df['years_exp'].describe())
print(f"\nMissing experience values: {df['years_exp'].isna().sum()}")

print("\n📊 Salary (average):")
print(df['avg_salary'].describe())


df_skills = df['clean_skills'].dropna().str.split(',').explode().str.strip()
df_skills = df['clean_skills'].dropna().str.split(',').explode().str.strip()
df_skills = df_skills[df_skills != "N/A"]
df_skills = df_skills[df_skills != ""]

# Optionally make all skills Title Case (some listings mix case)
df_skills = df_skills.str.title()


# Remove "N/A" and empty strings
df_skills = df_skills[df_skills != "N/A"]
df_skills = df_skills[df_skills != ""]

# --- Top N skills ---
top_n = 15
top_skills_counts = df_skills.value_counts().head(top_n)

# --- Print info ---
print(f"\n🔍 Total unique skills: {df_skills.nunique()}")
print(f"\nTop {top_n} skills:\n")
print(top_skills_counts)

# --- Save cleaned data to CSV ---
df.to_csv("cleaned_jobs.csv", index=False)
print("✅ Cleaned data saved to cleaned_jobs.csv")

# FINAL cleaned dataset (for dashboard)
df.to_csv("final_cleaned_jobs.csv", index=False)
print("✅ Final cleaned data saved to final_cleaned_jobs.csv")
