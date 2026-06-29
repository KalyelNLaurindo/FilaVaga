"""
Comprehensive integration, edge cases, and robustness tests designed to achieve 100% test coverage.

Author: Kalyel N. Laurindo / Software Engineer
"""

import os
import json
import sys
import shutil
import datetime as dt
import pytest
from unittest.mock import patch, MagicMock
from rich.console import Console

from filavaga.main import main
from filavaga.infra.cli.command_router import ArgparseCLIAdapter
from filavaga.infra.persistence.atomic_json import AtomicJsonRepository, JsonUnitOfWork
from filavaga.infra.translation import TranslationService
from filavaga.core.entities import Candidate, Vacancy, Queue, QueueEntry
from filavaga.core.exceptions import FilaVagaDomainError, EntityNotFoundError
from filavaga.application.services.analytics_service import AnalyticsService
from filavaga.application.services.archive_service import ArchiveService
from filavaga.application.services.config_wizard import ConfigWizardService
from filavaga.application.services.csv_importer import CSVImportService
from filavaga.application.services.queue_manager import QueueManager
from filavaga.application.services.match_engine import MatchEngine
from filavaga.infra.logger import configure_logging


def test_main_entrypoint_execution(tmp_path):
    """Test that main.py boots correctly, parses CLI register command and runs."""
    config_file = tmp_path / "config.json"
    
    # Pre-populate config
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump({
            "database_folder": str(tmp_path),
            "vacancy_ttl_hours": 24,
            "pruning_days": 30,
            "timezone": "UTC",
            "language": "pt",
            "log_level": "INFO"
        }, f)

    # Mock command arguments to run 'register'
    test_args = [
        "main.py",
        "register",
        "--name", "Maria Silva",
        "--cbo", "4110-10",
        "--zone", "SUL"
    ]
    
    with patch("os.path.expanduser", return_value=str(tmp_path)):
        with patch.object(sys, "argv", test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code in (0, None)


def test_interactive_repl_inputs(tmp_path):
    """Test REPL interactive menu options 'c', 'm', 'l' and 'q'."""
    db_folder = tmp_path / "db"
    db_folder.mkdir()
    
    repository = AtomicJsonRepository(filepath=str(db_folder / "state_snapshot.json"))
    
    # Seed vacancy to match
    vacancy = Vacancy(
        id="v_test_repl", title="Carpinteiro", profession_code="5141-10",
        sector_zone="SUL", capacity=1, created_at="2026-06-15T08:00:00Z", expires_at="2026-06-30T08:00:00Z"
    )
    with repository._lock:
        repository._vacancies[vacancy.id] = vacancy
        repository._queues["5141-10"] = Queue(profession_code="5141-10")
        repository._save_state_to_disk()

    register_mock = MagicMock()
    candidate = Candidate(
        id="c_repl_test", name="Repl Candidate", sector_zone="SUL",
        profession_code="5141-10", registered_at="2026-06-15T08:00:00Z", status="PENDING"
    )
    register_mock.register_candidate.return_value = candidate

    match_mock = MagicMock()
    match_mock.match_vacancy.return_value = candidate

    translation_service = TranslationService(default_lang="pt")
    presenter = MagicMock()

    adapter = ArgparseCLIAdapter(
        register_usecase=register_mock,
        match_usecase=match_mock,
        repository=repository,
        presenter=presenter,
        translation_service=translation_service
    )

    inputs = [
        "c", "Repl Candidate", "5141-10", "SUL", "",
        "m", "v_test_repl", "",
        "l", "2",
        "q"
    ]

    with patch("builtins.input", side_effect=inputs):
        adapter._run_interactive_dashboard_loop()

    assert register_mock.register_candidate.called
    assert match_mock.match_vacancy.called
    assert translation_service._active_lang == "en"


def test_persistence_auto_healing_scenarios(tmp_path):
    """Test various auto-healing and isolation corruption paths in AtomicJsonRepository."""
    db_file = tmp_path / "state_snapshot.json"
    bak_file = tmp_path / "state_snapshot.json.bak"
    err_file = tmp_path / "state_snapshot.json.err"
    
    repo = AtomicJsonRepository(filepath=str(db_file))
    cand = Candidate(id="c_1", name="C1", sector_zone="SUL", profession_code="4110-10", registered_at="2026-06-15T08:00:00Z")
    repo.save_candidate(cand)
    
    # Save second to create .bak
    cand2 = Candidate(id="c_2", name="C2", sector_zone="SUL", profession_code="4110-10", registered_at="2026-06-15T08:00:00Z")
    repo.save_candidate(cand2)
    
    assert os.path.exists(bak_file)

    # 1. Precreate corrupt err file to hit os.remove(err_path) line
    with open(err_file, "w") as f:
        f.write("corrupt dummy")

    # 2. Corrupt active snapshot
    with open(db_file, "w") as f:
        f.write("invalid json")

    # This should load from backup after removing old err file and renaming active to err
    healed_repo = AtomicJsonRepository(filepath=str(db_file))
    assert healed_repo.get_candidate("c_1") is not None
    assert os.path.exists(err_file)

    # 3. Simulate rename isolation failure (locks)
    with patch("os.rename", side_effect=OSError("locked")):
        with open(db_file, "w") as f:
            f.write("invalid json")
        # Should catch rename error, log error, and still heal from backup
        healed_repo_rename_fail = AtomicJsonRepository(filepath=str(db_file))
        assert healed_repo_rename_fail.get_candidate("c_1") is not None

    # 4. Simulate restore copy failure
    with patch("shutil.copy2", side_effect=OSError("copy failed")):
        with open(db_file, "w") as f:
            f.write("invalid json")
        # Should log backup restore failure and reset to empty state
        repo_copy_fail = AtomicJsonRepository(filepath=str(db_file))
        assert len(repo_copy_fail.get_all_candidates()) == 0

    # 5. Simulate missing backup altogether
    if os.path.exists(bak_file):
        os.remove(bak_file)
    with open(db_file, "w") as f:
        f.write("invalid json")
    repo_no_bak = AtomicJsonRepository(filepath=str(db_file))
    assert len(repo_no_bak.get_all_candidates()) == 0


def test_permission_hardening_failures():
    """Verify that permission hardening handles OS failures and POSIX paths correctly."""
    repo = AtomicJsonRepository(filepath="dummy_path.json")
    
    # 1. Direct apply permissions on non-existing path
    repo._apply_secure_permissions("non_existent_file.json")
    
    # 2. Mock POSIX path branch
    with patch("os.path.exists", return_value=True):
        with patch("os.name", "posix"):
            with patch("os.chmod", side_effect=PermissionError("chmod disallowed")):
                # Should log warning but not crash
                repo._apply_secure_permissions("some_file.json")

    # 3. Mock Windows icacls subprocess failure
    with patch("os.path.exists", return_value=True):
        with patch("os.name", "nt"):
            with patch("subprocess.run", side_effect=FileNotFoundError("icacls not found")):
                # Should log warning but not crash
                repo._apply_secure_permissions("some_file.json")


def test_queue_manager_validation_checks(tmp_path):
    """Test validation errors in QueueManager application service."""
    repo = AtomicJsonRepository(filepath=str(tmp_path / "state.json"))
    uow = JsonUnitOfWork(repo)
    clock = MagicMock()
    qm = QueueManager(uow, clock)

    with pytest.raises(FilaVagaDomainError, match="Candidate name cannot be empty"):
        qm.register_candidate("", "4110-10", "SUL")

    with pytest.raises(FilaVagaDomainError, match="Profession CBO code cannot be empty"):
        qm.register_candidate("Maria Silva", "", "SUL")

    with pytest.raises(FilaVagaDomainError, match="Sector zone cannot be empty"):
        qm.register_candidate("Maria Silva", "4110-10", "  ")


def test_match_engine_edge_cases(tmp_path):
    """Test match engine behaviors for empty queues, missing candidates and mismatching parameters."""
    repo = AtomicJsonRepository(filepath=str(tmp_path / "state.json"))
    
    # Seed vacancy
    vacancy = Vacancy(
        id="v_empty_q", title="Auxiliar", profession_code="1234-56",
        sector_zone="SUL", capacity=2, created_at="2026-06-15T08:00:00Z", expires_at="2026-06-30T08:00:00Z"
    )
    repo.save_vacancy(vacancy)
    
    uow = JsonUnitOfWork(repo)
    clock = MagicMock()
    clock.now.return_value = dt.datetime.fromisoformat("2026-06-20T12:00:00+00:00")
    me = MatchEngine(uow, clock)

    # 1. No queue matches CBO
    matched = me.match_vacancy("v_empty_q")
    assert matched is None

    # 2. Queue exists but contains an absent candidate ID in repository
    queue = Queue(profession_code="1234-56", entries=[QueueEntry(candidate_id="c_absent", registered_at="2026-06-15T08:00:00Z")])
    repo.save_queue(queue)
    
    matched = me.match_vacancy("v_empty_q")
    assert matched is None

    # 3. Candidate exists in queue but status is not PENDING (already PLACED)
    candidate = Candidate(id="c_placed", name="C Placed", sector_zone="SUL", profession_code="1234-56", registered_at="2026-06-15T08:00:00Z", status="PLACED")
    repo.save_candidate(candidate)
    queue2 = Queue(profession_code="1234-56", entries=[QueueEntry(candidate_id="c_placed", registered_at="2026-06-15T08:00:00Z")])
    repo.save_queue(queue2)
    
    matched = me.match_vacancy("v_empty_q")
    assert matched is None


def test_archive_service_edge_cases(tmp_path):
    """Test archive service candidates date parsing exceptions and missing repository implementation."""
    repo = AtomicJsonRepository(filepath=str(tmp_path / "state.json"))
    # Save candidate with malformed date format
    cand = Candidate(id="c_malformed", name="C Malformed", sector_zone="SUL", profession_code="4110-10", registered_at="invalid-date", status="PLACED")
    repo.save_candidate(cand)

    uow = JsonUnitOfWork(repo)
    clock = MagicMock()
    clock.now.return_value = dt.datetime.fromisoformat("2026-06-20T12:00:00+00:00")
    
    service = ArchiveService(uow, clock)
    # Malformed registered_at should be logged/warned but not raise an error
    archived_count = service.archive_candidates(30)
    assert archived_count == 0

    # Test repository lacking save_archived_candidates capability
    repo_no_archive = MagicMock()
    repo_no_archive.get_all_candidates.return_value = {
        "c_1": Candidate(id="c_1", name="C1", sector_zone="SUL", profession_code="4110-10", registered_at="2026-06-15T08:00:00Z", status="PLACED")
    }
    # Deliberately remove save_archived_candidates attribute
    if hasattr(repo_no_archive, "save_archived_candidates"):
        delattr(repo_no_archive, "save_archived_candidates")
        
    uow_mock = MagicMock()
    uow_mock.repository = repo_no_archive
    service_no_arch = ArchiveService(uow_mock, clock)
    
    # Should warn and return 0 safely
    res = service_no_arch.archive_candidates(0)
    assert res == 0


def test_config_wizard_scenarios(tmp_path):
    """Test interactive config wizard input correction loops and clean dictionary initialization."""
    wizard = ConfigWizardService()
    wizard.config_path = str(tmp_path / "config.json")
    
    # Clean up file
    if os.path.exists(wizard.config_path):
        os.remove(wizard.config_path)

    # Inputs:
    # 1. Directory
    # 2. TTL (first invalid -5, then valid 24)
    # 3. Pruning limit (first invalid 0, then valid 30)
    # 4. Language selection Choices
    # 5. Timezone string (first invalid " ", then America/Sao_Paulo)
    # 6. Logging level choices
    inputs_prompt = ["db_dir", "pt", "  ", "America/Sao_Paulo", "INFO"]
    inputs_int = [-5, 24, 0, 30]

    with patch("rich.prompt.Prompt.ask", side_effect=inputs_prompt):
        with patch("rich.prompt.IntPrompt.ask", side_effect=inputs_int):
            wizard.run_wizard()

    assert os.path.exists(wizard.config_path)
    with open(wizard.config_path, "r") as f:
        cfg = json.load(f)
        assert cfg["persistence"]["directory"] == "db_dir"
        assert cfg["business_rules"]["default_vacancy_ttl_hours"] == 24
        assert cfg["timezone"] == "America/Sao_Paulo"

    # Test reading a corrupted configuration file
    with open(wizard.config_path, "w") as f:
        f.write("{ invalid json config }")
        
    inputs_reentry_prompt = ["db_dir2", "en", "UTC", "DEBUG"]
    inputs_reentry_int = [24, 30]
    
    with patch("rich.prompt.Prompt.ask", side_effect=inputs_reentry_prompt):
        with patch("rich.prompt.IntPrompt.ask", side_effect=inputs_reentry_int):
            wizard.run_wizard()


def test_csv_importer_schema_and_row_failures(tmp_path):
    """Test CSV importer header identification failures, blank rows, missing columns and validation failures."""
    repo = AtomicJsonRepository(filepath=str(tmp_path / "state.json"))
    uow = JsonUnitOfWork(repo)
    clock = MagicMock()
    service = CSVImportService(uow, clock)

    # 1. Invalid CSV headers
    csv_invalid = tmp_path / "invalid.csv"
    with open(csv_invalid, "w", encoding="utf-8") as f:
        f.write("Header1,Header2\nValue1,Value2\n")
        
    with pytest.raises(FilaVagaDomainError, match="Invalid CSV headers"):
        service.import_csv(str(csv_invalid))

    # 2. Candidates CSV with validation failures (shorter rows, empty names, invalid CBO, invalid zones)
    csv_candidates = tmp_path / "candidates_invalid.csv"
    with open(csv_candidates, "w", encoding="utf-8") as f:
        f.write("Nome,CBO,Zona Preferencia,ID\n")
        f.write("\n")  # Empty line
        f.write("Shorter,Row\n")  # Shorter row than headers
        f.write(" ,4110-10,SUL\n")  # Empty name
        f.write("Maria Silva,invalid-cbo,SUL\n")  # Invalid CBO
        f.write("Maria Silva,4110-10,invalid-zone\n")  # Invalid zone
        
    res = service.import_csv(str(csv_candidates))
    assert res == {"candidates": 0, "vacancies": 0}

    # 3. Vacancies CSV with validation failures (missing headers, shorter rows, empty titles, invalid CBO/zone, invalid capacity)
    csv_vacancies = tmp_path / "vacancies_invalid.csv"
    # Header: missing Zone
    with open(csv_vacancies, "w", encoding="utf-8") as f:
        f.write("Titulo,CBO\n")
        f.write("Auxiliar,4110-10\n")
    
    res = service.import_csv(str(csv_vacancies))
    assert res == {"candidates": 0, "vacancies": 0}

    # Header correct, but invalid data
    csv_vacancies_data = tmp_path / "vacancies_data_invalid.csv"
    with open(csv_vacancies_data, "w", encoding="utf-8") as f:
        f.write("Titulo,CBO,Zona,Capacidade\n")
        f.write("Short Row\n")
        f.write(" ,4110-10,SUL,2\n")  # Empty title
        f.write("Vaga,invalid-cbo,SUL,2\n")  # Invalid CBO
        f.write("Vaga,4110-10,invalid-zone,2\n")  # Invalid Zone
        f.write("Vaga,4110-10,SUL,not-integer\n")  # Invalid capacity string
        f.write("Vaga,4110-10,SUL,-1\n")  # Negative capacity

    res = service.import_csv(str(csv_vacancies_data))
    assert res == {"candidates": 0, "vacancies": 0}


def test_analytics_placement_rate_safeguards(tmp_path):
    """Test AnalyticsService division-by-zero safeguards and CSV output writing failures."""
    repo = AtomicJsonRepository(filepath=str(tmp_path / "state.json"))
    uow = JsonUnitOfWork(repo)
    clock = MagicMock()
    clock.now.return_value = dt.datetime.fromisoformat("2026-06-20T12:00:00+00:00")
    
    # 1. Test empty database (zero candidates, zero vacancies)
    service = AnalyticsService(uow, clock)
    out_csv = tmp_path / "report.csv"
    service.export_stats(str(out_csv))
    
    assert os.path.exists(out_csv)
    with open(out_csv, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Placement_Rate" in content

    # 2. Test writing to an invalid target directory with invalid characters (causes OSError disk write failure)
    invalid_csv_path = "report?.csv"
    with pytest.raises(OSError):
        service.export_stats(invalid_csv_path)


def test_atomic_json_archive_file_cases(tmp_path):
    """Test AtomicJsonRepository archive appending when file already exists and when it is corrupted."""
    archive_file = tmp_path / "archive_snapshot.json"
    
    # Pre-create valid archive
    repo = AtomicJsonRepository(filepath=str(tmp_path / "state_snapshot.json"))
    cand = Candidate(id="c_archived", name="Archived Cand", sector_zone="SUL", profession_code="4110-10", registered_at="2026-06-15T08:00:00Z", status="PLACED")
    repo.save_archived_candidates([cand])
    
    assert os.path.exists(archive_file)

    # Append to existing archive
    cand2 = Candidate(id="c_archived2", name="Archived Cand 2", sector_zone="SUL", profession_code="4110-10", registered_at="2026-06-15T08:00:00Z", status="PLACED")
    repo.save_archived_candidates([cand2])
    
    # Test loading corrupted archive (should recover by overwriting/starting fresh)
    with open(archive_file, "w") as f:
        f.write("{ invalid json archive }")
    repo.save_archived_candidates([cand])
