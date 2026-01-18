import sqlite3
import os
from config.settings import DB_PATH, HISTORY_LIMIT

def init_db():
    """Skapar databasen och tabellen om de inte finns."""
    try:
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
        print(f"✅ Databas initierad: {DB_PATH}")
    except Exception as e:
        print(f"❌ Databasfel vid initiering: {e}")

def save_message(session_id, role, content, image=None):
    """Sparar ett meddelande i historiken."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO history (session_id, role, content, image) VALUES (?, ?, ?, ?)",
                  (session_id, role, content, image))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Kunde inte spara till DB: {e}")

def get_history(session_id=None, limit=HISTORY_LIMIT):
    """
    Hämtar konversationshistorik.
    OBS: Ignorerar session_id för att ge 'globalt minne' över alla sessioner.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Hämtar de senaste 'limit' raderna från HELA historiken (oavsett session)
        # Vi sorterar DESC för att få de senaste, och sen ASC för att få dem i rätt tidsordning.
        query = f"""
            SELECT role, content, image 
            FROM (
                SELECT * FROM history 
                ORDER BY id DESC 
                LIMIT ?
            ) 
            ORDER BY id ASC
        """
        
        c.execute(query, (limit,))
        rows = c.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            msg = {"role": row["role"], "content": row["content"]}
            # Inkludera bild om det finns (för framtida bruk)
            if row["image"]: 
                msg["image"] = row["image"]
            history.append(msg)
            
        return history
    except Exception as e:
        print(f"⚠️ Kunde inte hämta historik: {e}")
        return []