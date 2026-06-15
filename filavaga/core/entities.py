"""
Domain core entities for the FilaVaga engine.

This module houses pure business entities containing invariant rules
and status transitions.

Author: Kalyel N. Laurindo / Software Engineer
"""

from dataclasses import dataclass, field
from datetime import datetime
from filavaga.core.exceptions import (
    InvalidStateTransitionError,
    EntityExpiredError,
    CapacityLimitExceededError,
)


@dataclass
class Candidate:
    """
    Represents a job seeker registered in the SINE public queue system.
    
    A Candidate is the core unit of a Waitlist FIFO queue, categorized by
    their professional code (CBO) and prioritized by their registration date/time.
    """
    id: str
    name: str
    sector_zone: str
    profession_code: str
    registered_at: str
    status: str = field(default="PENDING")

    def transition_to(self, new_status: str) -> None:
        """
        Transition candidate's status according to strict state machine rules.
        
        Allowed paths:
        PENDING -> CONTACTED
        CONTACTED -> PLACED
        CONTACTED -> REJECTED
        
        Any other transition triggers InvalidStateTransitionError.
        """
        if new_status == self.status:
            return

        allowed_transitions = {
            "PENDING": {"CONTACTED"},
            "CONTACTED": {"PLACED", "REJECTED"},
            "PLACED": set(),
            "REJECTED": set()
        }

        valid_targets = allowed_transitions.get(self.status, set())
        if new_status not in valid_targets:
            raise InvalidStateTransitionError(
                f"Invalid status transition: Cannot transition from {self.status} to {new_status}"
            )

        self.status = new_status


@dataclass
class Vacancy:
    """
    Represents a job opening registered by an employer in a specific SINE branch.
    
    Contains capacity rules and lazy-evaluated Time-To-Live (TTL) expiration.
    """
    id: str
    title: str
    profession_code: str
    sector_zone: str
    capacity: int
    created_at: str
    expires_at: str
    placed_candidate_ids: list[str] = field(default_factory=list)

    def is_expired(self, current_time: datetime | str) -> bool:
        """
        Dynamically determine if the vacancy has expired (lazy evaluation).
        
        Compares the expires_at timestamp with the provided current_time.
        """
        # Convert string to datetime if needed
        if isinstance(current_time, str):
            # Replacing Z suffix with +00:00 to support native ISO-8601 parsing in Python < 3.11
            dt_current = datetime.fromisoformat(current_time.replace("Z", "+00:00"))
        else:
            dt_current = current_time

        dt_expires = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        return dt_current >= dt_expires

    def is_full(self) -> bool:
        """
        Check if the vacancy has reached its maximum placement capacity.
        """
        return len(self.placed_candidate_ids) >= self.capacity

    def place_candidate(self, candidate_id: str, current_time: datetime | str) -> None:
        """
        Allocate a candidate to this vacancy, validating TTL and capacity.
        
        Raises EntityExpiredError if the vacancy has expired.
        Raises CapacityLimitExceededError if the vacancy is already full.
        """
        if self.is_expired(current_time):
            raise EntityExpiredError(f"Cannot place candidate {candidate_id}: Vacancy {self.id} has expired")

        if self.is_full():
            raise CapacityLimitExceededError(
                f"Cannot place candidate {candidate_id}: Vacancy {self.id} capacity limit of {self.capacity} exceeded"
            )

        self.placed_candidate_ids.append(candidate_id)


