from textual.app import App, ComposeResult
from textual.containers import Vertical, Center, Horizontal, Middle
from textual.widgets import Button, Label ,Input
from textual.screen import Screen

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

class Dashboard(BaseScreen):
    """Dashboard screen for authenticated users."""
    def compose_content(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Dashboard", id="screen-title")
                yield Label("Welcome to your dashboard!", id="screen-subtitle")
                yield Button("Logout", id="logout", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "logout":
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

    def verified_or_not(self, user_id: str) -> bool:
        """Verifies the user ID."""
        # Check if the ID consists only of digits and is not empty
        return user_id.strip().isdigit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        super().on_button_pressed(event)
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "login":
            user_input = self.query_one("#input", Input).value
            if self.verified_or_not(user_input):
                 self.app.push_screen(Dashboard())
            else:
                 subtitle = self.query_one("#screen-subtitle", Label)
                 subtitle.update("Error: ID must consist only of numbers!")
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
    """

    def on_mount(self) -> None:
        self.push_screen(WelcomePage())

if __name__ == "__main__":
    app = StudentManagerApp()
    app.run()
