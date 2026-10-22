import requests, json, sqlite3
from datetime import datetime, timezone

def fetch_all(pages=10):
    all_jobs = []
    for page in range(1, pages + 1):
        r = requests.get(
            "https://www.arbeitnow.com/api/job-board-api",
            params={"page": page},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json().get("data", [])
        if not data:
            break
        all_jobs.extend(data)
        print(f"page {page}: +{len(data)} (total {len(all_jobs)})")
    return all_jobs

def save_raw(jobs):
    with sqlite3.connect("jobs.db") as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS raw_postings (
                source TEXT, source_id TEXT, fetched_at TEXT, raw_json TEXT,
                PRIMARY KEY (source, source_id)
            )
        """)
        now = datetime.now(timezone.utc).isoformat()
        for j in jobs:
            con.execute(
                "INSERT OR IGNORE INTO raw_postings VALUES (?,?,?,?)",
                ("arbeitnow", j.get("slug") or j.get("url"), now, json.dumps(j)),
            )
    print(f"saved {len(jobs)} raw postings")

if __name__ == "__main__":
    save_raw(fetch_all(pages=10))