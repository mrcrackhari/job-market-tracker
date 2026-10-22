import sqlite3, json, re, html

def clean(s):
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)      # strip HTML tags
    s = re.sub(r"\s+", " ", s).strip()  # normalise whitespace
    return s

with sqlite3.connect("jobs.db") as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS postings (
            posting_id TEXT PRIMARY KEY, source TEXT, title TEXT,
            company TEXT, city TEXT, country TEXT, posted_at TEXT,
            clean_text TEXT
        )
    """)
    rows = con.execute("SELECT source_id, raw_json FROM raw_postings").fetchall()
    for pid, raw in rows:
        j = json.loads(raw)
        con.execute(
            "INSERT OR IGNORE INTO postings VALUES (?,?,?,?,?,?,?,?)",
            (pid, "arbeitnow", j.get("title"), j.get("company_name"),
             j.get("location"), "DE", j.get("created_at"),
             clean(j.get("description", ""))),
        )
    n = con.execute("SELECT COUNT(*) FROM postings").fetchone()[0]
    print(f"postings table: {n} rows")