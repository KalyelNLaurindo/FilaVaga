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
        IUnitOfWork,
    )

    assert issubclass(IRegisterCandidateUseCase, ABC)
    assert issubclass(IMatchVacancyUseCase, ABC)
    assert issubclass(IClock, ABC)
    assert issubclass(IStateRepository, ABC)
    assert issubclass(IUnitOfWork, ABC)

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


class MockUnitOfWork(ABC):
    """Mock implementation of the IUnitOfWork port."""
    def __init__(self, repository):
        self._repository = repository
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    @property
    def repository(self):
        return self._repository


def test_queue_manager_register_candidate():
    """Verify that QueueManager registers a candidate and puts them in the correct queue in FIFO order."""
    from filavaga.application.services.queue_manager import QueueManager
    from filavaga.core.exceptions import FilaVagaDomainError

    repo = MockStateRepository()
    uow = MockUnitOfWork(repo)
    clock = MockClock("2026-06-15T10:00:00Z")
    manager = QueueManager(uow, clock)

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
    uow_2 = MockUnitOfWork(repo)
    manager_2 = QueueManager(uow_2, clock_2)
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


def test_match_engine_scenarios():
    """Verify that MatchEngine implements all matching heuristics, TTL validation and capacity locks."""
    from filavaga.application.services.match_engine import MatchEngine
    from filavaga.core.entities import Candidate, Vacancy, Queue, QueueEntry
    from filavaga.core.exceptions import (
        EntityNotFoundError,
        EntityExpiredError,
        CapacityLimitExceededError,
    )

    repo = MockStateRepository()
    uow = MockUnitOfWork(repo)
    clock = MockClock("2026-06-15T12:00:00Z")
    engine = MatchEngine(uow, clock)

    # 1. Non-existent vacancy raises EntityNotFoundError
    with pytest.raises(EntityNotFoundError):
        engine.match_vacancy("v_non_exist")

    # 2. Setup mock vacancy
    vacancy = Vacancy(
        id="v_01", title="Auxiliar", profession_code="4110-10",
        sector_zone="SUL", capacity=2, created_at="2026-06-15T10:00:00Z",
        expires_at="2026-06-16T10:00:00Z"
    )
    repo.save_vacancy(vacancy)

    # 3. Setup candidates
    # C_A: Valid CBO and Zone, registered early
    c_a = Candidate(
        id="c_a", name="Candidate A", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z",
        status="PENDING"
    )
    # C_B: Valid CBO but different Zone (NORTE)
    c_b = Candidate(
        id="c_b", name="Candidate B", sector_zone="NORTE",
        profession_code="4110-10", registered_at="2026-06-15T08:30:00Z",
        status="PENDING"
    )
    # C_C: Valid CBO and Zone, registered late
    c_c = Candidate(
        id="c_c", name="Candidate C", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T09:00:00Z",
        status="PENDING"
    )

    repo.save_candidate(c_a)
    repo.save_candidate(c_b)
    repo.save_candidate(c_c)

    queue = Queue(
        profession_code="4110-10",
        entries=[
            QueueEntry(candidate_id="c_a", registered_at="2026-06-15T08:00:00Z"),
            QueueEntry(candidate_id="c_b", registered_at="2026-06-15T08:30:00Z"),
            QueueEntry(candidate_id="c_c", registered_at="2026-06-15T09:00:00Z")
        ]
    )
    repo.save_queue(queue)

    # First match: should pick C_A (early, matches zone SUL)
    matched_1 = engine.match_vacancy("v_01")
    assert matched_1 == c_a
    assert matched_1.status == "CONTACTED"
    assert vacancy.placed_candidate_ids == ["c_a"]

    # Second match: should pick C_C (skips C_B because zone doesn't match; skips C_A because status is CONTACTED)
    matched_2 = engine.match_vacancy("v_01")
    assert matched_2 == c_c
    assert matched_2.status == "CONTACTED"
    assert vacancy.placed_candidate_ids == ["c_a", "c_c"]
    assert vacancy.is_full()

    # Third match on a full vacancy: raises CapacityLimitExceededError
    with pytest.raises(CapacityLimitExceededError):
        engine.match_vacancy("v_01")

    # 4. Try match on an expired vacancy: raises EntityExpiredError
    vacancy_expired = Vacancy(
        id="v_exp", title="Auxiliar Exp", profession_code="4110-10",
        sector_zone="SUL", capacity=2, created_at="2026-06-15T10:00:00Z",
        expires_at="2026-06-16T10:00:00Z"
    )
    repo.save_vacancy(vacancy_expired)

    # Advance clock beyond expiration time
    clock_expired = MockClock("2026-06-17T12:00:00Z")
    uow_expired = MockUnitOfWork(repo)
    engine_expired = MatchEngine(uow_expired, clock_expired)

    with pytest.raises(EntityExpiredError):
        engine_expired.match_vacancy("v_exp")


