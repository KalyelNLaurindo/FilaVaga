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


def test_system_clock_utc_timezone():
    """Verify that SystemClock returns a timezone-aware UTC datetime and matches format."""
    from filavaga.infra.persistence.system_clock import SystemClock
    from datetime import datetime, timezone

    clock = SystemClock()
    now_val = clock.now()

    assert isinstance(now_val, datetime)
    assert now_val.tzinfo is not None
    assert now_val.tzinfo.utcoffset(now_val) == timezone.utc.utcoffset(now_val)
    
    # Verify it produces valid ISO-8601 string containing +00:00 (since it is UTC timezone-aware)
    iso_str = now_val.isoformat()
    assert "+00:00" in iso_str


def test_system_clock_override_and_mocking():
    """Verify that SystemClock supports overriding for test isolation."""
    from filavaga.infra.persistence.system_clock import SystemClock
    from datetime import datetime, timezone

    # 1. Override via instantiation parameter
    fixed_time = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    clock_fixed = SystemClock(override_time=fixed_time)
    
    assert clock_fixed.now() == fixed_time
    assert clock_fixed.now().isoformat() == "2026-06-15T12:00:00+00:00"


def test_argparse_cli_adapter_register(tmp_path, capsys):
    """Verify that ArgparseCLIAdapter routes register commands and prints output."""
    from filavaga.infra.cli.command_router import ArgparseCLIAdapter
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    from filavaga.infra.persistence.system_clock import SystemClock
    from filavaga.application.services.queue_manager import QueueManager
    from datetime import datetime, timezone
    
    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))
    clock = SystemClock(override_time=datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc))
    manager = QueueManager(repo, clock)
    
    adapter = ArgparseCLIAdapter(register_usecase=manager, match_usecase=None)
    
    # Execute routing
    adapter.run(["register", "--name", "Maria Silva", "--cbo", "4110-10", "--zone", "SUL"])
    
    captured = capsys.readouterr()
    assert "Maria Silva" in captured.out
    assert "4110-10" in captured.out
    assert "SUL" in captured.out
    
    # Verify candidate actually exists in repository
    all_candidates = repo.get_all_candidates()
    assert len(all_candidates) == 1
    candidate = list(all_candidates.values())[0]
    assert candidate.name == "Maria Silva"
    assert candidate.profession_code == "4110-10"
    assert candidate.sector_zone == "SUL"


def test_argparse_cli_adapter_match(tmp_path, capsys):
    """Verify that ArgparseCLIAdapter routes match commands and prints output."""
    from filavaga.infra.cli.command_router import ArgparseCLIAdapter
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    from filavaga.infra.persistence.system_clock import SystemClock
    from filavaga.application.services.match_engine import MatchEngine
    from filavaga.core.entities import Candidate, Vacancy, Queue
    from datetime import datetime, timezone
    
    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))
    clock = SystemClock(override_time=datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc))
    engine = MatchEngine(repo, clock)
    
    # Setup state
    vacancy = Vacancy(
        id="v_01", title="Auxiliar", profession_code="4110-10",
        sector_zone="SUL", capacity=2, created_at="2026-06-15T10:00:00Z",
        expires_at="2026-06-16T10:00:00Z"
    )
    repo.save_vacancy(vacancy)
    
    c_a = Candidate(
        id="c_a", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z",
        status="PENDING"
    )
    repo.save_candidate(c_a)
    
    queue = Queue(profession_code="4110-10", candidate_ids=["c_a"])
    repo.save_queue(queue)
    
    adapter = ArgparseCLIAdapter(register_usecase=None, match_usecase=engine)
    
    # Execute routing
    adapter.run(["match", "--id", "v_01"])
    
    captured = capsys.readouterr()
    assert "Maria Silva" in captured.out
    assert "v_01" in captured.out
    
    # Verify vacancy capacity updated
    updated_vacancy = repo.get_vacancy("v_01")
    assert updated_vacancy.placed_candidate_ids == ["c_a"]


def test_argparse_cli_adapter_help(capsys):
    """Verify that ArgparseCLIAdapter prints help when requested."""
    from filavaga.infra.cli.command_router import ArgparseCLIAdapter
    import pytest
    
    adapter = ArgparseCLIAdapter(None, None)
    
    with pytest.raises(SystemExit):
        adapter.run(["--help"])
        
    captured = capsys.readouterr()
    assert "register" in captured.out or "register" in captured.err
    assert "match" in captured.out or "match" in captured.err


def test_presenter_layouts():
    """Verify that RichConsolePresenter renders candidate registration, matches, and errors correctly."""
    from filavaga.infra.cli.presenter import RichConsolePresenter
    from filavaga.core.entities import Candidate
    from rich.console import Console
    
    console = Console(record=True, width=80)
    presenter = RichConsolePresenter(console=console)
    
    # 1. Test candidate registration rendering
    candidate = Candidate(
        id="c_test", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T12:00:00+00:00"
    )
    presenter.display_candidate_registration(candidate)
    output = console.export_text()
    assert "Maria Silva" in output
    assert "4110-10" in output
    assert "SUL" in output
    assert "PENDING" in output
    
    # 2. Test vacancy match rendering
    presenter.display_vacancy_match(vacancy_id="v_01", candidate=candidate)
    output = console.export_text()
    assert "v_01" in output
    assert "Maria Silva" in output
    
    # 3. Test no match rendering
    presenter.display_no_match(vacancy_id="v_01")
    output = console.export_text()
    assert "v_01" in output
    assert "No matching candidate" in output
    
    # 4. Test error rendering
    presenter.display_error("Domain Error", "Candidate already exists")
    output = console.export_text()
    assert "Domain Error" in output
    assert "Candidate already exists" in output


def test_presenter_dashboard():
    """Verify that RichConsolePresenter renders the dashboard table grid correctly."""
    from filavaga.infra.cli.presenter import RichConsolePresenter
    from filavaga.core.entities import Candidate, Vacancy, Queue
    from rich.console import Console
    
    console = Console(record=True, width=80)
    presenter = RichConsolePresenter(console=console)
    
    # Mock data indexes
    candidates = {
        "c_1": Candidate(
            id="c_1", name="Maria Silva", sector_zone="SUL",
            profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
        )
    }
    vacancies = {
        "v_1": Vacancy(
            id="v_1", title="Auxiliar", profession_code="4110-10",
            sector_zone="SUL", capacity=2, created_at="2026-06-15T10:00:00Z",
            expires_at="2026-06-16T10:00:00Z"
        )
    }
    queues = {
        "4110-10": Queue(profession_code="4110-10", candidate_ids=["c_1"])
    }
    
    presenter.display_dashboard(candidates, vacancies, queues)
    output = console.export_text()
    
    assert "Maria Silva" in output
    assert "4110-10" in output
    assert "v_1" in output
    assert "Auxiliar" in output


def test_json_logging_format_and_stderr(capsys):
    """Verify that configure_logging sets up structured JSON logs writing exclusively to stderr."""
    from filavaga.infra.logger import configure_logging
    import logging
    import json
    
    # Configure logging
    configure_logging(level=logging.DEBUG)
    
    logger = logging.getLogger("filavaga")
    
    # 1. Log a message
    logger.info("Test info message")
    
    captured = capsys.readouterr()
    
    # Verify stdout is clean
    assert captured.out == ""
    
    # Verify stderr contains JSON
    err_lines = captured.err.strip().split("\n")
    assert len(err_lines) >= 1
    
    log_record = json.loads(err_lines[-1])
    assert "timestamp" in log_record
    assert log_record["level"] == "INFO"
    assert log_record["message"] == "Test info message"
    
    # 2. Log an exception
    try:
        raise ValueError("Simulated error")
    except ValueError:
        logger.exception("Something went wrong")
        
    captured_err = capsys.readouterr()
    err_lines_exc = captured_err.err.strip().split("\n")
    log_record_exc = json.loads(err_lines_exc[-1])
    
    assert log_record_exc["level"] == "ERROR"
    assert log_record_exc["message"] == "Something went wrong"
    assert "ValueError: Simulated error" in log_record_exc["exception"]



