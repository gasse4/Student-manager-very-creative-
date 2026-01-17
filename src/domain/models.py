from dataclasses import dataclass, field
from enum import Enum


class Role(Enum):
    """Defines access levels within the system."""
    STUDENT = "student"
    ADMIN = "admin"


@dataclass(frozen=True)
class Subject:
    """Domain Value Object representing a course of study."""
    name: str


@dataclass
class Quiz:
    """Domain Entity for subject assessments."""
    title: str
    subject_name: str


@dataclass
class User:
    """Base Domain Entity for all users."""
    username: str
    role: Role


@dataclass
class Student(User):
    """Aggregate Root representing a student and their enrollments."""
    subjects: list[Subject] = field(default_factory=list)

    def __post_init__(self):
        self.role = Role.STUDENT


#  Domain Exceptions 

class DomainError(Exception):
    """Base class for domain-specific business rule violations."""
    pass


class MaxSubjectsReachedError(DomainError):
    """Raised when a student attempts to exceed the enrollment limit (default 8)."""
    def __init__(self, limit: int = 8):
        super().__init__(f"Enrollment limit reached: Maximum {limit} subjects allowed.")


class DuplicateSubjectError(DomainError):
    """Raised when adding a subject the student is already enrolled in."""
    def __init__(self, name: str):
        super().__init__(f"Already enrolled in subject: {name}")


class UserAlreadyExistsError(DomainError):
    """Raised during registration if the username is taken."""
    def __init__(self, username: str):
        super().__init__(f"The username '{username}' is already in use.")
