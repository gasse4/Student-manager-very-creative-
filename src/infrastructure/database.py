import sqlite3
import os
import uuid
import sys
import re

DB_NAME = "student_manager.db"

def is_admin_string_hard(s):
    if len(s) < 12: return False
    has_upper = re.search(r"[A-Z]", s)
    has_lower = re.search(r"[a-z]", s)
    has_digit = re.search(r"\d", s)
    has_symbol = re.search(r"[^a-zA-Z0-9]", s)
    return all([has_upper, has_lower, has_digit, has_symbol])

class UniversityDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute("PRAGMA foreign_keys = ON")
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

    def get_user_by_id(self, custom_id):
        self.cursor.execute("SELECT * FROM users WHERE custom_id=?", (custom_id,))
        return self.cursor.fetchone()

    def register_user(self, name, role, custom_id):
        u_uuid = str(uuid.uuid4())
        try:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (u_uuid, custom_id, name, role))
            self.conn.commit()
            return custom_id
        except: return None

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def student_portal(db):
    while True:
        clear()
        print("=== STUDENT PORTAL ===")
        print("1. Login (UUID)\n2. Register (Get UUID)\n3. Exit")
        choice = input("\nAction: ")
        if choice == '1':
            sid = input("Enter UUID: ").strip()
            user = db.get_user_by_id(sid)
            if user and user[3] == 'student': student_session(db, user)
            else: input("Access Denied.")
        elif choice == '2':
            name = input("Enter Student Full Name: ")
            cid = db.register_user(name, 'student', str(uuid.uuid4()))
            input(f"\n[!] Registration Successful!\nYour Login UUID is: {cid}\nPress Enter...")
        elif choice == '3': break

def student_session(db, user):
    u_uuid, u_cid, u_name, _ = user
    while True:
        clear()
        print(f"STUDENT: {u_name}")
        print("-" * 30)
        print("1. Enroll (Max 8)\n2. My Courses\n3. Logout")
        act = input("\nChoice: ")
        if act == '1':
            db.cursor.execute("SELECT COUNT(*) FROM enrollments WHERE user_uuid=?", (u_uuid,))
            if db.cursor.fetchone()[0] >= 8:
                input("Limit reached (Max 8)."); continue
            db.cursor.execute("SELECT * FROM courses")
            for c in db.cursor.fetchall(): print(f"[{c[0]}] {c[1]}")
            target = input("Enter Course Code: ")
            try:
                db.cursor.execute("INSERT INTO enrollments VALUES (?, ?)", (u_uuid, target))
                db.conn.commit(); input("Enrolled!")
            except: input("Invalid code or already enrolled.")
        elif act == '2':
            db.cursor.execute("SELECT c.name FROM courses c JOIN enrollments e ON c.code = e.course_code WHERE e.user_uuid=?", (u_uuid,))
            print("\nYOUR SCHEDULE:")
            for c in db.cursor.fetchall(): print(f"• {c[0]}")
            input("\nPress Enter...")
        elif act == '3': break

def admin_portal(db, admin_str):
    user = db.get_user_by_id(admin_str)
    
    if not user:
        db.register_user(admin_str, 'admin', admin_str)
        user = db.get_user_by_id(admin_str)

    while True:
        clear()
        print(f"ADMIN PORTAL | ID: {user[1]}")
        print("-" * 50)
        print("1. Add Course")
        print("2. VIEW GLOBAL ROSTER")
        print("3. REGISTER NEW ADMIN (STRING ONLY)")
        print("4. Exit")
        
        choice = input("\nAction: ")
        if choice == '1':
            code, name = input("Course Code: "), input("Course Name: ")
            try:
                db.cursor.execute("INSERT INTO courses VALUES (?, ?)", (code, name))
                db.conn.commit(); input("Course Added.")
            except: input("Error: Code exists.")
        
        elif choice == '2':
            db.cursor.execute('''SELECT u.name, u.custom_id, group_concat(c.code, ', ') 
                                 FROM users u JOIN enrollments e ON u.u_uuid = e.user_uuid 
                                 JOIN courses c ON e.course_code = c.code 
                                 WHERE u.role='student' GROUP BY u.u_uuid''')
            print("\n--- MASTER ROSTER ---")
            for r in db.cursor.fetchall(): print(f"Student: {r[0]} | ID: {r[1]}\nCourses: {r[2]}\n")
            input("Back...")
            
        elif choice == '3':
            new_s = input("Enter New Hard Admin String: ")
            if not is_admin_string_hard(new_s):
                input("Error: String is too weak!"); continue
            if db.register_user(new_s, 'admin', new_s):
                input(f"Success! Admin string '{new_s}' is now active.")
            else: input("Error: String already exists.")
            
        elif choice == '4': break

if __name__ == "__main__":
    db = UniversityDB()
    if len(sys.argv) == 2:
        admin_str = sys.argv[1]
        if is_admin_string_hard(admin_str):
            admin_portal(db, admin_str)
        else:
            print("\n[!] Security Error: Admin String is too weak.")
    else:
        student_portal(db)