"""
Outbound ports (Infrastructure Interfaces) for the FilaVaga engine application layer.

These ports define interfaces for external services and drivers (like databases,
filesystem, clock, logging) that the application services depend on.

Author: Kalyel N. Laurindo / Software Engineer
"""

from abc import ABC, abstractmethod
from datetime import datetime
from filavaga.core.entities import Candidate, Vacancy, Queue


class IClock(ABC):
    """
    Interface for timezone-safe high-precision system clock.
    """

    @abstractmethod
    def now(self) -> datetime:
        """
        Return the current date and time as a timezone-aware UTC datetime.
        """
        pass


class IStateRepository(ABC):
    """
    Interface for persistence operations (persistence adapter port).
    """

    @abstractmethod
    def get_candidate(self, candidate_id: str) -> Candidate | None:
        """
        Retrieve a candidate by their unique ID.
        """
        pass

    @abstractmethod
    def save_candidate(self, candidate: Candidate) -> None:
        """
        Save/update a candidate's state in persistent storage.
        """
        pass

    @abstractmethod
    def get_all_candidates(self) -> dict[str, Candidate]:
        """
        Retrieve all candidates indexed by their ID.
        """
        pass

    @abstractmethod
    def get_vacancy(self, vacancy_id: str) -> Vacancy | None:
        """
        Retrieve a vacancy by its unique ID.
        """
        pass

    @abstractmethod
    def save_vacancy(self, vacancy: Vacancy) -> None:
        """
        Save/update a vacancy's state in persistent storage.
        """
        pass

    @abstractmethod
    def get_all_vacancies(self) -> dict[str, Vacancy]:
        """
        Retrieve all vacancies indexed by their ID.
        """
        pass

    @abstractmethod
    def get_queue(self, profession_code: str) -> Queue | None:
        """
        Retrieve the queue for a given profession code.
        """
        pass

    @abstractmethod
    def save_queue(self, queue: Queue) -> None:
        """
        Save/update a queue's state in persistent storage.
        """
        pass
