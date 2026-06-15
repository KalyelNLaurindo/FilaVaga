"""
Inbound ports (Use Cases) for the FilaVaga engine application layer.

These ports define the boundary interfaces for external clients (like CLI or APIs)
to interact with the core business use cases.

Author: Kalyel N. Laurindo / Software Engineer
"""

from abc import ABC, abstractmethod
from filavaga.core.entities import Candidate


class IRegisterCandidateUseCase(ABC):
    """
    Interface for the candidate registration use case.
    """

    @abstractmethod
    def register_candidate(
        self, name: str, profession_code: str, sector_zone: str
    ) -> Candidate:
        """
        Validate and register a new candidate into the appropriate FIFO queue.
        
        Args:
            name: Full name of the candidate.
            profession_code: CBO code for the candidate's profession.
            sector_zone: Preferred region of work.
            
        Returns:
            The registered Candidate entity with its assigned ID and timestamp.
        """
        pass


class IMatchVacancyUseCase(ABC):
    """
    Interface for the vacancy matching engine use case.
    """

    @abstractmethod
    def match_vacancy(self, vacancy_id: str) -> Candidate | None:
        """
        Find and return the highest-priority matching candidate for a given vacancy.
        
        Evaluates vacancy TTL dynamically, checks capacity, scans the matching FIFO
        profession queue, and returns the priority candidate.
        
        Args:
            vacancy_id: The unique identifier of the vacancy to match.
            
        Returns:
            The matching Candidate entity, or None if no eligible candidate is found.
        """
        pass
