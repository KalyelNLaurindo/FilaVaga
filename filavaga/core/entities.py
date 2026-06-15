"""
Domain core entities for the FilaVaga engine.

This module houses pure business entities containing invariant rules
and status transitions.

Author: Kalyel N. Laurindo / Software Engineer
"""

from dataclasses import dataclass, field
from filavaga.core.exceptions import InvalidStateTransitionError


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

