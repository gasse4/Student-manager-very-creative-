from src.presentation.app import StudentManagerApp
from src.infrastructure import UniversityDB, UserRepository, CourseRepository, EnrollmentRepository, is_admin_string_hard
from src.presentation.interface import student_portal, admin_portal
import sys


def main() -> None:
    """
    Composition Root for the Student Manager application.
    Initializes infrastructure and routes to student or admin portal.
    """
    
    if "--tui" in sys.argv:
        try:
            from src.presentation.app import StudentManagerApp
            app = StudentManagerApp()
            app.run()
        except ImportError:
            print("[!] TUI mode not available. Using CLI mode instead.")
            cli_main()
    else:
        cli_main()


def cli_main() -> None:
    """CLI mode for the application."""
    db = UniversityDB()
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    enrollment_repo = EnrollmentRepository(db)
    
    if len(sys.argv) == 2:
        admin_str = sys.argv[1]
        if is_admin_string_hard(admin_str):
            admin_portal(user_repo, course_repo, enrollment_repo, admin_str)
        else:
            print("\n[!] Security Error: Admin String is too weak.")
            print("[!] Requirements: At least 12 characters with uppercase, lowercase, digit, and symbol")
    else:
        student_portal(user_repo, course_repo, enrollment_repo)
    
    db.close()


if __name__ == "__main__":
    main()