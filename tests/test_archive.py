"""
Unit tests for the candidate archiving and snapshot optimization (TSK-19).

Author: Kalyel N. Laurindo / Software Engineer
"""

import json
import os
import sys
import pytest
from unittest.mock import MagicMock
from filavaga.application.services.archive_service import ArchiveService
from filavaga.core.entities import Candidate, Queue
from filavaga.infra.persistence.atomic_json import AtomicJsonRepository, JsonUnitOfWork
from filavaga.infra.cli.command_router import ArgparseCLIAdapter
from tests.test_usecases import MockClock, MockStateRepository, MockUnitOfWork


def test_archive_candidates_by_age():
    """Verify that only PLACED or REJECTED candidates older than days threshold are archived."""
    # Current clock time: 2026-07-20T12:00:00Z
    clock = MockClock("2026-07-20T12:00:00Z")
    
    # Candidate 1: Old PLACED (registered 35 days ago, status PLACED) - should be archived
    c1 = Candidate("c_old_placed", "Alice Old", "SUL", "4110-10", "2026-06-15T12:00:00Z")
    c1.transition_to("CONTACTED")
    c1.transition_to("PLACED")

    # Candidate 2: Old REJECTED (registered 35 days ago, status REJECTED) - should be archived
    c2 = Candidate("c_old_rejected", "Bob Old", "NORTE", "4110-10", "2026-06-15T12:00:00Z")
    c2.transition_to("CONTACTED")
    c2.transition_to("REJECTED")

    # Candidate 3: New PLACED (registered 10 days ago, status PLACED) - should NOT be archived (too new)
    c3 = Candidate("c_new_placed", "Charlie New", "SUL", "4110-10", "2026-07-10T12:00:00Z")
    c3.transition_to("CONTACTED")
    c3.transition_to("PLACED")

    # Candidate 4: Old PENDING (registered 35 days ago, status PENDING) - should NOT be archived (still pending)
    c4 = Candidate("c_old_pending", "Daniel Pending", "SUL", "4110-10", "2026-06-15T12:00:00Z")

    repository = MockStateRepository()
    repository.save_candidate(c1)
    repository.save_candidate(c2)
    repository.save_candidate(c3)
    repository.save_candidate(c4)

    # Initialize professional queues
    q = Queue("4110-10")
    q.add_candidate(c1.id, c1.registered_at)
    q.add_candidate(c2.id, c2.registered_at)
    q.add_candidate(c3.id, c3.registered_at)
    q.add_candidate(c4.id, c4.registered_at)
    repository.save_queue(q)

    # Mock deletion and archiving methods on MockStateRepository
    repository.delete_candidate = MagicMock()
    repository.save_archived_candidates = MagicMock()

    uow = MockUnitOfWork(repository)
    service = ArchiveService(uow, clock)

    # Run archive with 30 days threshold
    count = service.archive_candidates(days=30)
    assert count == 2

    # Check that c1 and c2 were sent to archive
    repository.save_archived_candidates.assert_called_once()
    archived_list = repository.save_archived_candidates.call_args[0][0]
    assert len(archived_list) == 2
    assert any(c.id == "c_old_placed" for c in archived_list)
    assert any(c.id == "c_old_rejected" for c in archived_list)

    # Check that delete_candidate was called for c1 and c2
    assert repository.delete_candidate.call_count == 2
    repository.delete_candidate.assert_any_call("c_old_placed")
    repository.delete_candidate.assert_any_call("c_old_rejected")

    # Check queue updates
    updated_q = repository.get_queue("4110-10")
    assert "c_old_placed" not in updated_q.candidate_ids
    assert "c_old_rejected" not in updated_q.candidate_ids
    assert "c_new_placed" in updated_q.candidate_ids
    assert "c_old_pending" in updated_q.candidate_ids


def test_cli_archive_command_routing(tmp_path):
    """Verify that ArgparseCLIAdapter routes 'archive' subcommand correctly."""
    from filavaga.infra.translation import TranslationService
    service = TranslationService(locales_dir=str(tmp_path), default_lang="pt")
    
    mock_archive = MagicMock()
    mock_archive.archive_candidates.return_value = 5

    adapter = ArgparseCLIAdapter(
        None, None, translation_service=service, archive_usecase=mock_archive
    )

    adapter.run(["archive", "--days", "15"])
    mock_archive.archive_candidates.assert_called_once_with(days=15)
