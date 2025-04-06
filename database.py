import sqlite3

# Database connection
conn = sqlite3.connect("hiresmart.db")
cursor = conn.cursor()

# Setup table with email field
cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        score REAL,
        email TEXT,
        shortlisted INTEGER DEFAULT 1
    )
""")
conn.commit()

def save_candidate(cv_id, score, email=""):
    """Saves a shortlisted candidate to the database."""
    cursor.execute("INSERT OR REPLACE INTO candidates (id, score, email) VALUES (?, ?, ?)", (cv_id, score, email))
    conn.commit()

def get_shortlisted_candidates():
    """Retrieves all shortlisted candidates."""
    cursor.execute("SELECT id, score, email FROM candidates WHERE shortlisted = 1")
    return cursor.fetchall()

def close_connection():
    """Closes the database connection."""
    conn.close()

# Example usage (for testing)
if __name__ == "_main_":
    save_candidate("C1061", 90.5, "alyssachavez88@gmail.com")
    candidates = get_shortlisted_candidates()
    print("Shortlisted:", candidates)
    close_connection()