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

