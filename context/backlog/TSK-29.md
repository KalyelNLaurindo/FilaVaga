# TSK-29: UI RichConsolePresenter Key-based Translation Mapping

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** NFR05 / ACCESSIBILITY & DX  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Refactor the `RichConsolePresenter` and CLI output renderers in FilaVaga to replace all hardcoded text strings with translation keys from the newly established `TranslationService`.

This includes:
1. Moving all UI text strings, dashboard labels, table headers, and status cards into language JSON dictionary files under `locales/`.
2. Updating `RichConsolePresenter` methods (`display_candidate_registration`, `display_vacancy_match`, `display_no_match`, `display_dashboard`) to fetch localized text dynamically from `TranslationService`.

## ✅ Definition of Ready (DoR)

* [x] i18n Translation Engine and resource structure are implemented (TSK-28).
* [x] `RichConsolePresenter` is fully implemented and prints console components (TSK-13).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Testing/Quality - TDD]:** Unit tests verify that calling presenter methods returns equivalent layouts and translated texts for at least 3 distinct active locales.
* [ ] **[Functional - Presenter]:** Zero hardcoded Portuguese/English words remain inside `RichConsolePresenter.py` codebase; all labels resolve via translation keys.
* [ ] **[Functional - Table Alignment]:** Localized strings with differing character lengths do not break Rich table borders or vertical alignments.
* [ ] **[Verification]:** `pytest tests/test_infra.py` passes 100% green.
