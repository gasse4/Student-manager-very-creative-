from typing import List

from src.domain.interfaces import IUserRepository
from src.domain.models import (
    DuplicateSubjectError,
    MaxSubjectsReachedError,
    Role,
    Student,
    Subject,
    UserAlreadyExistsError,
)


class EnrollmentManager:
    """
    Use case handler for student registration and subject enrollment logic.
    Enforces business rules defined in the domain layer.
    """

    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo
        self._max_subjects = 8

    def register_student(self, username: str) -> Student:
        """
        Registers a new student if the username is unique.
        """
        if self._user_repo.exists(username):
            raise UserAlreadyExistsError(username)

        student = Student(username=username, role=Role.STUDENT)
        self._user_repo.save(student)
        return student

    def enroll_in_subject(self, username: str, subject_name: str) -> Student:
        """
        Enrolls a student in a new subject.
        Validates uniqueness and capacity limits.
        """
        user = self._user_repo.get_by_username(username)
        if not isinstance(user, Student):
            raise ValueError(f"User '{username}' is not a student.")

        # Business Rule: Check for duplicate subjects
        if any(s.name == subject_name for s in user.subjects):
            raise DuplicateSubjectError(subject_name)

        # Business Rule: Check for subject limit
        if len(user.subjects) >= self._max_subjects:
            raise MaxSubjectsReachedError(self._max_subjects)

        new_subject = Subject(name=subject_name)
        user.subjects.append(new_subject)

        self._user_repo.save(user)
        return user

    def get_student_subjects(self, username: str) -> List[Subject]:
        """Retrieves the list of subjects for a given student."""
        user = self._user_repo.get_by_username(username)
        if isinstance(user, Student):
            return user.subjects
        return []
