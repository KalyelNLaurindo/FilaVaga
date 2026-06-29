"""
ConfigWizardService class implementation.

Coordinates interactive setup configuration prompts.

Author: Kalyel N. Laurindo / Software Engineer
"""

import json
import os
import logging
from rich.prompt import Prompt, IntPrompt
from rich.console import Console
from filavaga.application.ports.inbound import IConfigWizardUseCase

logger = logging.getLogger("filavaga")


class ConfigWizardService(IConfigWizardUseCase):
    """
    Service responsible for guiding counselors or system administrators through
    editing config.json settings interactively.
    """

    def __init__(self, config_path: str = None):
        if config_path is None:
            # Resolve root directory path relative to this source file
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
        self.config_path = os.path.abspath(config_path)
        self.console = Console()

    def run_wizard(self) -> None:
        """
        Sequentially prompt for settings, validating entries and writing atomically.
        """
        self.console.print("[bold blue]=== FilaVaga Configuration Wizard ===[/bold blue]\n")

        # Define basic default settings schema
        config = {
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
            },
            "lang": "pt",
            "timezone": "UTC",
            "logging": {
                "level": "INFO"
            }
        }

        # 1. Load active config.json fields if file exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        # Merge dictionaries at root level
                        for k, v in loaded.items():
                            if isinstance(v, dict) and k in config:
                                config[k].update(v)
                            else:
                                config[k] = v
            except Exception as e:
                logger.warning("Could not read configuration file: %s. Using internal defaults.", e)

        # 2. Execute interactive prompt sequence
        try:
            # Directory
            curr_dir = config.get("persistence", {}).get("directory", "~/.filavaga")
            new_dir = Prompt.ask(
                "[cyan]Database folder path (persistence directory)[/cyan]",
                default=curr_dir,
                console=self.console
            )

            # Vacancy TTL (hours)
            curr_ttl = config.get("business_rules", {}).get("default_vacancy_ttl_hours", 24)
            new_ttl = IntPrompt.ask(
                "[cyan]Default vacancy TTL in hours[/cyan]",
                default=curr_ttl,
                console=self.console
            )
            while new_ttl <= 0:
                self.console.print("[bold red]Error: TTL must be a positive integer.[/bold red]")
                new_ttl = IntPrompt.ask(
                    "[cyan]Default vacancy TTL in hours[/cyan]",
                    default=curr_ttl,
                    console=self.console
                )

            # Candidate Pruning Age Limit (days)
            curr_prune = config.get("business_rules", {}).get("candidate_pruning_days", 30)
            new_prune = IntPrompt.ask(
                "[cyan]Candidate pruning / archiving age threshold in days[/cyan]",
                default=curr_prune,
                console=self.console
            )
            while new_prune <= 0:
                self.console.print("[bold red]Error: Pruning days must be a positive integer.[/bold red]")
                new_prune = IntPrompt.ask(
                    "[cyan]Candidate pruning / archiving age threshold in days[/cyan]",
                    default=curr_prune,
                    console=self.console
                )

            # Language selection choices
            curr_lang = config.get("lang", "pt")
            new_lang = Prompt.ask(
                "[cyan]Active system language[/cyan]",
                choices=["pt", "en", "es", "fr", "de"],
                default=curr_lang,
                console=self.console
            )

            # Timezone selection string
            curr_tz = config.get("timezone", "UTC")
            new_tz = Prompt.ask(
                "[cyan]System executing timezone (e.g. UTC, America/Sao_Paulo)[/cyan]",
                default=curr_tz,
                console=self.console
            )
            while not new_tz.strip():
                self.console.print("[bold red]Error: Timezone cannot be empty.[/bold red]")
                new_tz = Prompt.ask(
                    "[cyan]System executing timezone (e.g. UTC, America/Sao_Paulo)[/cyan]",
                    default=curr_tz,
                    console=self.console
                )

            # Logging Level choices
            curr_log = config.get("logging", {}).get("level", "INFO")
            new_log = Prompt.ask(
                "[cyan]Console/standard output log level[/cyan]",
                choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                default=curr_log,
                console=self.console
            )

            # 3. Compile configurations and save atomically
            if "persistence" not in config:
                config["persistence"] = {}
            config["persistence"]["directory"] = new_dir.strip()

            if "business_rules" not in config:
                config["business_rules"] = {}
            config["business_rules"]["default_vacancy_ttl_hours"] = new_ttl
            config["business_rules"]["candidate_pruning_days"] = new_prune

            config["lang"] = new_lang.strip().lower()
            config["timezone"] = new_tz.strip()

            if "logging" not in config:
                config["logging"] = {}
            config["logging"]["level"] = new_log.strip().upper()

            # Perform atomic write staging
            tmp_path = self.config_path + ".tmp"
            parent_dir = os.path.dirname(self.config_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            os.replace(tmp_path, self.config_path)
            self.console.print("\n[bold green]Success: Configuration saved successfully to config.json![/bold green]")

        except KeyboardInterrupt:
            self.console.print("\n[bold yellow]Configuration wizard cancelled. No changes were saved.[/bold yellow]")
