import sqlite3


def initialize_database(path: str):
    with sqlite3.connect(path+"/chat_history.db") as conn:
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

def get_session_history(session_id: str, path: str):
    with sqlite3.connect(path+"/chat_history.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_input, assistant_response FROM chat_history WHERE session_id = ? ORDER BY timestamp", (session_id,))
        return [(row[0], row[1]) for row in cursor.fetchall()]

def append_to_session_history(session_id: str, user_input: str, assistant_response: str, path: str):
    try:
        with sqlite3.connect(path+"/chat_history.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (session_id, user_input, assistant_response) VALUES (?, ?, ?)",
                (session_id, user_input, assistant_response)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def close_database_connection(connection):
    """
    Safely close a database connection.
    
    Args:
        connection: SQLite database connection object
    """
    try:
        if connection:
            connection.close()
            print("Database connection closed successfully")
    except sqlite3.Error as e:
        print(f"Error closing database connection: {e}")