"""
CLI bootstrap coordinator for the FilaVaga engine.

Initializes production adapters and services and starts the command router.

Author: Kalyel N. Laurindo / Software Engineer
"""

import os
from filavaga.infra.persistence.system_clock import SystemClock
from filavaga.infra.persistence.atomic_json import AtomicJsonRepository, JsonUnitOfWork
from filavaga.application.services.queue_manager import QueueManager
from filavaga.application.services.match_engine import MatchEngine
from filavaga.application.services.csv_importer import CSVImportService
from filavaga.infra.cli.command_router import ArgparseCLIAdapter
from filavaga.infra.cli.presenter import RichConsolePresenter
from filavaga.infra.logger import configure_logging


from filavaga.infra.translation import TranslationService


def main():
    """
    Main entry point for bootstrapping the application.
    """
    # 0. Configure structured logging to stderr
    configure_logging()
    
    # 1. Determine local snapshot persistence path
    home_dir = os.path.expanduser("~")
    db_path = os.path.join(home_dir, ".filavaga", "state_snapshot.json")
    
    # 2. Instantiate Outbound Adapters
    clock = SystemClock()
    repository = AtomicJsonRepository(db_path)
    uow = JsonUnitOfWork(repository)
    translation_service = TranslationService()
    presenter = RichConsolePresenter()
    
    # 3. Instantiate Core Services (Inbound Ports implementation)
    queue_manager = QueueManager(uow, clock)
    match_engine = MatchEngine(uow, clock)
    csv_importer = CSVImportService(uow, clock)
    
    # 4. Instantiate CLI Adapter (Inbound controller) and run
    cli_adapter = ArgparseCLIAdapter(
        register_usecase=queue_manager,
        match_usecase=match_engine,
        presenter=presenter,
        repository=repository,
        translation_service=translation_service,
        import_usecase=csv_importer
    )
    cli_adapter.run()



if __name__ == "__main__":
    main()
