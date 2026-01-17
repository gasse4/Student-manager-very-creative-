from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, ProgressBar, Static

from src.domain.models import Student
from src.infrastructure.repositories import InMemoryUserRepository
from src.use_cases.enrollment_manager import EnrollmentManager


class WelcomeScreen(Screen):
    """Initial landing screen to choose between Student and Admin roles."""

    def compose(self) -> ComposeResult:
        pass

class LoginScreen(Screen):
    """Screen for student authentication and registration."""
    pass


class StudentDashboard(Screen):
    """Main dashboard for students to manage their subjects."""

    pass

class StudentManagerApp(App):
    """
    Main Application class using Clean Architecture.
    Gasser's Implementation - Presentation Layer.
    """

    pass


if __name__ == "__main__":
    app = StudentManagerApp()
    app.run()
