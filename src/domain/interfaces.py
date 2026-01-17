from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Quiz, User


class IUserRepository(ABC):
    """
    Interface for User and Student persistence.
    Decouples the domain logic from specific storage implementations (Memory, SQL, NoSQL).
    """

    @abstractmethod
    def save(self, user: User) -> None:
        """Persists or updates a user/student in the data store."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieves a user entity by their unique username."""
        pass

    @abstractmethod
    def exists(self, username: str) -> bool:
        """Checks if a username is already taken."""
        pass


class IQuizRepository(ABC):
    """
    Interface for Quiz management persistence.
    Handled primarily by Admin roles.
    """

    @abstractmethod
    def save(self, quiz: Quiz) -> None:
        """Persists a new quiz entity."""
        pass

    @abstractmethod
    def get_by_subject(self, subject_name: str) -> List[Quiz]:
        """Retrieves all quizzes associated with a specific subject."""
        pass
