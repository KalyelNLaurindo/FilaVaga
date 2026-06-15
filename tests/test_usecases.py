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


class MockClock(ABC):
    """Mock implementation of the IClock port."""
    def __init__(self, time_str="2026-06-15T12:00:00Z"):
        from datetime import datetime
        self.time_val = datetime.fromisoformat(time_str.replace("Z", "+00:00"))

    def now(self):
        return self.time_val


class MockStateRepository(ABC):
    """Mock implementation of the IStateRepository port."""
    def __init__(self):
        self.candidates = {}
        self.vacancies = {}
        self.queues = {}

    def get_candidate(self, candidate_id):
        return self.candidates.get(candidate_id)

    def save_candidate(self, candidate):
        self.candidates[candidate.id] = candidate

    def get_all_candidates(self):
        return self.candidates

    def get_vacancy(self, vacancy_id):
        return self.vacancies.get(vacancy_id)

    def save_vacancy(self, vacancy):
        self.vacancies[vacancy.id] = vacancy

    def get_all_vacancies(self):
        return self.vacancies

    def get_queue(self, profession_code):
        return self.queues.get(profession_code)

    def save_queue(self, queue):
        self.queues[queue.profession_code] = queue


def test_queue_manager_register_candidate():
    """Verify that QueueManager registers a candidate and puts them in the correct queue in FIFO order."""
    from filavaga.application.services.queue_manager import QueueManager
    from filavaga.core.exceptions import FilaVagaDomainError

    repo = MockStateRepository()
    clock = MockClock("2026-06-15T10:00:00Z")
    manager = QueueManager(repo, clock)

    # 1. Register candidate (Valid)
    candidate = manager.register_candidate(
        name="Maria Silva",
        profession_code="4110-10",
        sector_zone="SUL"
    )

    assert candidate.id.startswith("c_")
    assert candidate.name == "Maria Silva"
    assert candidate.profession_code == "4110-10"
    assert candidate.sector_zone == "SUL"
    assert candidate.registered_at == "2026-06-15T10:00:00+00:00"
    assert candidate.status == "PENDING"

    # Verify candidate saved in repository
    assert repo.get_candidate(candidate.id) == candidate

    # Verify queue created and candidate added
    queue = repo.get_queue("4110-10")
    assert queue is not None
    assert queue.candidate_ids == [candidate.id]

    # 2. Register a second candidate (valid FIFO ordering check)
    clock_2 = MockClock("2026-06-15T09:00:00Z")  # earlier
    manager_2 = QueueManager(repo, clock_2)
    candidate_early = manager_2.register_candidate(
        name="Joao Cedo",
        profession_code="4110-10",
        sector_zone="SUL"
    )

    # Queue must reorder: Joao Cedo registered earlier than Maria Silva
    assert queue.candidate_ids == [candidate_early.id, candidate.id]

    # 3. Validation error on empty name
    with pytest.raises(FilaVagaDomainError):
        manager.register_candidate("", "4110-10", "SUL")

