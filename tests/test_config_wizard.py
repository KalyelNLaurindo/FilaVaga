"""
Unit tests for the interactive configuration wizard (TSK-20).

Author: Kalyel N. Laurindo / Software Engineer
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from filavaga.application.services.config_wizard import ConfigWizardService
from filavaga.infra.cli.command_router import ArgparseCLIAdapter


def test_config_wizard_success(tmp_path):
    """Verify that configuration wizard updates and saves config.json atomically on success."""
    config_file = tmp_path / "config.json"
    
    # 1. Start with initial config
    initial_config = {
        "app_id": "filavaga-sine-local",
        "schema_version": "1.0",
        "persistence": {
            "directory": "~/.filavaga",
            "filename": "state_snapshot.json",
            "backup_filename": "state_snapshot.json.bak"
        },
        "business_rules": {
            "default_vacancy_ttl_hours": 24,
            "candidate_pruning_days": 30
        }
    }
    config_file.write_text(json.dumps(initial_config, indent=2), encoding="utf-8")

    # Instantiating service
    service = ConfigWizardService(str(config_file))

    # Mock user input values
    # Prompts order:
    # 1. Directory (Prompt.ask)
    # 2. Vacancy TTL (IntPrompt.ask)
    # 3. Pruning Days (IntPrompt.ask)
    # 4. Language (Prompt.ask)
    # 5. Timezone (Prompt.ask)
    # 6. Log Level (Prompt.ask)
    
    with patch("rich.prompt.Prompt.ask") as mock_prompt, \
         patch("rich.prompt.IntPrompt.ask") as mock_int_prompt:
        
        # We need mock_prompt side effects:
        # Prompt 1: directory
        # Prompt 4: language
        # Prompt 5: timezone
        # Prompt 6: log_level
        mock_prompt.side_effect = ["~/new_dir", "en", "America/Sao_Paulo", "DEBUG"]
        
        # mock_int_prompt side effects:
        # Prompt 2: vacancy_ttl
        # Prompt 3: pruning_days
        mock_int_prompt.side_effect = [12, 45]

        service.run_wizard()

    # Load and verify written configuration file
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    assert config_data["persistence"]["directory"] == "~/new_dir"
    assert config_data["business_rules"]["default_vacancy_ttl_hours"] == 12
    assert config_data["business_rules"]["candidate_pruning_days"] == 45
    assert config_data["lang"] == "en"
    assert config_data["timezone"] == "America/Sao_Paulo"
    assert config_data["logging"]["level"] == "DEBUG"


def test_config_wizard_keyboard_interrupt_graceful_cancel(tmp_path):
    """Verify that KeyboardInterrupt (Ctrl+C) cancels the wizard gracefully without writing changes."""
    config_file = tmp_path / "config.json"
    initial_config = {"lang": "pt"}
    config_file.write_text(json.dumps(initial_config), encoding="utf-8")

    service = ConfigWizardService(str(config_file))

    with patch("rich.prompt.Prompt.ask", side_effect=KeyboardInterrupt):
        # Execution must run and complete gracefully (no unhandled KeyboardInterrupt raised)
        service.run_wizard()

    # Verify that file has not been mutated
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    assert config_data == {"lang": "pt"}


def test_cli_config_wizard_routing(tmp_path):
    """Verify that command router correctly triggers the config-wizard subcommand."""
    from filavaga.infra.translation import TranslationService
    service = TranslationService(locales_dir=str(tmp_path), default_lang="pt")
    
    mock_wizard = MagicMock()
    
    adapter = ArgparseCLIAdapter(
        None, None, translation_service=service, config_wizard_usecase=mock_wizard
    )

    adapter.run(["config-wizard"])
    mock_wizard.run_wizard.assert_called_once()
