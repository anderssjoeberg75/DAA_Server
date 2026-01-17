import sqlite3
# Importera HISTORY_LIMIT här:
from config.settings import DB_PATH, HISTORY_LIMIT
import os

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO history (session_id, role, content, image) VALUES (?, ?, ?, ?)",
              (session_id, role, content, image))
    conn.commit()
    conn.close()

# Använd HISTORY_LIMIT som default-värde
def get_history(session_id, limit=HISTORY_LIMIT):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Hämtar de senaste 'limit' raderna
    c.execute(f"SELECT role, content, image FROM (SELECT * FROM history WHERE session_id = ? ORDER BY id DESC LIMIT {limit}) ORDER BY id ASC", (session_id,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        msg = {"role": row["role"], "content": row["content"]}
        if row["image"]: msg["image"] = row["image"]
        history.append(msg)
    return history