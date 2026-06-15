"""
Custom domain exceptions for the FilaVaga engine.

All exceptions here encapsulate specific business logic errors, preventing
infrastructure details from leaking outside the pure core domain boundary.

Author: Kalyel N. Laurindo / Software Engineer
"""

class FilaVagaDomainError(Exception):
    """
    Base exception class for all business domain errors in FilaVaga.
    
    All specialized domain errors must inherit from this class to allow
    high-level orchestration layers to catch all domain errors uniformly.
    """
    pass


class InvalidStateTransitionError(FilaVagaDomainError):
    """
    Raised when a candidate status transition violates state machine rules.
    
    For example, attempting to transition directly from PENDING to PLACED
    without first being CONTACTED.
    """
    pass


class EntityNotFoundError(FilaVagaDomainError):
    """
    Raised when a queried entity (like a candidate or vacancy) does not exist.
    """
    pass


class CapacityLimitExceededError(FilaVagaDomainError):
    """
    Raised when attempting to allocate more candidates than a vacancy's capacity allows.
    """
    pass


class EntityExpiredError(FilaVagaDomainError):
    """
    Raised when attempting to interact with or match against an expired vacancy (TTL violation).
    """
    pass


class DuplicateCandidateError(FilaVagaDomainError):
    """
    Raised when attempting to register a candidate that is already present in the queue.
    """
    pass

