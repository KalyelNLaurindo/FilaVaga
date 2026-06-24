"""
RichConsolePresenter for FilaVaga console UI.

Handles terminal presentation layouts using the rich library.
Provides colored panels, detailed tables, error alerts, and dashboards.

Author: Kalyel N. Laurindo / Software Engineer
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from filavaga.core.entities import Candidate, Vacancy, Queue


class RichConsolePresenter:
    """
    Console UI renderer using Rich components.
    
    Produces premium visual grids, status cards, and layout frames, fully localized.
    """

    def __init__(self, console: Console | None = None, translation_service = None, ascii_only: bool = False):
        """
        Initialize the presenter with a Console instance and translation service.
        """
        self.console = console or Console()
        if translation_service is None:
            from filavaga.infra.translation import TranslationService
            translation_service = TranslationService()
        self.translation_service = translation_service
        
        # Determine box style (ASCII fallback)
        import os
        if ascii_only or os.environ.get("FILAVAGA_ASCII") == "1":
            self.box_style = box.ASCII
        else:
            self.box_style = box.SQUARE

    def display_candidate_registration(self, candidate: Candidate) -> None:
        """
        Render candidate registration details in a beautiful green success Panel.
        """
        content = Text()
        content.append(f"{self.translation_service.translate('label_id')}: ", style="bold green")
        content.append(f"{candidate.id}\n", style="white")
        content.append(f"{self.translation_service.translate('label_name')}: ", style="bold green")
        content.append(f"{candidate.name}\n", style="white")
        content.append(f"{self.translation_service.translate('label_profession')}: ", style="bold green")
        content.append(f"{candidate.profession_code}\n", style="white")
        content.append(f"{self.translation_service.translate('label_zone')}: ", style="bold green")
        content.append(f"{candidate.sector_zone}\n", style="white")
        content.append(f"{self.translation_service.translate('label_status')}: ", style="bold green")
        content.append(f"{candidate.status}\n", style="bold yellow")
        content.append(f"{self.translation_service.translate('label_registered_at')}: ", style="bold green")
        content.append(f"{candidate.registered_at}", style="white")

        panel = Panel(
            content,
            title=self.translation_service.translate('candidate_registered_title'),
            border_style="green",
            expand=False,
            box=self.box_style,
        )
        self.console.print(panel)

    def display_vacancy_match(self, vacancy_id: str, candidate: Candidate) -> None:
        """
        Render a blue info panel showing that a candidate has matched a vacancy.
        """
        content = Text()
        content.append(f"{self.translation_service.translate('label_vacancy_id')}: ", style="bold cyan")
        content.append(f"{vacancy_id}\n", style="white")
        content.append(f"{self.translation_service.translate('label_matched_candidate_id')}: ", style="bold cyan")
        content.append(f"{candidate.id}\n", style="white")
        content.append(f"{self.translation_service.translate('label_candidate_name')}: ", style="bold cyan")
        content.append(f"{candidate.name}\n", style="white")
        content.append(f"{self.translation_service.translate('label_candidate_status')}: ", style="bold cyan")
        content.append(f"{candidate.status}", style="bold yellow")

        panel = Panel(
            content,
            title=self.translation_service.translate('vacancy_matched_title'),
            border_style="cyan",
            expand=False,
            box=self.box_style,
        )
        self.console.print(panel)

    def display_no_match(self, vacancy_id: str) -> None:
        """
        Render a yellow warning panel indicating no candidate matched the vacancy.
        """
        content = Text(
            self.translation_service.translate('no_match_content', vacancy_id=vacancy_id),
            style="bold yellow",
        )
        panel = Panel(
            content,
            title=self.translation_service.translate('no_match_title'),
            border_style="yellow",
            expand=False,
            box=self.box_style,
        )
        self.console.print(panel)

    def display_error(self, title: str, message: str) -> None:
        """
        Render a red error panel for system or validation failures.
        """
        translated_title = self.translation_service.translate(title)
        translated_message = self.translation_service.translate(message)
        content = Text(translated_message, style="bold red")
        panel = Panel(
            content,
            title=f"[bold red]{translated_title}[/bold red]",
            border_style="red",
            expand=False,
            box=self.box_style,
        )
        self.console.print(panel)

    def display_dashboard(
        self,
        candidates: dict[str, Candidate],
        vacancies: dict[str, Vacancy],
        queues: dict[str, Queue],
    ) -> None:
        """
        Render a full status dashboard containing queue and vacancy statistics.
        """
        self.console.print("\n")
        header_text = self.translation_service.translate('dashboard_header')
        self.console.print(
            Align.center(f"[bold magenta]{header_text}[/bold magenta]")
        )
        self.console.print("\n")

        # 1. Summary Cards
        total_candidates = len(candidates)
        pending_candidates = sum(1 for c in candidates.values() if c.status == "PENDING")
        total_vacancies = len(vacancies)
        active_vacancies = sum(1 for v in vacancies.values() if not v.is_full())
        total_queues = len(queues)

        stats_text = Text()
        cand_str = self.translation_service.translate('stats_candidates', total=total_candidates, pending=pending_candidates)
        vac_str = self.translation_service.translate('stats_vacancies', total=total_vacancies, active=active_vacancies)
        q_str = self.translation_service.translate('stats_active_queues', total=total_queues)
        stats_text.append(f"{cand_str}\n", style="green")
        stats_text.append(f"{vac_str}\n", style="cyan")
        stats_text.append(f"{q_str}", style="yellow")

        stats_panel = Panel(
            stats_text,
            title=f"[bold white]{self.translation_service.translate('stats_title')}[/bold white]",
            border_style="white",
            expand=True,
            box=self.box_style,
        )
        self.console.print(stats_panel)
        self.console.print("\n")

        # 2. Queues Table
        q_table_title = self.translation_service.translate('queues_table_title')
        queues_table = Table(title=f"[bold yellow]{q_table_title}[/bold yellow]", expand=True, box=self.box_style)
        queues_table.add_column(self.translation_service.translate('col_profession_cbo'), style="bold yellow")
        queues_table.add_column(self.translation_service.translate('col_queue_length'), justify="right")
        queues_table.add_column(self.translation_service.translate('col_next_candidate_id'), style="cyan")
        queues_table.add_column(self.translation_service.translate('col_next_candidate_name'))

        for q_code, queue in queues.items():
            length = len(queue.candidate_ids)
            next_cand_id = "N/A"
            next_cand_name = "N/A"
            if length > 0:
                first_cand_id = queue.candidate_ids[0]
                first_cand = candidates.get(first_cand_id)
                if first_cand:
                    next_cand_id = first_cand.id
                    next_cand_name = first_cand.name
            queues_table.add_row(q_code, str(length), next_cand_id, next_cand_name)

        self.console.print(queues_table)
        self.console.print("\n")

        # 3. Vacancies Table
        v_table_title = self.translation_service.translate('vacancies_table_title')
        vacancies_table = Table(title=f"[bold cyan]{v_table_title}[/bold cyan]", expand=True, box=self.box_style)
        vacancies_table.add_column(self.translation_service.translate('col_id'), style="bold cyan")
        vacancies_table.add_column(self.translation_service.translate('col_title'))
        vacancies_table.add_column(self.translation_service.translate('col_cbo_code'))
        vacancies_table.add_column(self.translation_service.translate('col_zone'))
        vacancies_table.add_column(self.translation_service.translate('col_capacity'), justify="right")
        vacancies_table.add_column(self.translation_service.translate('col_placed'), justify="right")
        vacancies_table.add_column(self.translation_service.translate('col_expires_at'))

        for v in vacancies.values():
            vacancies_table.add_row(
                v.id,
                v.title,
                v.profession_code,
                v.sector_zone,
                str(v.capacity),
                str(len(v.placed_candidate_ids)),
                v.expires_at,
            )

        self.console.print(vacancies_table)
        self.console.print("\n")
