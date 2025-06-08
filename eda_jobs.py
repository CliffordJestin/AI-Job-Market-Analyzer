import pandas as pd

# Load your data
df = pd.read_csv('final_cleaned_jobs.csv')

# Prepare skills column (handle missing values)
df['clean_skills'] = df['clean_skills'].fillna('').astype(str)

# Only consider rows with salary info
df_with_salary = df[df['avg_salary'].notna()].copy()

# Explode the skills column to one skill per row
df_with_salary_exploded = df_with_salary.assign(clean_skills=df_with_salary['clean_skills'].str.split(','))
df_with_salary_exploded = df_with_salary_exploded.explode('clean_skills')
df_with_salary_exploded['clean_skills'] = df_with_salary_exploded['clean_skills'].str.strip()

# Drop empty skills
df_with_salary_exploded = df_with_salary_exploded[df_with_salary_exploded['clean_skills'] != '']

# Now get count of jobs with salary info per skill
skill_salary_counts = df_with_salary_exploded['clean_skills'].value_counts().reset_index()
skill_salary_counts.columns = ['Skill', 'Jobs_with_Salary_Info']

# Show top skills with salary info
print(skill_salary_counts.head(20))

# Optional: Save to CSV to analyze in more detail
# skill_salary_counts.to_csv('skills_with_salary_info.csv', index=False)
