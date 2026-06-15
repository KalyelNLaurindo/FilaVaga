import os
import pytest
import threading
import json
from filavaga.core.entities import Candidate, Vacancy, Queue

def test_atomic_json_repository_crud(tmp_path):
    """Verify that AtomicJsonRepository can save and retrieve candidates, vacancies and queues correctly."""
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository

    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))

    # 1. Candidate CRUD
    candidate = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    repo.save_candidate(candidate)
    assert repo.get_candidate("c_1") == candidate
    assert repo.get_candidate("c_non_exist") is None
    assert repo.get_all_candidates() == {"c_1": candidate}

    # 2. Vacancy CRUD
    vacancy = Vacancy(
        id="v_1", title="Auxiliar", profession_code="4110-10",
        sector_zone="SUL", capacity=2, created_at="2026-06-15T10:00:00Z",
        expires_at="2026-06-16T10:00:00Z"
    )
    repo.save_vacancy(vacancy)
    assert repo.get_vacancy("v_1") == vacancy
    assert repo.get_vacancy("v_non_exist") is None
    assert repo.get_all_vacancies() == {"v_1": vacancy}

    # 3. Queue CRUD
    queue = Queue(profession_code="4110-10", candidate_ids=["c_1"])
    repo.save_queue(queue)
    assert repo.get_queue("4110-10") == queue
    assert repo.get_queue("7152-10") is None

    # Verify that the physical file was written and can be read back
    # Instantiating a new repository with the same file path should load existing state
    new_repo = AtomicJsonRepository(str(db_file))
    assert new_repo.get_candidate("c_1") == candidate
    assert new_repo.get_vacancy("v_1") == vacancy
    assert new_repo.get_queue("4110-10") == queue


def test_atomic_json_repository_concurrency(tmp_path):
    """Verify that AtomicJsonRepository remains thread-safe during concurrent writes."""
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository

    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))

    def write_worker(worker_id):
        candidate = Candidate(
            id=f"c_{worker_id}", name=f"Worker {worker_id}", sector_zone="SUL",
            profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
        )
        repo.save_candidate(candidate)

    threads = []
    # Launch 20 concurrent threads writing to the repository
    for i in range(20):
        t = threading.Thread(target=write_worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # All 20 candidates must be registered and saved correctly without race conditions
    all_candidates = repo.get_all_candidates()
    assert len(all_candidates) == 20
    for i in range(20):
        assert f"c_{i}" in all_candidates
