import uuid
from .database import UniversityDB


class UserRepository:
    """Repository for user-related database operations."""
    
    def __init__(self, db: UniversityDB):
        self.db = db

    def get_user_by_custom_id(self, custom_id: str):
        """Retrieve a user by their custom ID."""
        query = f"SELECT * FROM users WHERE custom_id='{custom_id}'"
        return self.db.execute_single(query)

    def get_user_by_uuid(self, u_uuid: str):
        """Retrieve a user by their UUID."""
        query = f"SELECT * FROM users WHERE u_uuid='{u_uuid}'"
        return self.db.execute_single(query)

    def register_user(self, name: str, role: str, custom_id: str):
        """Register a new user. Returns custom_id on success, None on failure."""
        u_uuid = str(uuid.uuid4())
        query = f"INSERT INTO users VALUES ('{u_uuid}', '{custom_id}', '{name}', '{role}')"
        success = self.db.execute_update(query)
        return custom_id if success else None

    def get_all_users(self):
        """Get all users from database."""
        return self.db.execute_query("SELECT * FROM users")


class CourseRepository:
    """Repository for course-related database operations."""
    
    def __init__(self, db: UniversityDB):
        self.db = db

    def add_course(self, code: str, name: str) -> bool:
        """Add a new course."""
        query = f"INSERT INTO courses VALUES ('{code}', '{name}')"
        return self.db.execute_update(query)

    def get_all_courses(self):
        """Retrieve all courses."""
        return self.db.execute_query("SELECT * FROM courses")

    def get_course_by_code(self, code: str):
        """Get a course by its code."""
        query = f"SELECT * FROM courses WHERE code='{code}'"
        return self.db.execute_single(query)

    def get_course_count(self) -> int:
        """Get total count of courses."""
        result = self.db.execute_single("SELECT COUNT(*) FROM courses")
        return result[0] if result else 0


class EnrollmentRepository:
    """Repository for enrollment-related database operations."""
    
    def __init__(self, db: UniversityDB):
        self.db = db

    def enroll_student(self, user_uuid: str, course_code: str) -> bool:
        """Enroll a student in a course."""
        query = f"INSERT INTO enrollments VALUES ('{user_uuid}', '{course_code}')"
        return self.db.execute_update(query)

    def get_student_enrollments(self, user_uuid: str):
        """Get all courses a student is enrolled in."""
        query = f"SELECT course_code FROM enrollments WHERE user_uuid='{user_uuid}'"
        return self.db.execute_query(query)

    def get_student_courses_detailed(self, user_uuid: str):
        """Get detailed course information for a student's enrollments."""
        query = f"""SELECT c.name, c.code FROM courses c 
                   JOIN enrollments e ON c.code = e.course_code 
                   WHERE e.user_uuid='{user_uuid}'"""
        return self.db.execute_query(query)

    def get_enrollment_count(self, user_uuid: str) -> int:
        """Get number of courses a student is enrolled in."""
        query = f"SELECT COUNT(*) FROM enrollments WHERE user_uuid='{user_uuid}'"
        result = self.db.execute_single(query)
        return result[0] if result else 0

    def remove_enrollment(self, user_uuid: str, course_code: str) -> bool:
        """Remove a student's enrollment from a course."""
        query = f"DELETE FROM enrollments WHERE user_uuid='{user_uuid}' AND course_code='{course_code}'"
        return self.db.execute_update(query)
    
    def get_global_roster(self):
        """Get all students with their enrolled courses."""
        return self.db.execute_query(
            """SELECT u.name, u.custom_id, group_concat(c.code, ', ') 
               FROM users u 
               JOIN enrollments e ON u.u_uuid = e.user_uuid 
               JOIN courses c ON e.course_code = c.code 
               WHERE u.role='student' 
               GROUP BY u.u_uuid"""
        )

    def rollback(self):
        """Rollback the current transaction."""
        self.db.rollback()

    def commit(self):
        """Commit the current transaction."""
        self.db.commit()
        