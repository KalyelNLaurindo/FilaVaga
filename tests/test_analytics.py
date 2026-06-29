"""
Unit tests for the anonymized placement stats analytics CSV export (TSK-21).

Author: Kalyel N. Laurindo / Software Engineer
"""

import os
import json
import pytest
import csv
from unittest.mock import patch, MagicMock
from filavaga.infra.persistence.atomic_json import AtomicJsonRepository, JsonUnitOfWork
from filavaga.infra.persistence.system_clock import SystemClock
from filavaga.core.entities import Candidate, Vacancy, Queue, QueueEntry
from filavaga.application.services.analytics_service import AnalyticsService
from filavaga.infra.cli.command_router import ArgparseCLIAdapter


class MockClock:
    """Mock clock for precise datetime calculations in testing."""
    def __init__(self, now_str: str):
        import datetime as dt
        self._now = dt.datetime.fromisoformat(now_str.replace("Z", "+00:00"))

    def now(self):
        return self._now


def test_analytics_empty_database_no_division_by_zero(tmp_path):
    """Verify that export works on an empty repository without division-by-zero errors."""
    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))
    uow = JsonUnitOfWork(repo)
    clock = SystemClock()

    service = AnalyticsService(uow, clock)
    csv_file = tmp_path / "stats.csv"

    # Execution should not raise any math error
    service.export_stats(str(csv_file))

    # Verify that file has been written with header
    assert os.path.exists(csv_file)
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0] == [
        "Sector_Zone",
        "CBO_Code",
        "Total_Candidates",
        "Placed_Candidates",
        "Placement_Rate",
        "Average_Wait_Time_Seconds",
        "Average_Fulfillment_Time_Seconds",
    ]


def test_analytics_wait_time_and_fulfillment_calculations(tmp_path):
    """Verify metrics calculation logic (wait times, fulfillment speed, placement rates)."""
    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))
    uow = JsonUnitOfWork(repo)

    # Mock Clock is set to 2026-06-20T12:00:00Z
    clock = MockClock("2026-06-20T12:00:00Z")

    # Group: Zone 'SUL', CBO '4110-10'
    # 1. Candidate 1 (Placed): registered 2026-06-18T10:00:00Z.
    #    Matched to Vacancy created at 2026-06-19T10:00:00Z (wait time = 1 day = 86400s).
    #    Vacancy fulfillment time: since candidate registered before vacancy creation, it is instant (0s).
    c1 = Candidate(
        id="c_1", name="Maria Silva", sector_zone="SUL", profession_code="4110-10",
        registered_at="2026-06-18T10:00:00Z", status="PLACED"
    )

    # 2. Candidate 2 (Placed): registered 2026-06-19T12:00:00Z (after vacancy was created).
    #    Matched to Vacancy created at 2026-06-19T10:00:00Z.
    #    Wait time: candidate registered after vacancy was created -> matched instantly -> wait time = 0s.
    #    Vacancy fulfillment time: vacancy was waiting from 2026-06-19T10:00:00Z until candidate registered at T+2h (7200s).
    c2 = Candidate(
        id="c_2", name="Joao Souza", sector_zone="SUL", profession_code="4110-10",
        registered_at="2026-06-19T12:00:00Z", status="PLACED"
    )

    # 3. Candidate 3 (Pending): registered 2026-06-19T12:00:00Z.
    #    Still active waiting until clock.now() (2026-06-20T12:00:00Z).
    #    Wait time: 2026-06-20T12:00:00Z - 2026-06-19T12:00:00Z = 24 hours (86400s).
    c3 = Candidate(
        id="c_3", name="Ana Dias", sector_zone="SUL", profession_code="4110-10",
        registered_at="2026-06-19T12:00:00Z", status="PENDING"
    )

    # Vacancy: created 2026-06-19T10:00:00Z. Placed candidates: c_1, c_2.
    v1 = Vacancy(
        id="v_1", title="Auxiliar", profession_code="4110-10", sector_zone="SUL",
        capacity=3, created_at="2026-06-19T10:00:00Z", expires_at="2026-06-25T10:00:00Z",
        placed_candidate_ids=["c_1", "c_2"]
    )

    # Save entities
    with uow:
        repo.save_candidate(c1)
        repo.save_candidate(c2)
        repo.save_candidate(c3)
        repo.save_vacancy(v1)
        uow.commit()

    service = AnalyticsService(uow, clock)
    csv_file = tmp_path / "stats.csv"
    service.export_stats(str(csv_file))

    # Read output
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1
    row = rows[0]

    assert row["Sector_Zone"] == "SUL"
    assert row["CBO_Code"] == "4110-10"
    assert int(row["Total_Candidates"]) == 3
    assert int(row["Placed_Candidates"]) == 2
    assert float(row["Placement_Rate"]) == pytest.approx(2.0 / 3.0)

    # Wait times:
    # c_1 wait time = 86400s
    # c_2 wait time = 0s
    # c_3 wait time = 86400s
    # Average wait time = (86400 + 0 + 86400) / 3 = 57600s
    assert float(row["Average_Wait_Time_Seconds"]) == pytest.approx(57600.0)

    # Fulfillment speeds:
    # placement c_1 fulfillment time = 0s (instant)
    # placement c_2 fulfillment time = 7200s (2 hours)
    # Average fulfillment time = (0 + 7200) / 2 = 3600s
    assert float(row["Average_Fulfillment_Time_Seconds"]) == pytest.approx(3600.0)


def test_analytics_anonymization_lgpd_compliance(tmp_path):
    """Verify that no PII (names, candidate IDs) is leaked in the exported CSV."""
    db_file = tmp_path / "state_snapshot.json"
    repo = AtomicJsonRepository(str(db_file))
    uow = JsonUnitOfWork(repo)
    clock = SystemClock()

    c1 = Candidate(
        id="candidate-unique-id-999", name="Luiz Inacio", sector_zone="NORTE",
        profession_code="3120-10", registered_at="2026-06-15T08:00:00Z", status="PLACED"
    )
    with uow:
        repo.save_candidate(c1)
        uow.commit()

    service = AnalyticsService(uow, clock)
    csv_file = tmp_path / "stats.csv"
    service.export_stats(str(csv_file))

    with open(csv_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Neither personal name nor database IDs should be in the report
    assert "Luiz" not in content
    assert "Inacio" not in content
    assert "candidate-unique-id-999" not in content
    # The zone and CBO should be present
    assert "NORTE" in content
    assert "3120-10" in content


def test_cli_export_stats_routing(tmp_path):
    """Verify that ArgparseCLIAdapter routes the export-stats command to the correct use case."""
    from filavaga.infra.translation import TranslationService
    service = TranslationService(locales_dir=str(tmp_path), default_lang="pt")
    
    mock_analytics = MagicMock()
    
    adapter = ArgparseCLIAdapter(
        None, None, translation_service=service, export_stats_usecase=mock_analytics
    )

    output_path = str(tmp_path / "output.csv")
    adapter.run(["export-stats", "--output", output_path])
    
    mock_analytics.export_stats.assert_called_once_with(output_path=output_path)
