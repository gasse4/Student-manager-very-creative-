from textual.app import App, ComposeResult
from textual.containers import Vertical, Center, Horizontal, Middle
from textual.widgets import Button, Label, Input, DataTable
from textual.screen import Screen
from src.infrastructure.database import UniversityDB
from src.infrastructure.repositories import UserRepository, CourseRepository, EnrollmentRepository
from src.infrastructure.utils import is_admin_string_hard
import uuid
import sys

class BaseScreen(Screen):
    # Base screen.
    
    def compose(self) -> ComposeResult:
        with Horizontal(id="app-header"):
            yield Label("Student Manager", id="app-title")
            yield Button("Exit", id="exit-btn", variant="error")
        
        with Vertical(id="content-area"):
            yield from self.compose_content()

    def compose_content(self) -> ComposeResult:
        # Override this to add screen-specific content.
        yield Label("Default Content")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-btn":
            self.app.exit()



class UpdateCourseScreen(BaseScreen):
    # Screen for selecting a new course to replace an old one.
    def __init__(self, user, old_code, callback):
        super().__init__()
        self.user_data = user
        self.old_code = old_code
        self.callback = callback

    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label(f"Select replacement for {self.old_code}", id="screen-title")
                yield DataTable(id="update-table")
                yield Button("Select & Swap", id="swap-btn", variant="primary")
                yield Button("Cancel", id="back", variant="error")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Code", "Course Name")
        
        repo = self.app.course_repo
        en_repo = self.app.enrollment_repo
        
        enrolled = en_repo.get_student_enrollments(self.user_data[0])
        enrolled_codes = {r[0] for r in enrolled}
        
        all_courses = repo.get_all_courses()
        for row in all_courses:
            if row[0] not in enrolled_codes:
                table.add_row(*row)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "swap-btn":
            table = self.query_one("#update-table", DataTable)
            if table.cursor_row is not None and table.row_count > 0:
                try:
                    row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
                    row = table.get_row(row_key)
                    new_code = row[0]
                    
                    en_repo = self.app.enrollment_repo
                    if en_repo.remove_enrollment(self.user_data[0], self.old_code):
                        if en_repo.enroll_student(self.user_data[0], new_code):
                            self.notify(f"Updated: {self.old_code} -> {new_code}")
                            self.callback()
                            self.app.pop_screen()
                        else:
                            # Rollback if possible, though repo doesn't have a clean swap
                            en_repo.enroll_student(self.user_data[0], self.old_code)
                            self.notify("Error enrolling in new course.", severity="error")
                    else:
                        self.notify("Error removing old course.", severity="error")
                except Exception:
                    self.notify("Please select a course first.", severity="warning")
            else:
                self.notify("No courses available to swap.", severity="warning")


class ScheduleScreen(BaseScreen):
    # Screen for viewing current enrollments.
    def __init__(self, user, dashboard):
        super().__init__()
        self.user_data = user
        self.dashboard = dashboard

    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label(f"My Courses - {self.user_data[2]}", id="screen-title")
                yield Label(f"Modifications Used: {self.dashboard.action_count}/3", id="screen-subtitle")
                yield DataTable(id="schedule-table")
                yield Button("Remove Selected", id="remove-btn", variant="warning")
                yield Button("Update Selected", id="update-btn", variant="primary")
                yield Button("Back", id="back", variant="error")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        self.refresh_table()

    def refresh_table(self) -> None:
        self.query_one("#screen-subtitle", Label).update(f"Modifications Used: {self.dashboard.action_count}/3")
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("Code", "Course Name")
        enrollment_repo = self.app.enrollment_repo
        courses = enrollment_repo.get_student_courses_detailed(self.user_data[0])
        for name, code in courses:
            table.add_row(code, name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "remove-btn":
            if self.dashboard.action_count >= 3:
                self.notify("Error: Maximum limit of 3 modifications reached.", severity="error")
                return

            table = self.query_one("#schedule-table", DataTable)
            if table.cursor_row is not None and table.row_count > 0:
                try:
                    row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
                    row = table.get_row(row_key)
                    course_code = row[0]
                    
                    enrollment_repo = self.app.enrollment_repo
                    if enrollment_repo.remove_enrollment(self.user_data[0], course_code):
                        self.notify(f"Removed {course_code} from schedule.")
                        self.dashboard.action_count += 1
                        self.refresh_table()
                    else:
                        self.notify("Failed to remove course.", severity="error")
                except Exception:
                    self.notify("Error during removal.", severity="error")
            else:
                self.notify("Please select a course to remove.", severity="warning")
        elif event.button.id == "update-btn":
            if self.dashboard.action_count >= 3:
                self.notify("Error: Maximum limit of 3 modifications reached.", severity="error")
                return
            
            table = self.query_one("#schedule-table", DataTable)
            if table.cursor_row is not None and table.row_count > 0:
                try:
                    row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
                    row = table.get_row(row_key)
                    old_code = row[0]
                    
                    def on_success():
                        self.dashboard.action_count += 1
                        self.refresh_table()

                    self.app.push_screen(UpdateCourseScreen(self.user_data, old_code, on_success))
                except Exception:
                    self.notify("Please select a course to update.", severity="warning")
            else:
                self.notify("Please select a course to update.", severity="warning")



class EnrollmentScreen(BaseScreen):
    # Screen for browsing and enrolling in new courses.
    def __init__(self, user):
        super().__init__()
        self.user_data = user

    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Browse & Enroll", id="screen-title")
                yield Label("Select a course and click Enroll (Max 8)", id="screen-subtitle")
                yield DataTable(id="enroll-table")
                yield Button("Enroll Selected", id="enroll-btn", variant="success")
                yield Button("Back", id="back", variant="error")

    def on_mount(self) -> None:
        self.refresh_table()
        table = self.query_one(DataTable)
        table.cursor_type = "row"

    def refresh_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("Code", "Course Name")
        
        enrollment_repo = self.app.enrollment_repo
        course_repo = self.app.course_repo
        
        enrolled = enrollment_repo.get_student_enrollments(self.user_data[0])
        enrolled_codes = {r[0] for r in enrolled}
        
        all_courses = course_repo.get_all_courses()
        for row in all_courses:
            if row[0] not in enrolled_codes:
                table.add_row(*row)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "enroll-btn":
            table = self.query_one("#enroll-table", DataTable)
            if table.cursor_row is not None and table.row_count > 0:
                try:
                    row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
                    row = table.get_row(row_key)
                    course_code = row[0]
                    
                    enrollment_repo = self.app.enrollment_repo
                    if enrollment_repo.get_enrollment_count(self.user_data[0]) >= 8:
                        self.notify("Enrollment limit (8) reached!", severity="error")
                        return

                    if enrollment_repo.enroll_student(self.user_data[0], course_code):
                        self.notify(f"Successfully enrolled in {course_code}!")
                        self.refresh_table()
                    else:
                        self.notify(f"Enrollment failed.", severity="error")
                except Exception as e:
                    self.notify(f"Enrollment failed.", severity="error")
            else:
                self.notify("Please select a course from the table first.", severity="warning")



class Dashboard(BaseScreen):
    # Simple menu-based dashboard.
    def __init__(self, user):
        super().__init__()
        self.user = user 
        self.action_count = 0

    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label(f"Welcome, {self.user[2]}!", id="screen-title")
                yield Label(f"Student Portal | ID: {self.user[1]}", id="screen-subtitle")
                
                yield Button("My Schedule", id="view_schedule", variant="primary")
                yield Button("Browse & Enroll", id="browse_enroll", variant="default")
                yield Button("Logout", id="logout", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "view_schedule":
            self.app.push_screen(ScheduleScreen(self.user, self))
        elif event.button.id == "browse_enroll":
            self.app.push_screen(EnrollmentScreen(self.user))
        elif event.button.id == "logout":
            self.app.pop_screen()



class RegistrationScreen(BaseScreen):
    # Screen for new user registration.
    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Registration Screen", id="screen-title")
                yield Label("Start your journey", id="screen-subtitle", classes="success")
                yield Input(placeholder="Enter your name...", id="input")
                yield Button("Register", id="register", variant="primary")
                yield Button("Back to Welcome", id="back", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "register":
            name = self.query_one("#input", Input).value
            if name:
                user_repo = self.app.user_repo
                # Using a UUID as custom_id like in the student_portal logic
                user_id = str(uuid.uuid4())[:8].upper()
                result = user_repo.register_user(name, 'student', user_id)
                if result:
                    subtitle = self.query_one("#screen-subtitle", Label)
                    subtitle.update(f"Your ID is: {user_id}")
                    subtitle.remove_class("error")
                    subtitle.add_class("success")
                else:
                    subtitle = self.query_one("#screen-subtitle", Label)
                    subtitle.update("Error: Registration failed!")
                    subtitle.add_class("error")



class LoginScreen(BaseScreen):
    # Screen for current user login.
    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Login Screen", id="screen-title")
                yield Label("Welcome Back !", id="screen-subtitle", classes="success")
                yield Input(placeholder="Put your id ....." , id="input")
                yield Button("Login", id="login", variant="primary")
                yield Button("Back to Welcome", id="back", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "login":
            user_input = self.query_one("#input", Input).value
            user_repo = self.app.user_repo
            user = user_repo.get_user_by_custom_id(user_input)
            
            if user:
                if user[3] == 'student':
                    self.app.push_screen(Dashboard(user))
                elif user[3] == 'admin':
                    self.app.push_screen(AdminDashboard(user))
            else:
                 subtitle = self.query_one("#screen-subtitle", Label)
                 subtitle.update("Error: Invalid ID or Access Denied!")
                 subtitle.remove_class("success")
                 subtitle.add_class("error")


class AddCourseScreen(BaseScreen):
    # Screen for adding new courses.
    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Add New Course", id="screen-title")
                yield Input(placeholder="Course Code...", id="code-input")
                yield Input(placeholder="Course Name...", id="name-input")
                yield Button("Add Course", id="add-btn", variant="primary")
                yield Button("Back", id="back", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "add-btn":
            code = self.query_one("#code-input", Input).value
            name = self.query_one("#name-input", Input).value
            if code and name:
                repo = self.app.course_repo
                if repo.get_course_count() >= 10:
                    self.notify("Error: Limit reached (Max 10).", severity="error")
                    return
                if repo.add_course(code, name):
                    self.notify(f"Course {code} added!")
                    self.app.pop_screen()
                else:
                    self.notify("Error: Code already exists.", severity="error")

class RosterScreen(BaseScreen):
    # Screen for viewing global roster.
    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Master Roster", id="screen-title")
                yield DataTable(id="roster-table")
                yield Button("Back", id="back", variant="error")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Student", "ID", "Courses")
        repo = self.app.enrollment_repo
        roster = repo.get_global_roster()
        if roster:
            for r in roster:
                table.add_row(*r)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()

class RegisterAdminScreen(BaseScreen):
    # Screen for registering new admins.
    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Register New Admin", id="screen-title")
                yield Label("String must be hard!", id="screen-subtitle")
                yield Input(placeholder="New Admin ID...", id="admin-id")
                yield Button("Register Admin", id="reg-btn", variant="primary")
                yield Button("Back", id="back", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "reg-btn":
            admin_id = self.query_one("#admin-id", Input).value
            if not is_admin_string_hard(admin_id):
                self.notify("Error: String too weak!", severity="error")
                return
            repo = self.app.user_repo
            if repo.register_user(admin_id, 'admin', admin_id):
                self.notify("New admin registered!")
                self.app.pop_screen()
            else:
                self.notify("Error: Already exists.", severity="error")

class AdminDashboard(BaseScreen):
    # Dashboard for admins.
    def __init__(self, user):
        super().__init__()
        self.user = user

    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label(f"Admin: {self.user[2]}", id="screen-title")
                yield Button("Add Course", id="add_course", variant="primary")
                yield Button("View Roster", id="view_roster")
                yield Button("New Admin", id="new_admin")
                yield Button("Logout", id="logout", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "add_course":
            self.app.push_screen(AddCourseScreen())
        elif event.button.id == "view_roster":
            self.app.push_screen(RosterScreen())
        elif event.button.id == "new_admin":
            self.app.push_screen(RegisterAdminScreen())
        elif event.button.id == "logout":
            self.app.pop_screen()



class WelcomePage(BaseScreen):
    
    # The main welcome page of the Student Manager Tool.
    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Welcome to Student Manager (Very creative !)", id="welcome-title")
                yield Label("Please choose an option to continue", id="welcome-subtitle")
                with Vertical(id="buttons-container"):
                    yield Button("New User", id="new_user", variant="primary")
                    yield Button("Current User", id="current_user" , variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "new_user":
            self.app.push_screen(RegistrationScreen())
        elif event.button.id == "current_user":
            self.app.push_screen(LoginScreen())

class StudentManagerApp(App):

    TITLE = "Student Manager Tool"
    
    def on_mount(self) -> None:
        self.db = UniversityDB()
        self.user_repo = UserRepository(self.db)
        self.course_repo = CourseRepository(self.db)
        self.enrollment_repo = EnrollmentRepository(self.db)
        
        # Always push WelcomePage as the base screen
        self.push_screen(WelcomePage())
        
        # Check for admin string in command line arguments (parity with CLI)
        args = [a for a in sys.argv if a not in ("main.py", "--tui") and not a.startswith("/")]
        if args:
            admin_str = args[0]
            if is_admin_string_hard(admin_str):
                user = self.user_repo.get_user_by_custom_id(admin_str)
                if not user:
                    self.user_repo.register_user(admin_str, 'admin', admin_str)
                    user = self.user_repo.get_user_by_custom_id(admin_str)
                
                # Directly push Admin Dashboard on top of WelcomePage
                self.push_screen(AdminDashboard(user))

    CSS = """
    Screen {
        align: center middle;
    }

    #app-header {
        dock: top;
        height: 4;
        background: $surface;
        border-bottom: solid $primary;
        padding: 0 2;
        align: left middle;
        layout: horizontal;
        
    }

    #app-title {
        width: 1fr;
        height: 3;
        content-align: left middle;
        text-style: bold;
        color: $primary;
        
    }

    #exit-btn {
        width: 10;
        height: 3;
        content-align: center middle;
        margin: 0;
    }

    #content-area {
        height: 1fr;
        align: center middle;
    }

    Center Middle {
        height: auto;
        width: 60;
        border: heavy $primary;
        padding: 2 4;
        background: $surface;
    }

    #welcome-title, #screen-title {
        text-style: bold;
        width: 100%;
        text-align: center;
        margin-bottom: 1;
        color: $accent;
    }

    #welcome-subtitle, #screen-subtitle {
        width: 100%;
        text-align: center;
        margin-bottom: 3;
        padding: 1;
    }

    #buttons-container {
        width: 100%;
        height: auto;
        align: center middle;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }

    #input {
        margin-bottom: 2;
    }

    .success {
        color: $success;
    }

    .error {
        color: $error;
    }

    DataTable {
        height: 10;
        margin-bottom: 2;
        border: tall $primary;
    }
    """

if __name__ == "__main__":
    app = StudentManagerApp()
    app.run()
