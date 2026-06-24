import os
import json
import pytest
from unittest.mock import patch, mock_open

# We will import TranslationService from filavaga.infra.translation
# For the RED phase, this import will fail or classes won't be defined yet.

def test_translation_service_basic_loading(tmp_path):
    """Verify that TranslationService loads keys correctly from locale files."""
    from filavaga.infra.translation import TranslationService
    
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir()
    
    pt_data = {"welcome": "Olá mundo", "greet": "Olá {name}"}
    en_data = {"welcome": "Hello world", "greet": "Hello {name}"}
    
    with open(locales_dir / "pt.json", "w", encoding="utf-8") as f:
        json.dump(pt_data, f)
    with open(locales_dir / "en.json", "w", encoding="utf-8") as f:
        json.dump(en_data, f)
        
    service = TranslationService(locales_dir=str(locales_dir), default_lang="pt")
    service.load_language("pt")
    service.load_language("en")
    
    # Check default/active language translation
    assert service.translate("welcome", lang="pt") == "Olá mundo"
    assert service.translate("welcome", lang="en") == "Hello world"
    
    # Check interpolation
    assert service.translate("greet", lang="pt", name="Kalyel") == "Olá Kalyel"
    assert service.translate("greet", lang="en", name="Kalyel") == "Hello Kalyel"
    
    # Fallback to key if translation missing
    assert service.translate("missing_key", lang="pt") == "missing_key"


def test_translation_service_path_traversal_protection(tmp_path):
    """Verify that translation service rejects invalid language strings to prevent path traversal."""
    from filavaga.infra.translation import TranslationService
    
    service = TranslationService(locales_dir=str(tmp_path), default_lang="pt")
    
    # Traversal strings should raise ValueError
    with pytest.raises(ValueError):
        service.load_language("../invalid")
        
    with pytest.raises(ValueError):
        service.load_language("sub/folder")
        
    with pytest.raises(ValueError):
        service.load_language("pt.json")  # only codes are allowed


def test_translation_resolution_precedence(tmp_path):
    """Verify that active language resolves using strict precedence rules."""
    from filavaga.infra.translation import TranslationService
    
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir()
    
    # Create empty default translation file to allow loading
    with open(locales_dir / "pt.json", "w", encoding="utf-8") as f:
        json.dump({}, f)
    with open(locales_dir / "en.json", "w", encoding="utf-8") as f:
        json.dump({}, f)
    with open(locales_dir / "es.json", "w", encoding="utf-8") as f:
        json.dump({}, f)
    with open(locales_dir / "fr.json", "w", encoding="utf-8") as f:
        json.dump({}, f)
        
    # We will simulate config.json
    config_file = tmp_path / "config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump({"lang": "es"}, f)
        
    # 1. Fallback to default (pt) when everything is empty/unset
    with patch.dict(os.environ, {}, clear=True):
        service = TranslationService(locales_dir=str(locales_dir), config_path=None)
        assert service.resolve_lang(cli_lang=None) == "pt"
        
    # 2. OS Environment variable LANG / LC_ALL
    with patch.dict(os.environ, {"LANG": "fr_FR.UTF-8"}, clear=True):
        service = TranslationService(locales_dir=str(locales_dir), config_path=None)
        assert service.resolve_lang(cli_lang=None) == "fr"
        
    with patch.dict(os.environ, {"LC_ALL": "en_US"}, clear=True):
        service = TranslationService(locales_dir=str(locales_dir), config_path=None)
        assert service.resolve_lang(cli_lang=None) == "en"
        
    # 3. config.json should override environment variable
    with patch.dict(os.environ, {"LANG": "fr"}, clear=True):
        service = TranslationService(locales_dir=str(locales_dir), config_path=str(config_file))
        assert service.resolve_lang(cli_lang=None) == "es"
        
    # 4. CLI Argument overrides config.json
    with patch.dict(os.environ, {"LANG": "fr"}, clear=True):
        service = TranslationService(locales_dir=str(locales_dir), config_path=str(config_file))
        assert service.resolve_lang(cli_lang="en") == "en"


def test_argparse_cli_lang(tmp_path):
    """Verify that ArgparseCLIAdapter registers --lang / -l and integrates with TranslationService."""
    from filavaga.infra.cli.command_router import ArgparseCLIAdapter
    from filavaga.infra.translation import TranslationService
    
    service = TranslationService(locales_dir=str(tmp_path), default_lang="pt")
    
    # We setup the adapter with a mocked register use case or similar
    # We just need to check if the adapter parses --lang / -l without throwing errors
    adapter = ArgparseCLIAdapter(
        register_usecase=None,
        match_usecase=None,
        translation_service=service
    )
    
    # We mock subcommand parsing to prevent execution from failing on missing subcommands
    # Actually, we can test it with argparse directly, or by passing '--lang en dashboard' (dashboard doesn't require a mock if repo is set up)
    # Let's inspect parser options
    import argparse
    parser = argparse.ArgumentParser()
    # Let's check if the adapter actually defines the argparse flags by instantiating or running it
    # We mock command_router's internal methods or test parsing directly
    # To do this cleanly, we check if `--lang` option exists in the adapter's parser
    # We can inspect the private parser inside run or by extending the command router.
    # Let's run a test where we pass '--lang en dashboard' but mock the repository to avoid DB errors
    from unittest.mock import MagicMock
    mock_repo = MagicMock()
    mock_repo.get_all_candidates.return_value = {}
    mock_repo.get_all_vacancies.return_value = {}
    
    adapter._repository = mock_repo
    
    # Let's run and verify it resolves active_lang as "en"
    adapter.run(["--lang", "en", "dashboard"])
    assert service._active_lang == "en"

