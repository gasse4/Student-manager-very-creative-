import sqlite3
import uuid
from .database import UniversityDB

class UserRepository:
    def __init__(self, db: UniversityDB):
        self.db = db

    def get_user_by_custom_id(self, custom_id: str):
        return self.db.execute_single(
            "SELECT * FROM users WHERE custom_id = ?", (custom_id,)
        )

    def get_user_by_uuid(self, u_uuid: bytes):
        return self.db.execute_single(
            "SELECT * FROM users WHERE u_uuid = ?", (u_uuid,)
        )

    def register_user(self, name: str, role: str, custom_id: str):
        u_uuid = uuid.uuid4().bytes
        success = self.db.execute_update(
            "INSERT INTO users (u_uuid, custom_id, name, role) VALUES (?, ?, ?, ?)",
            (u_uuid, custom_id, name, role)
        )
        return u_uuid if success else None

    def get_all_users(self):
        return self.db.execute_query("SELECT * FROM users")


class CourseRepository:
    def __init__(self, db: UniversityDB):
        self.db = db

    def add_course(self, code: str, name: str) -> bool:
        return self.db.execute_update(
            "INSERT INTO courses (code, name) VALUES (?, ?)", (code, name)
        )

    def get_all_courses(self):
        return self.db.execute_query("SELECT * FROM courses")

    def get_course_by_code(self, code: str):
        return self.db.execute_single(
            "SELECT * FROM courses WHERE code = ?", (code,)
        )

    def get_course_count(self) -> int:
        result = self.db.execute_single("SELECT COUNT(*) FROM courses")
        return result[0] if result else 0


class EnrollmentRepository:
    def __init__(self, db: UniversityDB):
        self.db = db

    def enroll_student(self, user_uuid: bytes, course_code: str) -> bool:
        return self.db.execute_update(
            "INSERT INTO enrollments (user_uuid, course_code) VALUES (?, ?)",
            (user_uuid, course_code)
        )

    def get_student_enrollments(self, user_uuid: bytes):
        return self.db.execute_query(
            "SELECT course_code FROM enrollments WHERE user_uuid = ?", (user_uuid,)
        )

    def get_student_courses_detailed(self, user_uuid: bytes):
        return self.db.execute_query("""
            SELECT c.name, c.code 
            FROM courses c 
            JOIN enrollments e ON c.code = e.course_code 
            WHERE e.user_uuid = ?
        """, (user_uuid,))

    def get_enrollment_count(self, user_uuid: bytes) -> int:
        result = self.db.execute_single(
            "SELECT COUNT(*) FROM enrollments WHERE user_uuid = ?", (user_uuid,)
        )
        return result[0] if result else 0

    def remove_enrollment(self, user_uuid: bytes, course_code: str) -> bool:
        return self.db.execute_update("""
            DELETE FROM enrollments 
            WHERE user_uuid = ? AND course_code = ?
        """, (user_uuid, course_code))

    def swap_enrollment(self, user_uuid: bytes, old_code: str, new_code: str) -> bool:
        """Atomically replace one enrollment with another."""
        try:
            self.db.cursor.execute(
                "DELETE FROM enrollments WHERE user_uuid = ? AND course_code = ?",
                (user_uuid, old_code)
            )
            self.db.cursor.execute(
                "INSERT INTO enrollments (user_uuid, course_code) VALUES (?, ?)",
                (user_uuid, new_code)
            )
            self.db.conn.commit()
            return True
        except sqlite3.Error:
            self.db.conn.rollback()
            return False

    def get_global_roster(self):
        return self.db.execute_query("""
            SELECT u.name, u.custom_id, GROUP_CONCAT(c.code, ', ') AS courses
            FROM users u 
            JOIN enrollments e ON u.u_uuid = e.user_uuid 
            JOIN courses c ON e.course_code = c.code 
            WHERE u.role = 'student'
            GROUP BY u.u_uuid, u.name, u.custom_id
        """)

    def rollback(self):
        self.db.rollback()

    def commit(self):
        self.db.commit()