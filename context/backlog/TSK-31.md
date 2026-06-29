# TSK-31: CLI Accessibility Suite (Support for --no-color and Screen-Reader Linearization)

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** NFR05 / ACCESSIBILITY  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Ensure the FilaVaga console command line output is fully accessible to blind, colorblind, and visually impaired operators utilizing terminal screen readers (like NVDA/JAWS) and running in diverse host environments.

Tasks:
1. Implement the standard `NO_COLOR` environment variable detection and `--no-color` CLI parameter switch to completely disable all Rich/ANSI color escape sequences.
2. Structure the dashboard and queue output streams to render in a linear top-down format instead of horizontal grids, preventing reading order confusion for screen readers.
3. Replace visual-only status colors with clear text indicators (e.g. `[STATUS: ACTIVE]` instead of relying only on green/red text blocks).

## ✅ Definition of Ready (DoR)

* [x] Presenter localization adapter is fully functional and routes UI strings (TSK-29).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Testing/Quality - TDD]:** Test cases verify that setting environment variable `NO_COLOR=1` or parameter `--no-color` results in stdout containing pure text with zero ANSI color escape characters.
* [x] **[Functional - Screen Reader]:** Provide a command-line flag `--linear` or `--accessible` that formats all output as a simple linear stream rather than box-drawing ASCII grids.
* [x] **[Functional - Contrast]:** Ensure high contrast compliance for default terminal output layouts.
* [x] **[Verification]:** `pytest tests/test_infra.py` passes 100% green.
