# TSK-35: Terminal UI/UX Overhaul — Interactive Shell Visual Redesign

* **Owner / Assignee:** Kalyel Nunes Laurindo / PO  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** FT-18 / UX Terminal  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

The current interactive CLI loop (`filavaga>` prompt) is functional but visually raw. It lacks a proper welcome banner, clear visual hierarchy in command outputs, consistent color/icon feedback conventions, and visual separation between consecutive command cycles. This task performs a full visual redesign of the interactive shell without breaking any existing functionality.

### Pain Points Identified (User Reported)

1. **No welcome screen / banner** — The user enters the raw prompt with no context about the application name, version, or available commands.
2. **Unformatted output** — Queue listings, candidate status, and match results are plain text with no visual structure.
3. **Inconsistent feedback** — Success, warning, and error messages have no consistent color/icon convention across commands.
4. **No visual separation** — Each command's output blends visually into the next REPL cycle.
5. **Unpollished prompt** — The `filavaga>` prompt lacks color or visual affordance to guide the user.

### Deliverables

1. **Branded ASCII banner** displayed once on shell startup — app name, version, tagline ("Vacancy queue management engine"), and a hint to type `help`.
2. **Color-coded prompt** — `filavaga ❯` in cyan, with user input in default terminal color.
3. **Consistent message icons** — `✅` success, `⚠️` warning, `❌` error, `ℹ️` info — prepended to all feedback lines across all commands.
4. **Boxed output sections** — Queue listing and match results wrapped in light Unicode box borders (`╭`, `─`, `│`, `╰`) for visual clarity.
5. **Separator lines** — Thin `─` dividers printed between consecutive command output cycles in the REPL.
6. **Graceful degradation** — All enhancements behind a `supports_unicode()` check; plain ASCII fallback for restricted terminals and `NO_COLOR=1` env.

## ✅ Definition of Ready (DoR)

* [x] Interactive CLI loop is implemented and functional (shipped as part of the TSK-33 interactive shell fix).
* [x] `colorama` or `rich` is available in the dependency stack for color rendering.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Functional - Banner]:** Launching `filavaga.exe` or `python -m filavaga` displays a branded ASCII banner with name, version, and tagline before entering the prompt.
* [ ] **[Functional - Prompt]:** The REPL prompt renders as a colored `filavaga ❯` with user input in default color.
* [ ] **[Functional - Feedback Icons]:** All success/error/warning/info outputs consistently prepend the appropriate icon across every command (`add-candidate`, `add-vacancy`, `fill-queue`, `status`, `purge`, etc.).
* [ ] **[Functional - Tables]:** Queue listings and match results render inside Unicode box borders with aligned columns.
* [ ] **[Functional - Separators]:** A thin `─` divider is printed after each command output in the REPL cycle.
* [ ] **[Functional - Fallback]:** `NO_COLOR=1` or `--no-color` strips ANSI codes and replaces Unicode box chars with plain ASCII equivalents (`+`, `-`, `|`).
* [ ] **[Testing/Quality - TDD]:** Visual rendering helpers are unit-tested via `capsys` stdout capture, asserting presence of icons, borders, and dividers per scenario.
* [ ] **[Verification]:** `python -m pytest` runs successfully with 100% pass rate (no regressions).
