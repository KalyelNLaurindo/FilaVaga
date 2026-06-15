# TSK-17: PyProject Configuration & PyInstaller Standalone Compilation

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** Distribution Strategy / Air-gapped Execution  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Configure the workspace using `pyproject.toml` and write build rules to generate a standalone executable file using `pyinstaller` (target single-binary compile). Ensure air-gapped workstations can run the application without installing Python.

## ✅ Definition of Ready (DoR)

* [x] TDD Setup: PyInstaller config file / pipeline scripts prepared
* [x] All python dependencies declared in pyproject.toml

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] PyInstaller compilation runs without error, producing a standalone executable
* [x] Executable starts up and successfully executes the CLI commands offline
* [x] Pyproject metadata contains valid, compliant project metadata details
