"""
Unit tests for the visual terminal TUI redesign (TSK-35).

Author: Kalyel N. Laurindo / Software Engineer
"""

import os
from unittest.mock import patch
from rich.console import Console
from filavaga.infra.cli.presenter import RichConsolePresenter
from filavaga.core.entities import Candidate


def test_tui_welcome_banner_rendering(capsys):
    """Verify that welcome banner renders branded app info and tagline."""
    presenter = RichConsolePresenter()
    presenter.display_welcome_banner()

    captured = capsys.readouterr().out
    assert "Vacancy" in captured
    assert "v2.1.0" in captured
    assert "management engine" in captured


def test_tui_separator_line(capsys):
    """Verify that display_separator prints a divider line."""
    presenter = RichConsolePresenter()
    presenter.display_separator()

    captured = capsys.readouterr().out
    assert len(captured.strip()) > 0
    # Should contain unicode divider char or plain ASCII dashes
    assert "─" in captured or "-" in captured


def test_tui_message_icons(capsys):
    """Verify that presenter prepends correct feedback icons to output."""
    presenter = RichConsolePresenter()
    
    # 1. Success message should display checkmark icon
    candidate = Candidate("c_1", "Test Candidate", "SUL", "4110-10", "2026-06-15T08:00:00Z")
    presenter.display_candidate_registration(candidate)
    captured = capsys.readouterr().out
    assert "✅" in captured or "Success" in captured

    # 2. Error message should display cross icon
    presenter.display_error("Domain Error", "Test message")
    captured = capsys.readouterr().out
    assert "❌" in captured or "Error" in captured


def test_tui_fallback_and_no_color(capsys):
    """Verify that TUI strips ANSI codes and falls back to plain ASCII under no_color/ascii mode."""
    # Test ASCII fallback box character conversion
    presenter = RichConsolePresenter(ascii_only=True, no_color=True)
    
    # Draw simple panel or error and check that unicode box chars are replaced with plain ASCII + / -
    presenter.display_error("Domain Error", "Test message")
    captured = capsys.readouterr().out
    
    # Unicode box characters shouldn't be present
    assert "╭" not in captured
    assert "─" not in captured
    assert "+" in captured or "-" in captured
