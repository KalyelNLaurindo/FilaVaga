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


def test_atomic_json_repository_auto_healing_decode_error(tmp_path):
    """Verify that AtomicJsonRepository isolates corrupted JSON to .err and restores from .bak."""
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    from filavaga.core.entities import Candidate
    import os
    
    db_file = tmp_path / "state_snapshot.json"
    bak_file = tmp_path / "state_snapshot.json.bak"
    err_file = tmp_path / "state_snapshot.json.err"
    
    # 1. Create a valid initial state to produce a backup
    repo = AtomicJsonRepository(str(db_file))
    candidate = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    repo.save_candidate(candidate)
    # Save a second time to ensure backup is created
    repo.save_candidate(candidate)
    
    # Verify .bak exists and is valid
    assert os.path.exists(bak_file)
    
    # 2. Corrupt the active database file (write invalid JSON syntax)
    with open(db_file, "w", encoding="utf-8") as f:
        f.write("{invalid_json_here")
        
    # 3. Instantiate a new repository which will load from disk, trigger decode error, and heal itself
    new_repo = AtomicJsonRepository(str(db_file))
    
    # Verify that the corrupt file was isolated to .err
    assert os.path.exists(err_file)
    with open(err_file, "r", encoding="utf-8") as f:
        assert f.read() == "{invalid_json_here"
        
    # Verify that state was restored from backup successfully
    assert new_repo.get_candidate("c_1") == candidate


def test_atomic_json_repository_auto_healing_schema_error(tmp_path):
    """Verify that AtomicJsonRepository isolates JSON violating schema rules and restores from .bak."""
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    from filavaga.core.entities import Candidate
    import os
    import json
    
    db_file = tmp_path / "state_snapshot.json"
    bak_file = tmp_path / "state_snapshot.json.bak"
    err_file = tmp_path / "state_snapshot.json.err"
    
    # 1. Create a valid initial state
    repo = AtomicJsonRepository(str(db_file))
    candidate = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    repo.save_candidate(candidate)
    # Save a second time to ensure backup is created
    repo.save_candidate(candidate)
    
    # 2. Corrupt active file with a valid JSON but missing the candidates schema section
    corrupt_schema = {"metadata": {"app_id": "filavaga-sine-local", "schema_version": "1.0"}}
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(corrupt_schema, f)
        
    # 3. Instantiate new repository triggering validation error and backup recovery
    new_repo = AtomicJsonRepository(str(db_file))
    
    # Verify isolation and recovery
    assert os.path.exists(err_file)
    assert new_repo.get_candidate("c_1") == candidate


def test_atomic_json_repository_auto_healing_no_backup(tmp_path):
    """Verify that if both active and backup are corrupt or missing, it falls back to empty state."""
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    import os
    
    db_file = tmp_path / "state_snapshot.json"
    
    # Write corrupt JSON with no backup file present
    with open(db_file, "w", encoding="utf-8") as f:
        f.write("{corrupt_and_no_backup")
        
    new_repo = AtomicJsonRepository(str(db_file))
    
    # Verify that it isolated the file and initialized empty structures
    assert os.path.exists(tmp_path / "state_snapshot.json.err")
    assert len(new_repo.get_all_candidates()) == 0


def test_argparse_cli_adapter_purge_all(tmp_path, capsys):
    """Verify that ArgparseCLIAdapter routes purge-all command, shreds files, and deletes them."""
    from filavaga.infra.cli.command_router import ArgparseCLIAdapter
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    from filavaga.core.entities import Candidate
    import os
    
    db_file = tmp_path / "state_snapshot.json"
    bak_file = tmp_path / "state_snapshot.json.bak"
    err_file = tmp_path / "state_snapshot.json.err"
    
    # 1. Setup repository and create some initial candidate data to write db and bak
    repo = AtomicJsonRepository(str(db_file))
    candidate = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    repo.save_candidate(candidate)
    repo.save_candidate(candidate)  # Creates backup file
    
    # Create fake .err file to make sure it gets cleaned up too
    with open(err_file, "w", encoding="utf-8") as f:
        f.write("fake error dump")
        
    # Verify files exist before purge
    assert os.path.exists(db_file)
    assert os.path.exists(bak_file)
    assert os.path.exists(err_file)
    
    adapter = ArgparseCLIAdapter(None, None, repository=repo)
    
    # Run purge-all
    adapter.run(["purge-all"])
    
    # 3. Assert all files are deleted
    assert not os.path.exists(db_file)
    assert not os.path.exists(bak_file)
    assert not os.path.exists(err_file)
    
    captured = capsys.readouterr()
    assert "Success" in captured.out or "Purge" in captured.out


def test_atomic_json_repository_secure_permissions_posix(tmp_path):
    """Verify that AtomicJsonRepository enforces POSIX 0700/0600 folder/file permissions."""
    import sys
    if sys.platform == "win32":
        pytest.skip("POSIX permissions test skipped on Windows")
        
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    from filavaga.core.entities import Candidate
    import stat
    
    db_dir = tmp_path / "subdir"
    db_file = db_dir / "state_snapshot.json"
    
    repo = AtomicJsonRepository(str(db_file))
    candidate = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    repo.save_candidate(candidate)
    
    # Verify directory has 0700
    dir_mode = os.stat(str(db_dir)).st_mode
    assert stat.S_IMODE(dir_mode) == 0o700
    
    # Verify database file has 0600
    file_mode = os.stat(str(db_file)).st_mode
    assert stat.S_IMODE(file_mode) == 0o600
    
    # Save again to trigger backup creation
    repo.save_candidate(candidate)
    
    bak_file = db_dir / "state_snapshot.json.bak"
    assert os.path.exists(bak_file)
    bak_mode = os.stat(str(bak_file)).st_mode
    assert stat.S_IMODE(bak_mode) == 0o600


def test_atomic_json_repository_secure_permissions_windows(tmp_path):
    """Verify that AtomicJsonRepository restricts Windows DACLs to current user and SYSTEM."""
    import sys
    if sys.platform != "win32":
        pytest.skip("Windows permissions test skipped on POSIX")
        
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    from filavaga.core.entities import Candidate
    import subprocess
    import getpass
    
    db_dir = tmp_path / "subdir"
    db_file = db_dir / "state_snapshot.json"
    
    repo = AtomicJsonRepository(str(db_file))
    candidate = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    repo.save_candidate(candidate)
    repo.save_candidate(candidate)  # Trigger backup file
    
    # Let's inspect permissions using icacls
    # We check that icacls output on db_file does not contain "Users" or "Everyone" or "(I)"
    result = subprocess.run(["icacls", str(db_file)], capture_output=True, text=True, check=True)
    output = result.stdout
    
    # Verify inheritance is disabled (no (I) flag in any access control entries)
    assert "(I)" not in output
    
    # Also verify that SYSTEM or current user is explicitly granted access
    username = getpass.getuser()
    assert username.lower() in output.lower() or os.environ.get("USERNAME", "").lower() in output.lower()
    
    # Check directory as well
    dir_result = subprocess.run(["icacls", str(db_dir)], capture_output=True, text=True, check=True)
    dir_output = dir_result.stdout
    assert "(I)" not in dir_output


def test_atomic_json_repository_mutability_protection(tmp_path):
    """Verify that AtomicJsonRepository protects against reference leaks and state mutation."""
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository
    from filavaga.core.entities import Candidate, Vacancy, Queue
    
    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))
    
    # 1. Test Candidate Mutability Protection (Read Isolation)
    candidate = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    repo.save_candidate(candidate)
    
    retrieved_candidate = repo.get_candidate("c_1")
    # Mutate the returned candidate directly (without saving)
    retrieved_candidate.name = "Modified Name"
    
    # Retrieving it again should return the original name
    assert repo.get_candidate("c_1").name == "Maria Silva"
    
    # 2. Test Candidate Mutability Protection (Write Isolation)
    candidate.name = "Another Name"
    repo.save_candidate(candidate)
    # Mutate original candidate object after save
    candidate.name = "Mutated After Save"
    assert repo.get_candidate("c_1").name == "Another Name"
    
    # 3. Test get_all_candidates isolation
    all_candidates = repo.get_all_candidates()
    all_candidates["c_1"].name = "Mutated in dict"
    assert repo.get_candidate("c_1").name == "Another Name"

    # 4. Test Vacancy Mutability Protection (Read & Write Isolation)
    vacancy = Vacancy(
        id="v_1", title="Auxiliar", profession_code="4110-10",
        sector_zone="SUL", capacity=2, created_at="2026-06-15T10:00:00Z",
        expires_at="2026-06-16T10:00:00Z"
    )
    repo.save_vacancy(vacancy)
    retrieved_vacancy = repo.get_vacancy("v_1")
    retrieved_vacancy.capacity = 10
    assert repo.get_vacancy("v_1").capacity == 2
    
    vacancy.capacity = 5
    repo.save_vacancy(vacancy)
    vacancy.capacity = 20
    assert repo.get_vacancy("v_1").capacity == 5
    
    # 5. Test Queue Mutability Protection (Read & Write Isolation)
    queue = Queue(profession_code="4110-10", candidate_ids=["c_1"])
    repo.save_queue(queue)
    retrieved_queue = repo.get_queue("4110-10")
    retrieved_queue.candidate_ids.append("c_2")
    assert repo.get_queue("4110-10").candidate_ids == ["c_1"]
    
    queue.candidate_ids.append("c_3")
    repo.save_queue(queue)
    queue.candidate_ids.append("c_4")
    assert repo.get_queue("4110-10").candidate_ids == ["c_1", "c_3"]


def test_json_unit_of_work_commit_and_rollback(tmp_path):
    """Verify that JsonUnitOfWork commits changes successfully and rolls back on exceptions."""
    from filavaga.infra.persistence.atomic_json import AtomicJsonRepository, JsonUnitOfWork
    from filavaga.core.entities import Candidate
    import os
    
    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))
    uow = JsonUnitOfWork(repo)
    
    candidate = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    
    # 1. Test Rollback on Exception
    try:
        with uow:
            uow.repository.save_candidate(candidate)
            assert uow.repository.get_candidate("c_1") == candidate
            raise ValueError("Simulated error to trigger rollback")
    except ValueError:
        pass
        
    # The candidate must have been rolled back from repository memory cache
    assert repo.get_candidate("c_1") is None
    # No file must have been written to disk
    assert not os.path.exists(db_file)
    
    # 2. Test Success Commit
    with uow:
        uow.repository.save_candidate(candidate)
        uow.commit()
        
    # The candidate is saved in memory
    assert repo.get_candidate("c_1") == candidate
    # File is written to disk
    assert os.path.exists(db_file)
    
    # 3. Verify read consistency after rollback
    candidate2 = Candidate(
        id="c_2", name="Joao Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T08:00:00Z"
    )
    try:
        with uow:
            uow.repository.save_candidate(candidate2)
            raise ValueError("Rollback c_2")
    except ValueError:
        pass
        
    # c_1 still exists, c_2 does not
    assert repo.get_candidate("c_1") == candidate
    assert repo.get_candidate("c_2") is None








