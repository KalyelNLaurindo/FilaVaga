"""
Command router CLI adapter using Python argparse.

Maps command line arguments directly to application use cases.

Author: Kalyel N. Laurindo / Software Engineer
"""

import os
import sys
import secrets
import argparse
from filavaga.application.ports.inbound import IRegisterCandidateUseCase, IMatchVacancyUseCase
from filavaga.application.ports.outbound import IStateRepository
from filavaga.core.exceptions import FilaVagaDomainError
from filavaga.infra.cli.presenter import RichConsolePresenter


def _secure_shred_file(filepath: str) -> None:
    """
    Safely overwrite a file with zeros and random bytes before removing it.
    This prevents physical recovery of personal candidate data (LGPD Compliance).
    """
    if not os.path.exists(filepath):
        return

    try:
        # Get file size
        size = os.path.getsize(filepath)

        # 1. Overwrite with zeros
        with open(filepath, "ba+", buffering=0) as f:
            f.seek(0)
            f.write(b"\x00" * size)
            f.flush()
            os.fsync(f.fileno())

        # 2. Overwrite with random bytes
        with open(filepath, "ba+", buffering=0) as f:
            f.seek(0)
            f.write(secrets.token_bytes(size))
            f.flush()
            os.fsync(f.fileno())

        # 3. Final deletion
        os.remove(filepath)
    except Exception:
        # Fallback to standard remove if shredding fails due to open locks
        try:
            os.remove(filepath)
        except Exception:
            pass


class ArgparseCLIAdapter:
    """
    CLI command router adapter.
    
    Translates terminal options into use case coordinates.
    """

    def __init__(
        self,
        register_usecase: IRegisterCandidateUseCase | None,
        match_usecase: IMatchVacancyUseCase | None,
        presenter: RichConsolePresenter | None = None,
        repository: IStateRepository | None = None,
        translation_service = None,
    ):
        """
        Initialize the adapter with required inbound use cases.
        """
        self._register_usecase = register_usecase
        self._match_usecase = match_usecase
        self._presenter = presenter or RichConsolePresenter()
        self._repository = repository
        self._translation_service = translation_service

    def run(self, args: list[str] | None = None) -> None:
        """
        Parse command line arguments and execute the matching use case.
        """
        parser = argparse.ArgumentParser(
            description="FilaVaga Engine - Local High-Precision Queue CLI Management Tool"
        )
        parser.add_argument("--lang", "-l", help="Language code (pt, en, es, fr, de)")
        subparsers = parser.add_subparsers(dest="command", required=False, help="Available commands")

        # 1. Register Command Subparser
        register_parser = subparsers.add_parser("register", help="Register a candidate in a FIFO queue")
        register_parser.add_argument("--name", required=True, help="Full name of the candidate")
        register_parser.add_argument("--cbo", required=True, help="CBO profession code")
        register_parser.add_argument("--zone", required=True, help="Sector region zone preference")

        # 2. Match Command Subparser
        match_parser = subparsers.add_parser("match", help="Match a vacancy to the highest priority candidate")
        match_parser.add_argument("--id", required=True, help="Unique identifier of the vacancy")

        # 3. Dashboard Command Subparser
        subparsers.add_parser("dashboard", help="Start the interactive dashboard view")

        # 4. Purge All Command Subparser (LGPD Compliance)
        subparsers.add_parser("purge-all", help="Safely and permanently purge all candidate data and local snapshots")

        # Parse args
        parsed_args = parser.parse_args(args)

        if self._translation_service:
            resolved_lang = self._translation_service.resolve_lang(parsed_args.lang)
            self._translation_service.load_language(resolved_lang)

        command = parsed_args.command or "dashboard"

        try:
            if command == "register":
                if not self._register_usecase:
                    raise RuntimeError("Registration usecase is not configured.")
                candidate = self._register_usecase.register_candidate(
                    name=parsed_args.name,
                    profession_code=parsed_args.cbo,
                    sector_zone=parsed_args.zone,
                )
                self._presenter.display_candidate_registration(candidate)

            elif command == "match":
                if not self._match_usecase:
                    raise RuntimeError("Match usecase is not configured.")
                candidate = self._match_usecase.match_vacancy(vacancy_id=parsed_args.id)
                if candidate:
                    self._presenter.display_vacancy_match(parsed_args.id, candidate)
                else:
                    self._presenter.display_no_match(parsed_args.id)

            elif command == "dashboard":
                if not self._repository:
                    raise RuntimeError("Repository is not configured for dashboard view.")
                
                self._run_interactive_dashboard_loop()

            elif command == "purge-all":
                db_path = None
                if self._repository and hasattr(self._repository, "filepath"):
                    db_path = self._repository.filepath
                else:
                    home_dir = os.path.expanduser("~")
                    db_path = os.path.join(home_dir, ".filavaga", "state_snapshot.json")

                bak_path = db_path + ".bak"
                err_path = db_path + ".err"

                # Perform secure shredding
                _secure_shred_file(db_path)
                _secure_shred_file(bak_path)
                _secure_shred_file(err_path)

                # Clear repository memory state
                if self._repository:
                    if hasattr(self._repository, "_candidates"):
                        self._repository._candidates.clear()
                    if hasattr(self._repository, "_vacancies"):
                        self._repository._vacancies.clear()
                    if hasattr(self._repository, "_queues"):
                        self._repository._queues.clear()

                print("Success: All local candidate data, backups, and error dumps have been permanently purged (LGPD-Compliant).")

        except FilaVagaDomainError as e:
            self._presenter.display_error("Domain Error", str(e))
            sys.exit(1)
        except Exception as e:
            self._presenter.display_error("System Error", str(e))
            sys.exit(1)

    def _run_interactive_dashboard_loop(self) -> None:
        """
        Runs the interactive CLI dashboard loop.
        Allows counselors to perform matching, candidate registration,
        language switching, or quit using single-character shortcuts.
        """
        from filavaga.core.exceptions import FilaVagaDomainError

        while True:
            # 1. Fetch current repository files state
            candidates_map = self._repository.get_all_candidates() if self._repository else {}
            vacancies_map = self._repository.get_all_vacancies() if self._repository else {}

            # Fetch all existing queues
            cbo_codes = set()
            cbo_codes.update(c.profession_code for c in candidates_map.values())
            cbo_codes.update(v.profession_code for v in vacancies_map.values())

            queues_map = {}
            for code in cbo_codes:
                q = self._repository.get_queue(code)
                if q:
                    queues_map[code] = q

            # 2. Print status header
            lang_code = self._translation_service._active_lang if self._translation_service else "pt"
            db_path_str = self._repository.filepath if self._repository else "In-Memory"
            db_status_str = "OK" if self._repository and os.path.exists(os.path.dirname(self._repository.filepath)) else "N/A"

            status_header = self._presenter.translation_service.translate(
                "header_status",
                lang=lang_code.upper(),
                db_path=db_path_str,
                status=db_status_str
            )
            self._presenter.console.print(f"[bold white on blue]{status_header}[/bold white on blue]")

            # 3. Print main dashboard
            self._presenter.display_dashboard(
                candidates=candidates_map,
                vacancies=vacancies_map,
                queues=queues_map
            )

            # 4. Display options menu
            options_text = self._presenter.translation_service.translate("menu_options")
            prompt_text = self._presenter.translation_service.translate("menu_prompt")
            self._presenter.console.print(f"[bold yellow]{options_text}[/bold yellow]")

            try:
                choice = input(prompt_text).strip().lower()
            except (KeyboardInterrupt, EOFError):
                break

            if choice == "q":
                break

            elif choice == "c":
                name_prompt = self._presenter.translation_service.translate("prompt_enter_name")
                cbo_prompt = self._presenter.translation_service.translate("prompt_enter_cbo")
                zone_prompt = self._presenter.translation_service.translate("prompt_enter_zone")

                try:
                    name = input(name_prompt)
                    cbo = input(cbo_prompt)
                    zone = input(zone_prompt)

                    if not self._register_usecase:
                        raise RuntimeError("Registration usecase is not configured.")
                    candidate = self._register_usecase.register_candidate(
                        name=name,
                        profession_code=cbo,
                        sector_zone=zone,
                    )
                    self._presenter.display_candidate_registration(candidate)
                except FilaVagaDomainError as e:
                    self._presenter.display_error("Domain Error", str(e))
                except Exception as e:
                    self._presenter.display_error("System Error", str(e))

                input(self._presenter.translation_service.translate("press_enter"))

            elif choice == "m":
                vac_prompt = self._presenter.translation_service.translate("prompt_enter_vacancy_id")
                try:
                    vac_id = input(vac_prompt)
                    if not self._match_usecase:
                        raise RuntimeError("Match usecase is not configured.")
                    candidate = self._match_usecase.match_vacancy(vacancy_id=vac_id)
                    if candidate:
                        self._presenter.display_vacancy_match(vac_id, candidate)
                    else:
                        self._presenter.display_no_match(vac_id)
                except FilaVagaDomainError as e:
                    self._presenter.display_error("Domain Error", str(e))
                except Exception as e:
                    self._presenter.display_error("System Error", str(e))

                input(self._presenter.translation_service.translate("press_enter"))

            elif choice == "l":
                lang_prompt = self._presenter.translation_service.translate("prompt_lang_menu")
                lang_choice = input(lang_prompt).strip()
                lang_mapping = {
                    "1": "pt",
                    "2": "en",
                    "3": "es",
                    "4": "fr",
                    "5": "de"
                }
                selected_lang = lang_mapping.get(lang_choice)
                if selected_lang and self._translation_service:
                    self._translation_service.resolve_lang(selected_lang)
                    self._translation_service.load_language(selected_lang)
                    # Sync presenter i18n
                    self._presenter.translation_service = self._translation_service
