# TSK-01: Configuration Validation & Directory Setup

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** NFR03 / ADR-001 (Local directory pathing & environment validation)  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Initialize the application environment. Implement a config loader module that verifies the runtime configuration, validates directory permissions for local data storage, and sets up required structures (like checking target directory privileges on `%USERPROFILE%/.filavaga` or `~/.filavaga`).

## ✅ Definition of Ready (DoR)

* [x] TDD Setup: Test file 'tests/test_infra.py' path is determined and ready for Red phase
* [x] Configuration JSON schema defined and validated

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] Configuration validation logic verifies if path privileges exist before running
* [x] If settings/directories do not exist, they are initialized gracefully
* [x] Tests check for invalid JSON or missing parameters in configuration
* [x] All unit/integration tests pass in 'tests/test_infra.py'
