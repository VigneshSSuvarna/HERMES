import os
import sqlite3

class HermesMemory:
    def __init__(self, db_name="hermes_matrix.db"):
        config_dir = "config"
        os.makedirs(config_dir, exist_ok=True)
        self.db_path = os.path.join(config_dir, db_name)
        self.initialize_database()

    def initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_telemetry (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()

    def append_interaction(self, role, text):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO chat_logs (role, message) VALUES (?, ?)", (role, text))
            conn.commit()

    def get_context_string(self, limit=15):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, message FROM (
                    SELECT id, role, message FROM chat_logs 
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
            """, (limit,))
            rows = cursor.fetchall()
            
        context = ""
        for role, msg in rows:
            role_label = "User" if role == "user" else "HERMES"
            context += f"{role_label}: {msg}\n"
        return context