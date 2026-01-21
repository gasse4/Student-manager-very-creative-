import sqlite3
import os

DB_NAME = "student_manager.db"


class UniversityDB:
    """Manages SQLite database connections and initialization."""
    
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """Initialize database schema with tables for users, courses, and enrollments."""
        self.cursor.execute("PRAGMA foreign_keys = ON")
        # self.cursor.execute("PRAGMA journal_mode = WAL")
        # self.cursor.execute("PRAGMA synchronous = NORMAL")
        # self.cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache
        # self.cursor.execute("PRAGMA temp_store = MEMORY")
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            u_uuid TEXT PRIMARY KEY,
            custom_id TEXT UNIQUE NOT NULL, 
            name TEXT NOT NULL, 
            role TEXT NOT NULL)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
            code TEXT PRIMARY KEY, 
            name TEXT NOT NULL)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS enrollments (
            user_uuid TEXT, 
            course_code TEXT, 
            PRIMARY KEY(user_uuid, course_code),
            FOREIGN KEY(user_uuid) REFERENCES users(u_uuid),
            FOREIGN KEY(course_code) REFERENCES courses(code))''')
        
        self.conn.commit()

    def execute_query(self, query: str):
        """Execute a SELECT query and return results."""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def execute_single(self, query: str):
        """Execute a SELECT query and return a single row."""
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def execute_update(self, query: str) -> bool:
        """Execute an INSERT/UPDATE/DELETE query."""
        try:
            self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception:
            return False

    def rollback(self):
        """Rollback the current transaction."""
        self.conn.rollback()

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()