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


from rich.layout import Layout


class RichConsolePresenter:
    """
    Console UI renderer using Rich components.
    
    Produces premium visual grids, status cards, and layout frames, fully localized.
    """

    def __init__(
        self,
        console: Console | None = None,
        translation_service = None,
        ascii_only: bool = False,
        no_color: bool = False,
        linear: bool = False,
    ):
        """
        Initialize the presenter with a Console instance and translation service.
        """
        import os
        # Detect standard NO_COLOR environment variable
        self.no_color = no_color or ("NO_COLOR" in os.environ)
        self.linear = linear

        if console:
            self.console = console
            if self.no_color:
                self.console._color_system = None
        else:
            self.console = Console(no_color=True if self.no_color else None)

        if translation_service is None:
            from filavaga.infra.translation import TranslationService
            translation_service = TranslationService()
        self.translation_service = translation_service
        
        # Determine box style (ASCII fallback)
        if ascii_only or os.environ.get("FILAVAGA_ASCII") == "1":
            self.box_style = box.ASCII
        else:
            self.box_style = box.SQUARE

    def _get_icon(self, msg_type: str) -> str:
        """Get the prefix icon for messages depending on NO_COLOR setting."""
        if self.no_color:
            mapping = {
                "success": "[Success] ",
                "error": "[Error] ",
                "warning": "[Warning] ",
                "info": "[Info] "
            }
        else:
            mapping = {
                "success": "✅ ",
                "error": "❌ ",
                "warning": "⚠️ ",
                "info": "ℹ️ "
            }
        return mapping.get(msg_type, "")

    def display_welcome_banner(self) -> None:
        """
        Renders a gorgeous branded ASCII art welcome banner on startup.
        """
        banner_text = r"""[bold cyan]
  _____ _ _      __     __              
 |  ___(_) | __ _\ \   / /_ _  __ _  __ _ 
 | |_  | | |/ _` |\ \ / / _` |/ _` |/ _` |
 |  _| | | | (_| | \ V / (_| | (_| | (_| |
 |_|   |_|_|\__,_|  \_/ \__,_|\__, |\__,_|
                              |___/       
[/bold cyan][bold white] Vacancy queue management engine | v2.1.0[/bold white]
[yellow] Type your choice from the menu options below to navigate.[/yellow]
"""
        # If no_color is True, rich Console will automatically strip styles.
        # But we also make sure raw text is printed clean.
        self.console.print(banner_text)

    def display_separator(self) -> None:
        """
        Renders a thin visual divider line to separate consecutive REPL cycle outputs.
        """
        width = self.console.size.width
        char = "-" if self.box_style == box.ASCII else "─"
        self.console.print(char * width, style="dim" if not self.no_color else None)

    def display_candidate_registration(self, candidate: Candidate) -> None:
        """
        Render candidate registration details in a beautiful green success Panel.
        """
        icon = self._get_icon("success")
        raw_title = self.translation_service.translate('candidate_registered_title')
        title = f"{icon}{raw_title}"

        if self.linear:
            import re
            clean_title = re.sub(r"\[.*?\]", "", title)
            
            content = f"=== {clean_title} ===\n"
            content += f"{self.translation_service.translate('label_id')}: {candidate.id}\n"
            content += f"{self.translation_service.translate('label_name')}: {candidate.name}\n"
            content += f"{self.translation_service.translate('label_profession')}: {candidate.profession_code}\n"
            content += f"{self.translation_service.translate('label_zone')}: {candidate.sector_zone}\n"
            content += f"{self.translation_service.translate('label_status')}: [STATUS: {candidate.status}]\n"
            content += f"{self.translation_service.translate('label_registered_at')}: {candidate.registered_at}"
            self.console.print(content, highlight=False)
            return

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
        content.append(f"[STATUS: {candidate.status}]\n", style="bold yellow")
        content.append(f"{self.translation_service.translate('label_registered_at')}: ", style="bold green")
        content.append(f"{candidate.registered_at}", style="white")

        panel = Panel(
            content,
            title=title,
            border_style="green",
            expand=False,
            box=self.box_style,
        )
        self.console.print(panel)

    def display_vacancy_match(self, vacancy_id: str, candidate: Candidate) -> None:
        """
        Render a blue info panel showing that a candidate has matched a vacancy.
        """
        icon = self._get_icon("success")
        raw_title = self.translation_service.translate('vacancy_matched_title')
        title = f"{icon}{raw_title}"

        if self.linear:
            import re
            clean_title = re.sub(r"\[.*?\]", "", title)
            
            content = f"=== {clean_title} ===\n"
            content += f"{self.translation_service.translate('label_vacancy_id')}: {vacancy_id}\n"
            content += f"{self.translation_service.translate('label_matched_candidate_id')}: {candidate.id}\n"
            content += f"{self.translation_service.translate('label_candidate_name')}: {candidate.name}\n"
            content += f"{self.translation_service.translate('label_candidate_status')}: [STATUS: {candidate.status}]"
            self.console.print(content, highlight=False)
            return

        content = Text()
        content.append(f"{self.translation_service.translate('label_vacancy_id')}: ", style="bold cyan")
        content.append(f"{vacancy_id}\n", style="white")
        content.append(f"{self.translation_service.translate('label_matched_candidate_id')}: ", style="bold cyan")
        content.append(f"{candidate.id}\n", style="white")
        content.append(f"{self.translation_service.translate('label_candidate_name')}: ", style="bold cyan")
        content.append(f"{candidate.name}\n", style="white")
        content.append(f"{self.translation_service.translate('label_candidate_status')}: ", style="bold cyan")
        content.append(f"[STATUS: {candidate.status}]", style="bold yellow")

        panel = Panel(
            content,
            title=title,
            border_style="cyan",
            expand=False,
            box=self.box_style,
        )
        self.console.print(panel)

    def display_no_match(self, vacancy_id: str) -> None:
        """
        Render a yellow warning panel indicating no candidate matched the vacancy.
        """
        icon = self._get_icon("warning")
        raw_title = self.translation_service.translate('no_match_title')
        title = f"{icon}{raw_title}"

        if self.linear:
            import re
            clean_title = re.sub(r"\[.*?\]", "", title)
            raw_content = self.translation_service.translate('no_match_content', vacancy_id=vacancy_id)
            clean_content = re.sub(r"\[.*?\]", "", raw_content)
            
            content = f"=== {clean_title} ===\n"
            content += clean_content
            self.console.print(content, highlight=False)
            return

        content = Text(
            self.translation_service.translate('no_match_content', vacancy_id=vacancy_id),
            style="bold yellow",
        )
        panel = Panel(
            content,
            title=title,
            border_style="yellow",
            expand=False,
            box=self.box_style,
        )
        self.console.print(panel)

    def display_error(self, title: str, message: str) -> None:
        """
        Render a red error panel for system or validation failures.
        """
        icon = self._get_icon("error")
        translated_title = self.translation_service.translate(title)
        translated_message = self.translation_service.translate(message)
        title_with_icon = f"{icon}{translated_title}"

        if self.linear:
            import re
            clean_title = re.sub(r"\[.*?\]", "", title_with_icon)
            clean_message = re.sub(r"\[.*?\]", "", translated_message)
            
            content = f"=== ERROR: {clean_title} ===\n"
            content += clean_message
            self.console.print(content, highlight=False)
            return

        content = Text(translated_message, style="bold red")
        panel = Panel(
            content,
            title=f"[bold red]{title_with_icon}[/bold red]",
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
        if self.linear:
            import re
            self.console.print("\n", highlight=False)
            header_text = self.translation_service.translate('dashboard_header')
            clean_header = re.sub(r"\[.*?\]", "", header_text)
            self.console.print(f"=== {clean_header} ===\n", highlight=False)

            # 1. Summary Cards
            total_candidates = len(candidates)
            pending_candidates = sum(1 for c in candidates.values() if c.status == "PENDING")
            total_vacancies = len(vacancies)
            active_vacancies = sum(1 for v in vacancies.values() if not v.is_full())
            total_queues = len(queues)

            cand_str = self.translation_service.translate('stats_candidates', total=total_candidates, pending=pending_candidates)
            vac_str = self.translation_service.translate('stats_vacancies', total=total_vacancies, active=active_vacancies)
            q_str = self.translation_service.translate('stats_active_queues', total=total_queues)

            stats_title = self.translation_service.translate('stats_title')
            clean_stats_title = re.sub(r"\[.*?\]", "", stats_title)

            self.console.print(f"[{clean_stats_title}]", highlight=False)
            self.console.print(re.sub(r"\[.*?\]", "", cand_str), highlight=False)
            self.console.print(re.sub(r"\[.*?\]", "", vac_str), highlight=False)
            self.console.print(re.sub(r"\[.*?\]", "", q_str), highlight=False)
            self.console.print("\n", highlight=False)

            # 2. Queues List
            q_table_title = self.translation_service.translate('queues_table_title')
            clean_q_title = re.sub(r"\[.*?\]", "", q_table_title)
            self.console.print(f"[{clean_q_title}]", highlight=False)

            col_cbo = self.translation_service.translate('col_profession_cbo')
            col_len = self.translation_service.translate('col_queue_length')
            col_next_id = self.translation_service.translate('col_next_candidate_id')
            col_next_name = self.translation_service.translate('col_next_candidate_name')

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
                line = f"{col_cbo}: {q_code} | {col_len}: {length} | {col_next_id}: {next_cand_id} | {col_next_name}: {next_cand_name}"
                self.console.print(re.sub(r"\[.*?\]", "", line), highlight=False)
            self.console.print("\n", highlight=False)

            # 3. Vacancies List
            v_table_title = self.translation_service.translate('vacancies_table_title')
            clean_v_title = re.sub(r"\[.*?\]", "", v_table_title)
            self.console.print(f"[{clean_v_title}]", highlight=False)

            col_id = self.translation_service.translate('col_id')
            col_title = self.translation_service.translate('col_title')
            col_cbo_code = self.translation_service.translate('col_cbo_code')
            col_zone = self.translation_service.translate('col_zone')
            col_capacity = self.translation_service.translate('col_capacity')
            col_placed = self.translation_service.translate('col_placed')
            col_expires = self.translation_service.translate('col_expires_at')

            for v in vacancies.values():
                import datetime as dt
                now_str = dt.datetime.utcnow().isoformat() + "Z"
                is_exp = v.is_expired(now_str)
                is_full = v.is_full()
                if is_exp:
                    vac_status = "EXPIRED"
                elif is_full:
                    vac_status = "FULL"
                else:
                    vac_status = "ACTIVE"

                line = f"{col_id}: {v.id} | {col_title}: {v.title} | {col_cbo_code}: {v.profession_code} | {col_zone}: {v.sector_zone} | {col_capacity}: {v.capacity} | {col_placed}: {len(v.placed_candidate_ids)} | {col_expires}: {v.expires_at} | [STATUS: {vac_status}]"
                self.console.print(re.sub(r"\[.*?\]", "", line), highlight=False)
            self.console.print("\n", highlight=False)
            return

        # Multi-pane Senior TUI Layout Rendering
        total_candidates = len(candidates)
        pending_candidates = sum(1 for c in candidates.values() if c.status == "PENDING")
        total_vacancies = len(vacancies)
        active_vacancies = sum(1 for v in vacancies.values() if not v.is_full())
        total_queues = len(queues)

        # 1. Header Card (Statistics Summary)
        stats_text = Text()
        cand_str = self.translation_service.translate('stats_candidates', total=total_candidates, pending=pending_candidates)
        vac_str = self.translation_service.translate('stats_vacancies', total=total_vacancies, active=active_vacancies)
        q_str = self.translation_service.translate('stats_active_queues', total=total_queues)
        stats_text.append(f"{cand_str}   •   ", style="green")
        stats_text.append(f"{vac_str}   •   ", style="cyan")
        stats_text.append(f"{q_str}", style="yellow")

        header_panel = Panel(
            Align.center(stats_text),
            title=f"[bold white]{self.translation_service.translate('stats_title')}[/bold white]",
            border_style="magenta",
            expand=True,
            box=self.box_style,
        )

        # 2. Queues Table Card (Left Side)
        q_table_title = self.translation_service.translate('queues_table_title')
        queues_table = Table(expand=True, box=self.box_style)
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

        queues_panel = Panel(
            queues_table,
            title=f"[bold yellow]{q_table_title}[/bold yellow]",
            border_style="yellow",
            expand=True,
            box=self.box_style,
        )

        # 3. Vacancies Table Card (Right Side)
        v_table_title = self.translation_service.translate('vacancies_table_title')
        vacancies_table = Table(expand=True, box=self.box_style)
        vacancies_table.add_column(self.translation_service.translate('col_id'), style="bold cyan")
        vacancies_table.add_column(self.translation_service.translate('col_title'))
        vacancies_table.add_column(self.translation_service.translate('col_cbo_code'))
        vacancies_table.add_column(self.translation_service.translate('col_capacity'), justify="right")
        vacancies_table.add_column(self.translation_service.translate('col_placed'), justify="right")

        # Display up to top 6 vacancies in the dashboard row layout to avoid scrolling issues
        for v in list(vacancies.values())[:6]:
            vacancies_table.add_row(
                v.id,
                v.title,
                v.profession_code,
                str(v.capacity),
                str(len(v.placed_candidate_ids)),
            )

        vacancies_panel = Panel(
            vacancies_table,
            title=f"[bold cyan]{v_table_title}[/bold cyan]",
            border_style="cyan",
            expand=True,
            box=self.box_style,
        )

        # Width-based adaptive layout: if too narrow, stack vertically to avoid wrapping truncation
        width = self.console.size.width
        if width < 100:
            self.console.print("\n")
            header_text = self.translation_service.translate('dashboard_header')
            self.console.print(Align.center(f"[bold magenta]{header_text}[/bold magenta]"))
            self.console.print("\n")
            self.console.print(header_panel)
            self.console.print("\n")
            self.console.print(queues_panel)
            self.console.print("\n")
            self.console.print(vacancies_panel)
            self.console.print("\n")
            return

        # Assemble into Layout for wider terminals
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1)
        )
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )

        layout["header"].update(header_panel)
        layout["body"]["left"].update(queues_panel)
        layout["body"]["right"].update(vacancies_panel)

        self.console.print("\n")
        header_text = self.translation_service.translate('dashboard_header')
        self.console.print(Align.center(f"[bold magenta]{header_text}[/bold magenta]"))
        self.console.print("\n")
        self.console.print(layout)
        self.console.print("\n")
