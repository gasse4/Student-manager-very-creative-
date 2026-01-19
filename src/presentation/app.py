from textual.app import App, ComposeResult
from textual.containers import Vertical, Center, Horizontal, Middle
from textual.widgets import Button, Label, Input, DataTable
from textual.screen import Screen
from src.infrastructure.database import UniversityDB
import uuid



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



class ScheduleScreen(BaseScreen):
    # Screen for viewing current enrollments.
    def __init__(self, user):
        super().__init__()
        self.user_data = user

    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label(f"My Courses - {self.user_data[2]}", id="screen-title")
                yield DataTable(id="schedule-table")
                yield Button("Back", id="back", variant="error")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Code", "Course Name")
        db = self.app.db
        db.cursor.execute("SELECT c.code, c.name FROM courses c JOIN enrollments e ON c.code = e.course_code WHERE e.user_uuid=?", (self.user_data[0],))
        for row in db.cursor.fetchall():
            table.add_row(*row)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()



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
        
        db = self.app.db
        db.cursor.execute("SELECT course_code FROM enrollments WHERE user_uuid=?", (self.user_data[0],))
        enrolled_codes = {r[0] for r in db.cursor.fetchall()}
        
        db.cursor.execute("SELECT * FROM courses")
        for row in db.cursor.fetchall():
            if row[0] not in enrolled_codes:
                table.add_row(*row)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "enroll-btn":
            table = self.query_one("#enroll-table", DataTable)
            if table.cursor_row is not None:
                try:
                    row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
                    row = table.get_row(row_key)
                    course_code = row[0]
                    
                    db = self.app.db
                    db.cursor.execute("SELECT COUNT(*) FROM enrollments WHERE user_uuid=?", (self.user_data[0],))
                    if db.cursor.fetchone()[0] >= 8:
                        self.notify("Enrollment limit (8) reached!", severity="error")
                        return

                    db.cursor.execute("INSERT INTO enrollments VALUES (?, ?)", (self.user_data[0], course_code))
                    db.conn.commit()
                    self.notify(f"Successfully enrolled in {course_code}!")
                    self.refresh_table()
                except Exception as e:
                    self.notify(f"Enrollment failed.", severity="error")
            else:
                self.notify("Please select a course from the table first.", severity="warning")



class Dashboard(BaseScreen):
    # Simple menu-based dashboard.
    def __init__(self, user):
        super().__init__()
        self.user = user 

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
            self.app.push_screen(ScheduleScreen(self.user))
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
                db = self.app.db
                # Using a UUID as custom_id like in the student_portal logic
                user_id = str(uuid.uuid4())
                result = db.register_user(name, 'student', user_id)
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
            db = self.app.db
            user = db.get_user_by_id(user_input)
            
            if user and user[3] == 'student':
                 self.app.push_screen(Dashboard(user))
            else:
                 subtitle = self.query_one("#screen-subtitle", Label)
                 subtitle.update("Error: Invalid ID or Access Denied!")
                 subtitle.remove_class("success")
                 subtitle.add_class("error")



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
        self.push_screen(WelcomePage())

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
