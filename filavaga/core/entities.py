"""
Domain core entities for the FilaVaga engine.

This module houses pure business entities containing invariant rules
and status transitions.

Author: Kalyel N. Laurindo / Software Engineer
"""

from dataclasses import dataclass, field


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
