import sqlite3
from datetime import datetime

DB_FILE = "chat_history.db"

def initialize_database():
    """Initialize the SQLite database and create tables if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_session_history(session_id: str):
    """Fetch the chat history for a given session ID."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_input, assistant_response FROM chat_history WHERE session_id = ? ORDER BY timestamp", (session_id,))
        return [(row[0], row[1]) for row in cursor.fetchall()]

def append_to_session_history(session_id: str, user_input: str, assistant_response: str):
    """Add a single interaction to the chat history."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (session_id, user_input, assistant_response) VALUES (?, ?, ?)",
            (session_id, user_input, assistant_response)
        )
        conn.commit()
