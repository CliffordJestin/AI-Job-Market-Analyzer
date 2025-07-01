# cleaned_jobs.py

import sqlite3
import pandas as pd
import re
from datetime import datetime, timedelta

# Connect to DB and load data
conn = sqlite3.connect("jobs.db")
df = pd.read_sql_query("SELECT * FROM jobs", conn)

def normalize_posted_date(p):
    if pd.isna(p) or str(p).strip() == "":
        return None

    today = datetime.today()
    p = str(p).lower()

    if 'today' in p:
        return today.date()
    elif 'yesterday' in p:
        return (today - timedelta(days=1)).date()
    elif 'day' in p:
        match = re.search(r'(\d+)', p)
        if match:
            return (today - timedelta(days=int(match.group(1)))).date()
    elif 'week' in p:
        match = re.search(r'(\d+)', p)
        if match:
            return (today - timedelta(weeks=int(match.group(1)))).date()
        elif '3+' in p:
            return (today - timedelta(weeks=3)).date()
    return None

if 'posted_date' in df.columns:
    df['posted_date_cleaned'] = df['posted_date'].apply(normalize_posted_date)
else:
    print("⚠️ 'posted_date' column not found. Skipping date normalization.")


# --- Clean Salary Column ---
def parse_salary(s):
    if not s or "Not" in s or "disclosed" in s.lower():
        return None, None, None

    s = s.replace(",", "").lower()

    multiplier = 1
    if "lakh" in s or "lac" in s or "lpa" in s:
        multiplier = 100000
    elif "thousand" in s or "k" in s:
        multiplier = 1000
    elif "cr" in s or "crore" in s:
        multiplier = 10000000

    match = re.findall(r'(\d+(?:\.\d+)?)', s)
    if len(match) >= 2:
        min_sal = float(match[0]) * multiplier
        max_sal = float(match[1]) * multiplier
        avg_sal = (min_sal + max_sal) / 2
        return int(min_sal), int(max_sal), int(avg_sal)
    elif len(match) == 1:
        sal = float(match[0]) * multiplier
        return int(sal), int(sal), int(sal)

    return None, None, None






df[['min_salary', 'max_salary', 'avg_salary']] = df['salary'].apply(
    lambda x: pd.Series(parse_salary(x))
)


# --- Clean Experience Column ---
def parse_experience(e):
    if not e or "fresher" in e.lower():
        return 0
    match = re.findall(r'(\d+)', e)
    if len(match) == 2:
        return (int(match[0]) + int(match[1])) / 2
    elif len(match) == 1:
        return int(match[0])
    return None


df['years_exp'] = df['experience'].apply(parse_experience)


# --- Clean Location Column ---
def clean_location(loc):
    if not loc or pd.isna(loc):
        return "N/A"

    loc = re.sub(r'Jobs in\s*', '', loc, flags=re.I).strip()
    loc = loc.replace("India", "").strip(", ")

    known_cities = ['Delhi', 'Mumbai', 'Pune', 'Bengaluru', 'Chennai', 'Hyderabad', 'Noida', 'Jaipur', 'Lucknow',
                    'Ranchi', 'Thiruvananthapuram', 'Udaipur', 'Mohali', 'Roorkee', 'Coimbatore', 'Ahmedabad', 'Indore', 'Surat',
                    'Kochi', 'Gurugram', 'Remote']
    loc_lower = loc.lower()

    # Check for Remote first
    if 'remote' in loc_lower:
        return 'Remote'

    # Extract known cities found in loc string
    found = []
    for city in known_cities:
        if city.lower() in loc_lower:
            found.append(city)

    if found:
        # Remove duplicates and join by comma
        found = sorted(set(found))
        return ', '.join(found)
    else:
        # fallback: return original cleaned loc if nothing matches
        return loc


df['clean_location'] = df['location'].apply(clean_location)


# --- Clean Skills Column ---
def clean_skills(skills_str):
    if not skills_str or pd.isna(skills_str) or skills_str.strip().lower() == 'n/a':
        return ""

    skills_list = [s.strip() for s in skills_str.split(',')]
    skills_list = [s for s in skills_list if s]
    skills_list = [s.title() for s in skills_list]

    seen = set()
    skills_cleaned = []
    for s in skills_list:
        if s not in seen:
            seen.add(s)
            skills_cleaned.append(s)

    return ', '.join(skills_cleaned)


df['clean_skills'] = df['skills'].apply(clean_skills)

# --- Save cleaned data to CSV ---
df.to_csv("cleaned_jobs.csv", index=False)
print("✅ Cleaned data saved to cleaned_jobs.csv")
