# TSK-30: Interactive Shortcuts & Layperson Menu Enhancements

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** NFR05 / ACCESSIBILITY & UX  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Improve the command line interface usability for laypersons and non-technical counselors by introducing runtime prompt helpers and easy-to-use hotkey operations.

This task includes:
1. Adding a persistent status header bar indicating the currently active language and database status.
2. Implementing one-key execution prompts in the interactive shell (`[C] Register | [M] Match | [L] Language Selection | [Q] Quit`).
3. Adding a language selector dialog screen where laypersons can type a simple number (1 to 5) to dynamically switch languages in the active session.

## ✅ Definition of Ready (DoR)

* [x] UI translation mapping is fully implemented (TSK-29).
* [x] Interactive Command Router and CLI Presenter are integrated (TSK-12).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Functional - Interactive]:** The CLI supports dynamic session language switching when entering `L` or executing `--lang`.
* [x] **[Functional - UX]:** Renders unified single-character keyboard shortcuts inside the interactive prompt loops, allowing counselors to execute actions without typing full command names.
* [x] **[Functional - Fallback]:** Unicode box layouts fallback to simple ASCII boxes if the terminal session fails to support advanced typography.
* [x] **[Verification]:** `pytest tests/test_infra.py` passes 100% green.
