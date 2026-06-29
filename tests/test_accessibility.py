"""
Unit tests for CLI Accessibility Suite (TSK-31).

Ensures FilaVaga console UI supports NO_COLOR environment variable,
--no-color CLI option, linear layouts for screen-readers, and clear
textual status indicators.

Author: Kalyel N. Laurindo / Software Engineer
"""

import io
import os
import pytest
from unittest.mock import patch, MagicMock
from rich.console import Console
from filavaga.infra.cli.presenter import RichConsolePresenter
from filavaga.infra.cli.command_router import ArgparseCLIAdapter
from filavaga.core.entities import Candidate, Vacancy, Queue, QueueEntry


def test_presenter_respects_no_color_arg():
    """Verify that passing no_color=True to RichConsolePresenter disables ANSI colors."""
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=True)
    presenter = RichConsolePresenter(console=console, no_color=True)
    
    candidate = Candidate(
        id="c_test", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T12:00:00Z"
    )
    presenter.display_candidate_registration(candidate)
    output = buffer.getvalue()
    
    # ANSI escape sequences start with \x1b[
    assert "\x1b[" not in output


def test_presenter_respects_no_color_env():
    """Verify that setting the NO_COLOR env var disables ANSI colors in RichConsolePresenter."""
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=True)
    with patch.dict(os.environ, {"NO_COLOR": "1"}):
        presenter = RichConsolePresenter(console=console)
        assert presenter.no_color is True
        
        candidate = Candidate(
            id="c_test", name="Maria Silva", sector_zone="SUL",
            profession_code="4110-10", registered_at="2026-06-15T12:00:00Z"
        )
        presenter.display_candidate_registration(candidate)
        output = buffer.getvalue()
        assert "\x1b[" not in output


def test_linear_presentation():
    """Verify that linear=True displays candidate details without box-drawing characters."""
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=True)
    presenter = RichConsolePresenter(console=console, linear=True)
    
    candidate = Candidate(
        id="c_test", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T12:00:00Z"
    )
    presenter.display_candidate_registration(candidate)
    output = buffer.getvalue()
    
    # Check that it output linear details and no box-drawing borders
    assert "c_test" in output
    assert "Maria Silva" in output
    assert "┌" not in output
    assert "─" not in output
    assert "│" not in output


def test_linear_dashboard_formatting():
    """Verify that linear=True prints dashboard lists without ASCII/SQUARE grid tables."""
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=True)
    presenter = RichConsolePresenter(console=console, linear=True)
    
    candidates = {
        "c_1": Candidate(id="c_1", name="Maria Silva", sector_zone="SUL", profession_code="4110-10", registered_at="2026-06-15T08:00:00Z")
    }
    vacancies = {
        "v_1": Vacancy(id="v_1", title="Auxiliar", profession_code="4110-10", sector_zone="SUL", capacity=2, created_at="2026-06-15T10:00:00Z", expires_at="2026-06-16T10:00:00Z")
    }
    queues = {
        "4110-10": Queue(profession_code="4110-10", entries=[QueueEntry(candidate_id="c_1", registered_at="2026-06-15T08:00:00Z")])
    }
    
    presenter.display_dashboard(candidates, vacancies, queues)
    output = buffer.getvalue()
    
    assert "Maria Silva" in output
    assert "v_1" in output
    assert "4110-10" in output
    assert "┌" not in output
    assert "─" not in output
    assert "│" not in output


def test_textual_status_indicators():
    """Verify that candidate display includes explicit textual status indicators."""
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=True)
    presenter = RichConsolePresenter(console=console, linear=True)
    
    candidate = Candidate(
        id="c_test", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T12:00:00Z", status="PENDING"
    )
    presenter.display_candidate_registration(candidate)
    output = buffer.getvalue()
    
    assert "STATUS: PENDING" in output.upper()


def test_command_router_no_color_flag(tmp_path):
    """Verify that command router processes --no-color flag and propagates to presenter."""
    from filavaga.infra.translation import TranslationService
    
    service = TranslationService(locales_dir=str(tmp_path), default_lang="pt")
    presenter = RichConsolePresenter()
    
    # Set up adapter
    adapter = ArgparseCLIAdapter(None, None, presenter=presenter, translation_service=service)
    
    mock_repo = MagicMock()
    mock_repo.get_all_candidates.return_value = {}
    mock_repo.get_all_vacancies.return_value = {}
    adapter._repository = mock_repo
    adapter._run_interactive_dashboard_loop = MagicMock()
    
    adapter.run(["--no-color", "dashboard"])
    
    assert presenter.no_color is True
    assert presenter.console.color_system is None


def test_command_router_linear_flag(tmp_path):
    """Verify that command router processes --linear / --accessible flags and propagates to presenter."""
    from filavaga.infra.translation import TranslationService
    
    service = TranslationService(locales_dir=str(tmp_path), default_lang="pt")
    presenter = RichConsolePresenter()
    
    # Set up adapter
    adapter = ArgparseCLIAdapter(None, None, presenter=presenter, translation_service=service)
    
    mock_repo = MagicMock()
    mock_repo.get_all_candidates.return_value = {}
    mock_repo.get_all_vacancies.return_value = {}
    adapter._repository = mock_repo
    adapter._run_interactive_dashboard_loop = MagicMock()
    
    adapter.run(["--linear", "dashboard"])
    
    assert presenter.linear is True
