import sqlite3
from flask import g

def get_db():
    """Gets a database connection for the current thread."""
    if 'db' not in g:
        g.db = sqlite3.connect("hiresmart.db", check_same_thread=False)  # Allow cross-thread usage
        g.db.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id TEXT PRIMARY KEY,
                score REAL,
                email TEXT,
                shortlisted INTEGER DEFAULT 1
            )
        """)
        g.db.commit()
    return g.db

def save_candidate(cv_id, score, email=""):
    """Saves a shortlisted candidate to the database."""
    db = get_db()
    db.execute("INSERT OR REPLACE INTO candidates (id, score, email) VALUES (?, ?, ?)", (cv_id, score, email))
    db.commit()

def get_shortlisted_candidates():
    """Retrieves all shortlisted candidates."""
    db = get_db()
    return db.execute("SELECT id, score, email FROM candidates WHERE shortlisted = 1").fetchall()

def close_connection():
    """Closes the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Example usage (for testing)
if __name__ == "_main_":
    save_candidate("C1061", 90.5, "alyssachavez88@gmail.com")
    candidates = get_shortlisted_candidates()
    print("Shortlisted:", candidates)
    close_connection()