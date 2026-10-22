import sqlite3
import pandas as pd

print("Creating a lightweight database for deployment...")
with sqlite3.connect("jobs.db") as con:
    # Export just the tables we need for the dashboard
    skills = pd.read_sql("SELECT * FROM skills", con)
    posting_skills = pd.read_sql("SELECT * FROM posting_skills", con)
    extractions = pd.read_sql("SELECT * FROM extractions", con)
    
# Save to a new, smaller database file
with sqlite3.connect("dashboard.db") as con:
    skills.to_sql("skills", con, index=False)
    posting_skills.to_sql("posting_skills", con, index=False)
    extractions.to_sql("extractions", con, index=False)

print("Created dashboard.db successfully!")