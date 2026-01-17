from typing import Dict, List, Optional

from src.domain.interfaces import IQuizRepository, IUserRepository
from src.domain.models import Quiz, User


class InMemoryUserRepository(IUserRepository):
    """
    In-memory implementation of user persistence till you implment the sqlite db TODO.
    """

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def save(self, user: User) -> None:
        """Stores the user in a dictionary keyed by username."""
        self._users[user.username] = user

    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieves user from the internal dictionary."""
        return self._users.get(username)

    def exists(self, username: str) -> bool:
        """Checks if the username key exists in the dictionary."""
        return username in self._users


class InMemoryQuizRepository(IQuizRepository):
    """
    In-memory implementation of quiz persistence.
    Stores quizzes in a simple list for easy filtering.
    """

    def __init__(self) -> None:
        self._quizzes: List[Quiz] = []

    def save(self, quiz: Quiz) -> None:
        """Adds a quiz to the storage list."""
        self._quizzes.append(quiz)

    def get_by_subject(self, subject_name: str) -> List[Quiz]:
        """Filters the stored quizzes by subject name."""
        return [q for q in self._quizzes if q.subject_name == subject_name]
