"""
Command router CLI adapter using Python argparse.

Maps command line arguments directly to application use cases.

Author: Kalyel N. Laurindo / Software Engineer
"""

import sys
import argparse
from filavaga.application.ports.inbound import IRegisterCandidateUseCase, IMatchVacancyUseCase
from filavaga.core.exceptions import FilaVagaDomainError


class ArgparseCLIAdapter:
    """
    CLI command router adapter.
    
    Translates terminal options into use case coordinates.
    """

    def __init__(
        self,
        register_usecase: IRegisterCandidateUseCase | None,
        match_usecase: IMatchVacancyUseCase | None,
    ):
        """
        Initialize the adapter with required inbound use cases.
        """
        self._register_usecase = register_usecase
        self._match_usecase = match_usecase

    def run(self, args: list[str] | None = None) -> None:
        """
        Parse command line arguments and execute the matching use case.
        """
        parser = argparse.ArgumentParser(
            description="FilaVaga Engine - Local High-Precision Queue CLI Management Tool"
        )
        subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

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

        # Parse args
        parsed_args = parser.parse_args(args)

        try:
            if parsed_args.command == "register":
                if not self._register_usecase:
                    raise RuntimeError("Registration usecase is not configured.")
                candidate = self._register_usecase.register_candidate(
                    name=parsed_args.name,
                    profession_code=parsed_args.cbo,
                    sector_zone=parsed_args.zone,
                )
                print(f"Success: Candidate registered successfully.")
                print(f"  ID: {candidate.id}")
                print(f"  Name: {candidate.name}")
                print(f"  CBO: {candidate.profession_code}")
                print(f"  Zone: {candidate.sector_zone}")
                print(f"  Status: {candidate.status}")
                print(f"  Registered At: {candidate.registered_at}")

            elif parsed_args.command == "match":
                if not self._match_usecase:
                    raise RuntimeError("Match usecase is not configured.")
                candidate = self._match_usecase.match_vacancy(vacancy_id=parsed_args.id)
                if candidate:
                    print(f"Success: Vacancy matched successfully.")
                    print(f"  Vacancy ID: {parsed_args.id}")
                    print(f"  Matched Candidate ID: {candidate.id}")
                    print(f"  Name: {candidate.name}")
                    print(f"  Status: {candidate.status}")
                else:
                    print(f"No matching candidate found for vacancy {parsed_args.id}.")

            elif parsed_args.command == "dashboard":
                print("Interactive dashboard started...")

        except FilaVagaDomainError as e:
            print(f"Domain Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"System Error: {e}", file=sys.stderr)
            sys.exit(1)
