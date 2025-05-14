import sqlite3
from datetime import datetime

DB_NAME = "messages.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_message(message_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (id, time) VALUES (?, ?)", (message_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_messages():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, time FROM messages")
    rows = c.fetchall()
    conn.close()
    return [{'id': row[0], 'time': row[1]} for row in rows]

def delete_message(message_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()
