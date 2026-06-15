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
