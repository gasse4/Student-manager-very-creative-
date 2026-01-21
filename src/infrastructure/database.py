# database.py
import sqlite3
import os

DB_NAME = "student_manager.db"

class UniversityDB:
    """Manages SQLite database connections with optimized settings for concurrency and performance."""

    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """Initialize schema with foreign keys and essential indexes."""
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.cursor.execute("PRAGMA journal_mode = WAL")
        self.cursor.execute("PRAGMA synchronous = NORMAL")
        self.cursor.execute("PRAGMA cache_size = -2000")  
        self.cursor.execute("PRAGMA temp_store = MEMORY")

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                u_uuid BLOB PRIMARY KEY,
                custom_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                user_uuid BLOB,
                course_code TEXT,
                PRIMARY KEY(user_uuid, course_code),
                FOREIGN KEY(user_uuid) REFERENCES users(u_uuid) ON DELETE CASCADE,
                FOREIGN KEY(course_code) REFERENCES courses(code) ON DELETE CASCADE
            )
        ''')

        # Essential indexes only
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_users_custom_id ON users(custom_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_user ON enrollments(user_uuid)")

        self.conn.commit()

    def execute_query(self, query: str, params: tuple = ()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_single(self, query: str, params: tuple = ()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()