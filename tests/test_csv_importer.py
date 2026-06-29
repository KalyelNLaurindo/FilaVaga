"""
Unit tests for the CSV Data Import Adapter (TSK-18).

Ensures FilaVaga can import candidates and vacancies from CSV files,
handles case-insensitive headers, performs row-by-row validation,
writes syntax/validation errors to standard error, and excludes PII.

Author: Kalyel N. Laurindo / Software Engineer
"""

import io
import sys
import pytest
from unittest.mock import MagicMock
from filavaga.application.services.csv_importer import CSVImportService
from filavaga.core.exceptions import FilaVagaDomainError
from filavaga.core.entities import Candidate, Vacancy, Queue
from tests.test_usecases import MockClock, MockStateRepository, MockUnitOfWork


def test_import_candidates_success(tmp_path):
    """Verify successful candidates CSV import, setting FIFO queues and omitting extra PII."""
    csv_file = tmp_path / "candidates.csv"
    csv_content = (
        "Name,CBO,Zone,CPF,Phone,Registration_Date\n"
        "Alice Smith,4110-10,SUL,123.456.789-00,555-1234,2026-06-15T09:00:00Z\n"
        "Bob Jones,4110-10,NORTE,987.654.321-11,555-5678,2026-06-15T08:00:00Z\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    clock = MockClock()
    repository = MockStateRepository()
    uow = MockUnitOfWork(repository)
    service = CSVImportService(uow, clock)

    res = service.import_csv(str(csv_file))
    assert res == {"candidates": 2, "vacancies": 0}

    # Verify candidates are persisted
    all_candidates = repository.get_all_candidates()
    assert len(all_candidates) == 2

    # Check mapping
    alice = next(c for c in all_candidates.values() if c.name == "Alice Smith")
    assert alice.profession_code == "4110-10"
    assert alice.sector_zone == "SUL"
    assert alice.registered_at == "2026-06-15T09:00:00Z"
    assert alice.status == "PENDING"
    # Ensure CPF and Phone are NOT present in candidate properties (LGPD Compliance)
    assert not hasattr(alice, "cpf")
    assert not hasattr(alice, "phone")

    bob = next(c for c in all_candidates.values() if c.name == "Bob Jones")
    assert bob.profession_code == "4110-10"
    assert bob.sector_zone == "NORTE"
    assert bob.registered_at == "2026-06-15T08:00:00Z"

    # Verify FIFO queue sorting chronology
    queue = repository.get_queue("4110-10")
    assert queue is not None
    # Bob has registered_at 08:00:00Z (earlier) and Alice has 09:00:00Z (later)
    # Queue should be [Bob, Alice]
    assert queue.candidate_ids == [bob.id, alice.id]


def test_import_vacancies_success(tmp_path):
    """Verify successful vacancies CSV import, configuring capacities and expiration dates."""
    csv_file = tmp_path / "vacancies.csv"
    csv_content = (
        "Title,CBO,Zone,Capacity,Expires_At\n"
        "Receptionist,4110-10,SUL,3,2026-06-16T10:00:00Z\n"
        "Bricklayer,7152-10,NORTE,1,2026-06-17T12:00:00Z\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    clock = MockClock()
    repository = MockStateRepository()
    uow = MockUnitOfWork(repository)
    service = CSVImportService(uow, clock)

    res = service.import_csv(str(csv_file))
    assert res == {"candidates": 0, "vacancies": 2}

    # Verify vacancies are persisted
    all_vacancies = repository.get_all_vacancies()
    assert len(all_vacancies) == 2

    v1 = next(v for v in all_vacancies.values() if v.title == "Receptionist")
    assert v1.profession_code == "4110-10"
    assert v1.sector_zone == "SUL"
    assert v1.capacity == 3
    assert v1.expires_at == "2026-06-16T10:00:00Z"

    v2 = next(v for v in all_vacancies.values() if v.title == "Bricklayer")
    assert v2.profession_code == "7152-10"
    assert v2.sector_zone == "NORTE"
    assert v2.capacity == 1
    assert v2.expires_at == "2026-06-17T12:00:00Z"


def test_import_row_by_row_validation_reports_to_stderr(tmp_path):
    """Verify that rows with validation errors are printed to stderr and skipped, but valid rows import."""
    csv_file = tmp_path / "mixed.csv"
    csv_content = (
        "Name,CBO,Zone\n"
        "Valid Candidate,4110-10,SUL\n"
        "Invalid CBO Candidate,invalid-cbo,SUL\n"
        "Invalid Zone Candidate,4110-10,INVALID_ZONE\n"
        "Another Valid,7152-10,NORTE\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    clock = MockClock()
    repository = MockStateRepository()
    uow = MockUnitOfWork(repository)
    service = CSVImportService(uow, clock)

    # Capture stderr
    stderr_buffer = io.StringIO()
    sys.stderr = stderr_buffer

    try:
        res = service.import_csv(str(csv_file))
    finally:
        sys.stderr = sys.__stderr__

    assert res == {"candidates": 2, "vacancies": 0}
    
    # Assert errors were logged to stderr with row numbers (1-indexed, header is row 1)
    err_output = stderr_buffer.getvalue()
    assert "Row 3" in err_output
    assert "Row 4" in err_output
    assert "invalid-cbo" in err_output
    assert "INVALID_ZONE" in err_output

    # Valid candidates should be registered
    all_candidates = repository.get_all_candidates()
    assert len(all_candidates) == 2
    assert any(c.name == "Valid Candidate" for c in all_candidates.values())
    assert any(c.name == "Another Valid" for c in all_candidates.values())


def test_import_case_insensitive_headers(tmp_path):
    """Verify case-insensitive header matching works regardless of column capitalization or casing."""
    csv_file = tmp_path / "casing.csv"
    csv_content = (
        "NaMe,cBo_CoDe,zOnA_pReFeReNcIa\n"
        "Alice Smith,4110-10,SUL\n"
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    clock = MockClock()
    repository = MockStateRepository()
    uow = MockUnitOfWork(repository)
    service = CSVImportService(uow, clock)

    res = service.import_csv(str(csv_file))
    assert res == {"candidates": 1, "vacancies": 0}

    all_candidates = repository.get_all_candidates()
    assert len(all_candidates) == 1
    alice = list(all_candidates.values())[0]
    assert alice.name == "Alice Smith"
    assert alice.profession_code == "4110-10"
    assert alice.sector_zone == "SUL"


def test_command_router_import_csv(tmp_path):
    """Verify that ArgparseCLIAdapter routes 'import-csv' subcommand correctly."""
    csv_file = tmp_path / "import_test.csv"
    csv_file.write_text("Name,CBO,Zone\nJohn Doe,4110-10,SUL\n", encoding="utf-8")

    from filavaga.infra.translation import TranslationService
    from filavaga.infra.cli.command_router import ArgparseCLIAdapter
    service = TranslationService(locales_dir=str(tmp_path), default_lang="pt")
    
    mock_import = MagicMock()
    mock_import.import_csv.return_value = {"candidates": 1, "vacancies": 0}

    adapter = ArgparseCLIAdapter(
        None, None, translation_service=service, import_usecase=mock_import
    )

    adapter.run(["import-csv", "--file", str(csv_file)])
    mock_import.import_csv.assert_called_once_with(filepath=str(csv_file))
