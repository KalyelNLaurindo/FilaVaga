import os
import pytest
from unittest.mock import patch, MagicMock
from filavaga.infra.cli.command_router import ArgparseCLIAdapter
from filavaga.infra.translation import TranslationService

def test_interactive_loop_quit():
    """Verify that entering 'q' or 'Q' exits the interactive loop immediately."""
    adapter = ArgparseCLIAdapter(None, None)
    
    # We mock self._repository to avoid DB load errors
    mock_repo = MagicMock()
    mock_repo.get_all_candidates.return_value = {}
    mock_repo.get_all_vacancies.return_value = {}
    adapter._repository = mock_repo
    
    # Simulating inputting 'q' to quit
    with patch("builtins.input", side_effect=["q"]) as mock_input:
        adapter._run_interactive_dashboard_loop()
        assert mock_input.call_count == 1


def test_interactive_loop_lang_switch(tmp_path):
    """Verify that entering 'l' opens the language selector and switches active language."""
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir()
    
    # Create locales files
    import json
    with open(locales_dir / "pt.json", "w", encoding="utf-8") as f:
        json.dump({"dashboard_header": "Painel"}, f)
    with open(locales_dir / "en.json", "w", encoding="utf-8") as f:
        json.dump({"dashboard_header": "Dashboard"}, f)

    service = TranslationService(locales_dir=str(locales_dir), default_lang="pt")
    adapter = ArgparseCLIAdapter(None, None, translation_service=service)
    
    mock_repo = MagicMock()
    mock_repo.get_all_candidates.return_value = {}
    mock_repo.get_all_vacancies.return_value = {}
    adapter._repository = mock_repo
    
    # Simulating inputs:
    # 1. 'l' -> open language menu
    # 2. '2' -> select 'en' (English)
    # 3. 'q' -> quit loop
    inputs = ["l", "2", "q"]
    with patch("builtins.input", side_effect=inputs):
        adapter._run_interactive_dashboard_loop()
        assert service._active_lang == "en"


def test_presenter_ascii_fallback(tmp_path):
    """Verify that RichConsolePresenter switches to ASCII borders when env var is set."""
    from filavaga.infra.cli.presenter import RichConsolePresenter
    from rich.console import Console
    from rich.box import ASCII, SQUARE
    
    # By default, should not use ASCII box
    presenter = RichConsolePresenter()
    assert presenter.box_style is None or presenter.box_style != ASCII
    
    with patch.dict(os.environ, {"FILAVAGA_ASCII": "1"}):
        presenter_ascii = RichConsolePresenter()
        # Verify it resolves to ASCII box style
        assert presenter_ascii.box_style == ASCII
