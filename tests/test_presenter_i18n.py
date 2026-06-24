import pytest
from rich.console import Console
from filavaga.core.entities import Candidate, Vacancy, Queue, QueueEntry
from filavaga.infra.cli.presenter import RichConsolePresenter
from filavaga.infra.translation import TranslationService

def test_presenter_translation_candidate_registration(tmp_path):
    """Verify candidate registration panel renders in different languages."""
    # Setup locales
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir()
    
    import json
    with open(locales_dir / "pt.json", "w", encoding="utf-8") as f:
        json.dump({
            "candidate_registered_title": "[bold green]Candidato Registrado com Sucesso[/bold green]",
            "label_id": "Identificação",
            "label_name": "Nome do Candidato"
        }, f)
    with open(locales_dir / "en.json", "w", encoding="utf-8") as f:
        json.dump({
            "candidate_registered_title": "[bold green]Candidate Registered Successfully[/bold green]",
            "label_id": "ID",
            "label_name": "Name"
        }, f)

    candidate = Candidate(
        id="c_test", name="Maria Silva", sector_zone="SUL",
        profession_code="4110-10", registered_at="2026-06-15T12:00:00Z"
    )

    # 1. Portuguese Presenter
    service_pt = TranslationService(locales_dir=str(locales_dir), default_lang="pt")
    service_pt.resolve_lang(cli_lang="pt")
    
    console_pt = Console(record=True, width=80)
    presenter_pt = RichConsolePresenter(console=console_pt, translation_service=service_pt)
    presenter_pt.display_candidate_registration(candidate)
    
    out_pt = console_pt.export_text()
    assert "Candidato Registrado com Sucesso" in out_pt
    assert "Identificação" in out_pt
    assert "Nome do Candidato" in out_pt

    # 2. English Presenter
    service_en = TranslationService(locales_dir=str(locales_dir), default_lang="pt")
    service_en.resolve_lang(cli_lang="en")
    
    console_en = Console(record=True, width=80)
    presenter_en = RichConsolePresenter(console=console_en, translation_service=service_en)
    presenter_en.display_candidate_registration(candidate)
    
    out_en = console_en.export_text()
    assert "Candidate Registered Successfully" in out_en
    assert "ID" in out_en
    assert "Name" in out_en


def test_presenter_translation_dashboard(tmp_path):
    """Verify dashboard details are fully localized."""
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir()
    
    import json
    with open(locales_dir / "es.json", "w", encoding="utf-8") as f:
        json.dump({
            "dashboard_header": "━━━ Tablero de Control ━━━",
            "stats_title": "Estadísticas",
            "queues_table_title": "Colas FIFO",
            "vacancies_table_title": "Vacantes Activas",
            "col_profession_cbo": "CBO Profesional",
            "col_title": "Título",
            "stats_active_queues": "Colas Activas: {total}",
            "stats_candidates": "Candidatos: {total} ({pending} Pendientes)",
            "stats_vacancies": "Vacantes: {total} ({active} Activas)"
        }, f)

    service_es = TranslationService(locales_dir=str(locales_dir), default_lang="pt")
    service_es.resolve_lang(cli_lang="es")
    
    console = Console(record=True, width=120)
    presenter = RichConsolePresenter(console=console, translation_service=service_es)

    candidates = {
        "c_1": Candidate(id="c_1", name="Maria Silva", sector_zone="SUL", profession_code="4110-10", registered_at="2026-06-15T08:00:00Z")
    }
    vacancies = {
        "v_1": Vacancy(id="v_1", title="Auxiliar", profession_code="4110-10", sector_zone="SUL", capacity=2, created_at="2026-06-15T10:00:00Z", expires_at="2026-06-16T10:00:00Z")
    }
    queues = {
        "4110-10": Queue(profession_code="4110-10", entries=[QueueEntry(candidate_id="c_1", registered_at="2026-06-15T08:00:00Z")])
    }

    presenter.display_dashboard(candidates, vacancies, queues)
    out = console.export_text()
    
    assert "Tablero de Control" in out
    assert "Estadísticas" in out
    assert "Colas FIFO" in out
    assert "Vacantes Activas" in out
    assert "CBO Profesional" in out
    assert "Título" in out
    assert "Colas Activas: 1" in out
