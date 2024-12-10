import sqlite3
import csv

CurrentPath = "/Users/javlonvaliyev/Desktop/Aisha/CompletedRAG/"
def save_job_application_to_csv(job_apply_result: dict, filename: str = CurrentPath+"job_applications.csv"):
    """
    Save the job application result to a CSV file.
    """
    headers = ["job_title", "full_name", "years_of_experience", "skills"]

    job_apply_result["skills"] = ", ".join(job_apply_result.get("skills", []))

    file_exists = False
    try:
        with open(filename, mode="r") as file:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        if not file_exists:
            writer.writeheader()

        writer.writerow(job_apply_result)



DB_FILE = CurrentPath + "chat_history.db"

def initialize_database():
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
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_input, assistant_response FROM chat_history WHERE session_id = ? ORDER BY timestamp", (session_id,))
        return [(row[0], row[1]) for row in cursor.fetchall()]

def append_to_session_history(session_id: str, user_input: str, assistant_response: str):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # print(f"Appending to DB - Session ID: {session_id}, User Input: {user_input}, Assistant Response: {assistant_response}")
            cursor.execute(
                "INSERT INTO chat_history (session_id, user_input, assistant_response) VALUES (?, ?, ?)",
                (session_id, user_input, assistant_response)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")