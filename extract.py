import sqlite3
import re

# 1. Define the skills we want to look for (and their variations)
SKILL_MAP = {
    "Python": ["python"],
    "SQL": ["sql", "mysql", "postgresql", "sqlite"],
    "Excel": ["excel", "vlookup", "pivot table"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "R": ["r programming", " r,", " r."],
    "Java": ["java"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "Machine Learning": ["machine learning", "ml"],
    "Data Analysis": ["data analysis", "data analyst"],
    "Git": ["git", "github"],
    "Docker": ["docker"],
    "JavaScript": ["javascript", "js"],
    "C++": ["c++"],
    "Pandas": ["pandas"],
    "Scikit-Learn": ["scikit-learn", "sklearn"],
    "ETL": ["etl", "extract transform load"],
    "SAP": ["sap"],
    "Salesforce": ["salesforce"]
}

def extract_skills(text):
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for canonical, variations in SKILL_MAP.items():
        for var in variations:
            # Look for the exact word to avoid false positives (e.g., "r" in "your")
            pattern = r'\b' + re.escape(var) + r'\b'
            if re.search(pattern, text_lower):
                found.append(canonical)
                break # Move to the next skill if found
    return found

def guess_seniority(text):
    if not text: return "unknown"
    text_lower = text.lower()
    if "senior" in text_lower or "lead" in text_lower or "principal" in text_lower:
        return "senior"
    if "junior" in text_lower or "intern" in text_lower or "graduate" in text_lower:
        return "junior"
    return "mid/unknown"

print("Starting rule-based extraction...")

with sqlite3.connect("jobs.db") as con:
    # Create tables
    con.execute("CREATE TABLE IF NOT EXISTS extractions (posting_id TEXT PRIMARY KEY, seniority TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS skills (skill_id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    con.execute("CREATE TABLE IF NOT EXISTS posting_skills (posting_id TEXT, skill_id INTEGER, PRIMARY KEY (posting_id, skill_id))")
    
    # Get all postings
    rows = con.execute("SELECT posting_id, clean_text FROM postings").fetchall()
    print(f"Processing {len(rows)} postings...")
    
    for pid, text in rows:
        # Extract seniority
        seniority = guess_seniority(text)
        con.execute("INSERT OR REPLACE INTO extractions (posting_id, seniority) VALUES (?, ?)", (pid, seniority))
        
        # Extract skills
        skills = extract_skills(text)
        for skill in skills:
            con.execute("INSERT OR IGNORE INTO skills(name) VALUES (?)", (skill,))
            sid = con.execute("SELECT skill_id FROM skills WHERE name=?", (skill,)).fetchone()[0]
            con.execute("INSERT OR IGNORE INTO posting_skills VALUES (?,?)", (pid, sid))
            
    con.commit()
print("Extraction complete! Data is ready.")

# ---------------------------------------------------------
# RUN THE ANALYSIS RIGHT NOW
# ---------------------------------------------------------
print("\n--- TOP 10 SKILLS ---")
with sqlite3.connect("jobs.db") as con:
    results = con.execute("""
        SELECT s.name, COUNT(DISTINCT ps.posting_id) as n
        FROM posting_skills ps
        JOIN skills s USING(skill_id)
        GROUP BY s.name
        ORDER BY n DESC
        LIMIT 10
    """).fetchall()
    for rank, (skill, count) in enumerate(results, 1):
        print(f"{rank}. {skill}: {count} postings")

print("\n--- SENIORITY MIX ---")
with sqlite3.connect("jobs.db") as con:
    results = con.execute("SELECT seniority, COUNT(*) FROM extractions GROUP BY 1 ORDER BY 2 DESC").fetchall()
    for sen, count in results:
        print(f"{sen}: {count} postings")