# TSK-02: Custom Domain Exceptions & Error Mapping

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** Architecture Hardening / System resilience  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Define custom domain exceptions to encapsulate errors within the core domain boundary. Create specific exceptions for operations like invalid state transitions, missing entities, capacity limits, and expired entities, preventing infrastructure leaks.

## ✅ Definition of Ready (DoR)

* [x] TDD Setup: Test file 'tests/test_domain.py' path is determined and ready for Red phase
* [x] Base architecture exception structure designed and agreed upon

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] All core custom exceptions inherit from a base domain exception
* [x] Exceptions are raised appropriately in domain entities and aggregates (tested in 'tests/test_domain.py')
* [x] Exceptions preserve clear, debugging-friendly message formats
