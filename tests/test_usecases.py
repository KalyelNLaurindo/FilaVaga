import pytest
from abc import ABC

def test_port_interfaces_defined():
    """Verify that ports exist and are abstract base classes (ABCs)."""
    from filavaga.application.ports.inbound import (
        IRegisterCandidateUseCase,
        IMatchVacancyUseCase,
    )
    from filavaga.application.ports.outbound import (
        IClock,
        IStateRepository,
    )

    assert issubclass(IRegisterCandidateUseCase, ABC)
    assert issubclass(IMatchVacancyUseCase, ABC)
    assert issubclass(IClock, ABC)
    assert issubclass(IStateRepository, ABC)

    # Check for abstract method presence
    assert "register_candidate" in IRegisterCandidateUseCase.__abstractmethods__
    assert "match_vacancy" in IMatchVacancyUseCase.__abstractmethods__
    assert "now" in IClock.__abstractmethods__
    
    assert "get_candidate" in IStateRepository.__abstractmethods__
    assert "save_candidate" in IStateRepository.__abstractmethods__
    assert "get_all_candidates" in IStateRepository.__abstractmethods__
    assert "get_vacancy" in IStateRepository.__abstractmethods__
    assert "save_vacancy" in IStateRepository.__abstractmethods__
    assert "get_all_vacancies" in IStateRepository.__abstractmethods__
    assert "get_queue" in IStateRepository.__abstractmethods__
    assert "save_queue" in IStateRepository.__abstractmethods__
