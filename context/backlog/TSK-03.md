# TSK-03: Candidate Domain Entity & Properties

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** RF01 - FIFO Engine  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Build the `Candidate` domain entity with absolute isolation and zero external dependencies. The candidate model must contain properties: `id`, `name`, `sector_zone`, `profession_code`, `registered_at` (ISO-8601 timestamp), and `status`.

## ✅ Definition of Ready (DoR)

* [x] TDD Setup: Test file 'tests/test_domain.py' is ready for adding Candidate unit tests
* [x] Properties, constraints, and types for Candidate entity defined

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] Candidate entity behaves correctly as a pure Python OOP model
* [x] Type hints are strictly applied to all attributes and methods
* [x] All tests in 'tests/test_domain.py' targeting Candidate are green
