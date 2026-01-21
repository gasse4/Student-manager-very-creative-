import time
import os
import sys
import uuid as uuid_pkg
from src.infrastructure.database import UniversityDB
from src.infrastructure.repositories import UserRepository, CourseRepository, EnrollmentRepository

def run_performance_test(n_users=100, n_courses=10):
    print(f"--- Optimized Performance Benchmark ---")
    print(f"Users: {n_users}, Courses: {n_courses}\n")
    
    test_db_path = "performance_test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = UniversityDB(test_db_path)
    
    # 1. Benchmark Course Addition
    start_time = time.time()
    course_data = [(f"C{i}", f"Course Name {i}") for i in range(n_courses)]
    db.cursor.executemany("INSERT INTO courses VALUES (?, ?)", course_data)
    db.conn.commit()
    course_time = time.time() - start_time
    print(f"[+] Added {n_courses} courses in: {course_time:.4f}s")
    
    # 2. Benchmark User Registration
    start_time = time.time()
    user_data = [(str(uuid_pkg.uuid4()), f"ID_{i}", f"Student {i}", "student") for i in range(n_users)]
    db.cursor.execute("BEGIN TRANSACTION")
    db.cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", user_data)
    db.conn.commit()
    user_time = time.time() - start_time
    print(f"[+] Registered {n_users} users in: {user_time:.4f}s")
    
    # 3. Benchmark Enrollment
    start_time = time.time()
    enrollment_data = []
    for row in user_data:
        u_uuid = row[0]
        for j in range(5):
            enrollment_data.append((u_uuid, f"C{j}"))
    
    db.cursor.execute("BEGIN TRANSACTION")
    db.cursor.executemany("INSERT INTO enrollments VALUES (?, ?)", enrollment_data)
    db.conn.commit()
    enroll_time = time.time() - start_time
    print(f"[+] Performed {n_users * 5} enrollments in: {enroll_time:.4f}s")
    
    # 4. Benchmark Global Roster Fetching
    start_time = time.time()
    db.cursor.execute("""SELECT u.name, u.custom_id, group_concat(c.code, ', ') 
                       FROM users u 
                       JOIN enrollments e ON u.u_uuid = e.user_uuid 
                       JOIN courses c ON e.course_code = c.code 
                       WHERE u.role='student' 
                       GROUP BY u.u_uuid""")
    roster = db.cursor.fetchall()
    roster_time = time.time() - start_time
    print(f"[+] Fetched global roster ({len(roster)} entries) in: {roster_time:.4f}s")
    
    print(f"\nTotal operations time: {course_time + user_time + enroll_time + roster_time:.4f}s")
    
    db.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

if __name__ == "__main__":
    users = 100000
    courses = 10
    if len(sys.argv) > 1:
        users = int(sys.argv[1])
    if len(sys.argv) > 2:
        courses = int(sys.argv[2])
    run_performance_test(users, courses)
