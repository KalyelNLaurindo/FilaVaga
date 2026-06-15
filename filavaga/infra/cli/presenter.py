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
from rich.columns import Columns
from filavaga.core.entities import Candidate, Vacancy, Queue


class RichConsolePresenter:
    """
    Console UI renderer using Rich components.
    
    Produces premium visual grids, status cards, and layout frames.
    """

    def __init__(self, console: Console | None = None):
        """
        Initialize the presenter with a Console instance.
        """
        self.console = console or Console()

    def display_candidate_registration(self, candidate: Candidate) -> None:
        """
        Render candidate registration details in a beautiful green success Panel.
        """
        content = Text()
        content.append("ID: ", style="bold green")
        content.append(f"{candidate.id}\n", style="white")
        content.append("Name: ", style="bold green")
        content.append(f"{candidate.name}\n", style="white")
        content.append("CBO (Profession): ", style="bold green")
        content.append(f"{candidate.profession_code}\n", style="white")
        content.append("Zone Preferred: ", style="bold green")
        content.append(f"{candidate.sector_zone}\n", style="white")
        content.append("Status: ", style="bold green")
        content.append(f"{candidate.status}\n", style="bold yellow")
        content.append("Registered At: ", style="bold green")
        content.append(f"{candidate.registered_at}", style="white")

        panel = Panel(
            content,
            title="[bold green]Candidate Registered Successfully[/bold green]",
            border_style="green",
            expand=False,
        )
        self.console.print(panel)

    def display_vacancy_match(self, vacancy_id: str, candidate: Candidate) -> None:
        """
        Render a blue info panel showing that a candidate has matched a vacancy.
        """
        content = Text()
        content.append("Vacancy ID: ", style="bold cyan")
        content.append(f"{vacancy_id}\n", style="white")
        content.append("Matched Candidate ID: ", style="bold cyan")
        content.append(f"{candidate.id}\n", style="white")
        content.append("Candidate Name: ", style="bold cyan")
        content.append(f"{candidate.name}\n", style="white")
        content.append("Candidate Status: ", style="bold cyan")
        content.append(f"{candidate.status}", style="bold yellow")

        panel = Panel(
            content,
            title="[bold cyan]Vacancy Matched Successfully[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
        self.console.print(panel)

    def display_no_match(self, vacancy_id: str) -> None:
        """
        Render a yellow warning panel indicating no candidate matched the vacancy.
        """
        content = Text(
            f"No matching candidate found in the FIFO queue for vacancy: {vacancy_id}.",
            style="bold yellow",
        )
        panel = Panel(
            content,
            title="[bold yellow]No Match Found[/bold yellow]",
            border_style="yellow",
            expand=False,
        )
        self.console.print(panel)

    def display_error(self, title: str, message: str) -> None:
        """
        Render a red error panel for system or validation failures.
        """
        content = Text(message, style="bold red")
        panel = Panel(
            content,
            title=f"[bold red]{title}[/bold red]",
            border_style="red",
            expand=False,
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
        self.console.print(
            Align.center("[bold magenta]━━━ FilaVaga Management Dashboard ━━━[/bold magenta]")
        )
        self.console.print("\n")

        # 1. Summary Cards
        total_candidates = len(candidates)
        pending_candidates = sum(1 for c in candidates.values() if c.status == "PENDING")
        total_vacancies = len(vacancies)
        active_vacancies = sum(1 for v in vacancies.values() if not v.is_full())
        total_queues = len(queues)

        stats_text = Text()
        stats_text.append(f"Candidates: {total_candidates} ({pending_candidates} Pending)\n", style="green")
        stats_text.append(f"Vacancies: {total_vacancies} ({active_vacancies} Active)\n", style="cyan")
        stats_text.append(f"Active Queues: {total_queues}", style="yellow")

        stats_panel = Panel(
            stats_text,
            title="[bold white]System Statistics[/bold white]",
            border_style="white",
            expand=True,
        )
        self.console.print(stats_panel)
        self.console.print("\n")

        # 2. Queues Table
        queues_table = Table(title="[bold yellow]Professional FIFO Queues[/bold yellow]", expand=True)
        queues_table.add_column("Profession CBO", style="bold yellow")
        queues_table.add_column("Queue Length", justify="right")
        queues_table.add_column("Next Candidate ID", style="cyan")
        queues_table.add_column("Next Candidate Name")

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
        vacancies_table = Table(title="[bold cyan]Active Vacancies[/bold cyan]", expand=True)
        vacancies_table.add_column("ID", style="bold cyan")
        vacancies_table.add_column("Title")
        vacancies_table.add_column("CBO Code")
        vacancies_table.add_column("Zone")
        vacancies_table.add_column("Capacity", justify="right")
        vacancies_table.add_column("Placed", justify="right")
        vacancies_table.add_column("Expires At")

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
