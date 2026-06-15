import pytest
from filavaga.core.exceptions import (
    FilaVagaDomainError,
    InvalidStateTransitionError,
    EntityNotFoundError,
    CapacityLimitExceededError,
    EntityExpiredError,
)

def test_exceptions_inheritance():
    """Verify that all custom domain exceptions inherit from the base domain error."""
    assert issubclass(FilaVagaDomainError, Exception)
    assert issubclass(InvalidStateTransitionError, FilaVagaDomainError)
    assert issubclass(EntityNotFoundError, FilaVagaDomainError)
    assert issubclass(CapacityLimitExceededError, FilaVagaDomainError)
    assert issubclass(EntityExpiredError, FilaVagaDomainError)

def test_exception_messages():
    """Verify that exceptions preserve their debug messages correctly."""
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        raise InvalidStateTransitionError("Cannot transit from PENDING to PLACED")
    assert str(exc_info.value) == "Cannot transit from PENDING to PLACED"

    with pytest.raises(EntityNotFoundError) as exc_info:
        raise EntityNotFoundError("Candidate with ID c_123 not found")
    assert str(exc_info.value) == "Candidate with ID c_123 not found"

    with pytest.raises(CapacityLimitExceededError) as exc_info:
        raise CapacityLimitExceededError("Vacancy capacity limit of 2 exceeded")
    assert str(exc_info.value) == "Vacancy capacity limit of 2 exceeded"

    with pytest.raises(EntityExpiredError) as exc_info:
        raise EntityExpiredError("Vacancy v_456 has expired")
    assert str(exc_info.value) == "Vacancy v_456 has expired"


def test_candidate_creation():
    """Verify that a Candidate entity can be successfully created with correct attributes."""
    from filavaga.core.entities import Candidate

    candidate = Candidate(
        id="c_01h3nbd7z6r6e",
        name="Maria Silva",
        sector_zone="SUL",
        profession_code="4110-10",
        registered_at="2026-06-15T08:30:15Z"
    )

    assert candidate.id == "c_01h3nbd7z6r6e"
    assert candidate.name == "Maria Silva"
    assert candidate.sector_zone == "SUL"
    assert candidate.profession_code == "4110-10"
    assert candidate.registered_at == "2026-06-15T08:30:15Z"
    assert candidate.status == "PENDING"


def test_candidate_state_transitions():
    """Verify that Candidate status transitions follow the strict state machine rules."""
    from filavaga.core.entities import Candidate
    from filavaga.core.exceptions import InvalidStateTransitionError

    candidate = Candidate(
        id="c_01h3nbd7z6r6e",
        name="Maria Silva",
        sector_zone="SUL",
        profession_code="4110-10",
        registered_at="2026-06-15T08:30:15Z"
    )

    # 1. PENDING -> CONTACTED (Valid)
    candidate.transition_to("CONTACTED")
    assert candidate.status == "CONTACTED"

    # 2. CONTACTED -> CONTACTED (Same status, Valid no-op)
    candidate.transition_to("CONTACTED")
    assert candidate.status == "CONTACTED"

    # 3. CONTACTED -> PLACED (Valid)
    candidate.transition_to("PLACED")
    assert candidate.status == "PLACED"

    # 4. PLACED -> PENDING (Invalid, backward transition)
    with pytest.raises(InvalidStateTransitionError):
        candidate.transition_to("PENDING")

    # 5. Reset to PENDING for testing other paths
    candidate_2 = Candidate(
        id="c_01h3nbd7z6r6f",
        name="João Silva",
        sector_zone="SUL",
        profession_code="4110-10",
        registered_at="2026-06-15T08:30:15Z"
    )

    # 6. PENDING -> PLACED (Invalid, direct jump)
    with pytest.raises(InvalidStateTransitionError):
        candidate_2.transition_to("PLACED")

    # 7. PENDING -> REJECTED (Invalid, direct jump)
    with pytest.raises(InvalidStateTransitionError):
        candidate_2.transition_to("REJECTED")

    # 8. PENDING -> CONTACTED -> REJECTED (Valid)
    candidate_2.transition_to("CONTACTED")
    candidate_2.transition_to("REJECTED")
    assert candidate_2.status == "REJECTED"

    # 9. REJECTED -> CONTACTED (Invalid, backward transition)
    with pytest.raises(InvalidStateTransitionError):
        candidate_2.transition_to("CONTACTED")


