from ..infrastructure.database import UniversityDB
from ..infrastructure.repositories import UserRepository, CourseRepository, EnrollmentRepository
from ..infrastructure.utils import is_admin_string_hard, clear_screen
import uuid


def student_portal(user_repo, course_repo, enrollment_repo):
    """Student login and course management portal."""
    while True:
        clear_screen()
        print("=== STUDENT PORTAL ===")
        print("1. Login (Custom ID)\n2. Register (Get Custom ID)\n3. Exit")
        choice = input("\nAction: ")
        
        if choice == '1':
            sid = input("Enter Custom ID: ").strip()
            user = user_repo.get_user_by_custom_id(sid)
            if user and user[3] == 'student':
                student_session(user, user_repo, course_repo, enrollment_repo)
            else:
                input("Access Denied. Custom ID not found.")
        
        elif choice == '2':
            name = input("Enter Student Full Name: ").strip()
            custom_id = str(uuid.uuid4())[:8].upper()
            result = user_repo.register_user(name, 'student', custom_id)
            if result:
                input(f"\n[+] Success! Your Custom ID is: {custom_id}\nPress Enter...")
            else:
                input("\n[!] Registration failed.")
        
        elif choice == '3':
            break
        
        else:
            input("Error: Invalid choice, please enter correct choice")


def student_session(user, user_repo, course_repo, enrollment_repo):
    """Student session for managing courses."""
    u_uuid, u_cid, u_name, _ = user
    update_count = 0
    
    while True:
        clear_screen()
        print(f"STUDENT: {u_name} | ID: {u_cid}")
        print("-" * 50)
        print(f"1. Enroll (Max 8)\n2. My Courses\n3. Update Course ({update_count}/3 Used)\n4. Logout")
        act = input("\nChoice: ")
        
        if act == '1':
            enrollment_count = enrollment_repo.get_enrollment_count(u_uuid)
            if enrollment_count >= 8:
                input("Limit reached (Max 8 courses).")
                continue
            
            all_courses = course_repo.get_all_courses()
            if not all_courses:
                input("No courses available.")
                continue
            
            print("Available Courses:")
            for c in all_courses:
                print(f"[{c[0]}] {c[1]}")
            
            target = input("Enter Course Code: ").strip()
            success = enrollment_repo.enroll_student(u_uuid, target)
            if success:
                input("Enrolled successfully!")
            else:
                input("Invalid code or already enrolled.")
        
        elif act == '2':
            course_enrollments = enrollment_repo.get_student_courses_detailed(u_uuid)
            print("\nYOUR SCHEDULE:")
            if course_enrollments:
                for c in course_enrollments:
                    print(f"• {c[1]}: {c[0]}")
            else:
                print("No courses enrolled.")
            input("\nPress Enter...")
        
        elif act == '3':
            if update_count >= 3:
                input("Error: You have reached the maximum limit of 3 updates.")
                continue
            
            course_codes = enrollment_repo.get_student_enrollments(u_uuid)
            if not course_codes:
                input("You are not enrolled in any courses to update.")
                continue
            
            enrolled_list = ", ".join(c[0] for c in course_codes)
            print(f"Your Courses: {enrolled_list}")
            old_code = input("Enter code of course to REMOVE: ").strip()
            new_code = input("Enter code of NEW course: ").strip()
            
            success = enrollment_repo.swap_enrollment(u_uuid, old_code, new_code)
            if success:
                update_count += 1
                input(f"Success! Update {update_count}/3 completed.")
            else:
                input("Error: Update failed. Check course codes (must exist and not duplicate).")
        
        elif act == '4':
            break
        
        else:
            input("Error: Invalid choice, please enter correct choice")


def admin_portal(user_repo, course_repo, enrollment_repo, admin_str):
    """Admin portal for managing courses and users."""
    user = user_repo.get_user_by_custom_id(admin_str)
    if not user:
        user_repo.register_user(admin_str, 'admin', admin_str)
        user = user_repo.get_user_by_custom_id(admin_str)
    
    while True:
        clear_screen()
        print(f"ADMIN PORTAL | ID: {user[1]}")
        print("-" * 50)
        print("1. Add Course (Max 10)\n2. VIEW GLOBAL ROSTER\n3. REGISTER NEW ADMIN\n4. Exit")
        
        choice = input("\nAction: ")
        
        if choice == '1':
            course_count = course_repo.get_course_count()
            if course_count >= 10:
                input("Error: Limit reached. Admin can only register 10 courses max.")
                continue
            
            code = input("Course Code: ").strip()
            name = input("Course Name: ").strip()
            success = course_repo.add_course(code, name)
            if success:
                input("Course Added.")
            else:
                input("Error: Code exists or invalid.")
        
        elif choice == '2':
            roster = enrollment_repo.get_global_roster()
            print("\n--- MASTER ROSTER ---")
            if roster:
                for r in roster:
                    print(f"Student: {r[0]} | ID: {r[1]}\nCourses: {r[2]}\n")
            else:
                print("No enrollments found.")
            input("Back...")
        
        elif choice == '3':
            new_s = input("Enter New Hard Admin String: ").strip()
            if not is_admin_string_hard(new_s):
                input("Error: String is too weak!")
                continue
            result = user_repo.register_user(new_s, 'admin', new_s)
            if result:
                input("Success! New admin registered.")
            else:
                input("Error: Already exists.")
        
        elif choice == '4':
            break
        
        else:
            input("Error: Invalid choice, please enter correct choice")