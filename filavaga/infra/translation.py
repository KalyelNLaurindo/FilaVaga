"""
Translation Service (i18n) Engine.

Provides multi-language translation resolution and loading capabilities.

Author: Kalyel N. Laurindo / Software Engineer
"""

import os
import json
import re
import logging

logger = logging.getLogger("filavaga")


class TranslationService:
    """
    Manages loading of locale json resource files, string translation
    and active locale resolution with fallback logic.
    """

    def __init__(self, locales_dir: str = None, default_lang: str = "pt", config_path: str = None):
        if locales_dir is None:
            # Package default locales folder path
            locales_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "locales")
        
        self.locales_dir = os.path.abspath(locales_dir)
        self.default_lang = default_lang
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
        self._translations = {}
        self._active_lang = default_lang

    def _sanitize_lang(self, lang: str) -> str:
        """
        Sanitize language input to prevent directory traversal and arbitrary file loading.
        Only allows simple language tags (e.g. pt, en, pt_BR, es-ES).
        """
        if not lang or not isinstance(lang, str):
            raise ValueError("Language code must be a non-empty string.")
            
        # Match alphanumeric, dash, and underscore only
        if not re.match(r"^[a-zA-Z0-9_-]+$", lang):
            raise ValueError(f"Security Warning: Invalid language format detected: {lang}")
            
        return lang.strip().lower()

    def load_language(self, lang: str) -> None:
        """
        Load a JSON translation file for a specific language into memory.
        """
        clean_lang = self._sanitize_lang(lang)
        file_path = os.path.join(self.locales_dir, f"{clean_lang}.json")
        
        # Verify the file is actually inside the locales directory (prevent traversal attacks)
        real_locales_dir = os.path.realpath(self.locales_dir)
        real_file_path = os.path.realpath(file_path)
        if not real_file_path.startswith(real_locales_dir):
            raise ValueError("Security Warning: Directory traversal attempt detected.")

        if not os.path.exists(file_path):
            logger.warning("Locale file not found: %s. Using default keys.", file_path)
            self._translations[clean_lang] = {}
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._translations[clean_lang] = data
        except Exception as e:
            logger.error("Failed to load locale file %s: %s", file_path, e)
            self._translations[clean_lang] = {}

    def translate(self, key: str, lang: str = None, **kwargs) -> str:
        """
        Translate a message key into the targeted language with string parameter formatting.
        """
        target_lang = self._sanitize_lang(lang or self._active_lang)
        
        # Ensure targeted language is loaded
        if target_lang not in self._translations:
            self.load_language(target_lang)
            
        # Get raw translation or fallback to default lang, then to key itself
        translation_dict = self._translations.get(target_lang, {})
        raw_msg = translation_dict.get(key)
        
        if raw_msg is None:
            # Try loading default language if different
            default_clean = self._sanitize_lang(self.default_lang)
            if target_lang != default_clean:
                if default_clean not in self._translations:
                    self.load_language(default_clean)
                raw_msg = self._translations.get(default_clean, {}).get(key)
                
        if raw_msg is None:
            raw_msg = key

        # Perform parameter interpolation safely
        try:
            return raw_msg.format(**kwargs)
        except KeyError as ke:
            logger.warning("Missing parameter for translation of '%s': %s", key, ke)
            return raw_msg
        except Exception as e:
            logger.error("Error formatting translation for key '%s': %s", key, e)
            return raw_msg

    def resolve_lang(self, cli_lang: str = None) -> str:
        """
        Resolve the active language code based on priority precedence:
        1. CLI flag (cli_lang)
        2. config.json config
        3. Environment variables (LC_ALL, LANG)
        4. Default fallback
        """
        # 1. CLI Lang
        if cli_lang:
            try:
                self._active_lang = self._sanitize_lang(cli_lang)
                return self._active_lang
            except ValueError:
                pass

        # 2. Config.json
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    if isinstance(config_data, dict) and "lang" in config_data:
                        self._active_lang = self._sanitize_lang(config_data["lang"])
                        return self._active_lang
            except Exception as e:
                logger.debug("Failed to read lang configuration from config.json: %s", e)

        # 3. Environment Variables
        for var in ["LC_ALL", "LANG"]:
            env_val = os.environ.get(var)
            if env_val:
                # Extracts the language part (e.g. en_US.UTF-8 -> en)
                match = re.match(r"^([a-zA-Z0-9_-]+)", env_val)
                if match:
                    lang_code = match.group(1).split("_")[0].split("-")[0]
                    try:
                        self._active_lang = self._sanitize_lang(lang_code)
                        return self._active_lang
                    except ValueError:
                        pass

        # 4. Default Fallback
        self._active_lang = self._sanitize_lang(self.default_lang)
        return self._active_lang
