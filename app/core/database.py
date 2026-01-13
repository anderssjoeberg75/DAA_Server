import sqlite3
from config.settings import DB_PATH

def init_db():
    """Initializes the SQLite database table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Schema supports text content and base64 images
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            image TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")

def save_message(session_id, role, content, image=None):
    """Saves a single message to the history table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO history (session_id, role, content, image) VALUES (?, ?, ?, ?)",
              (session_id, role, content, image))
    conn.commit()
    conn.close()

def get_history(session_id, limit=60):
    """Fetches recent conversation history."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = f"SELECT role, content, image FROM (SELECT * FROM history WHERE session_id = ? ORDER BY id DESC LIMIT {limit}) ORDER BY id ASC"
    c.execute(query, (session_id,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        msg = {"role": row["role"], "content": row["content"]}
        if row["image"]:
            msg["image"] = row["image"]
        history.append(msg)
    return history
