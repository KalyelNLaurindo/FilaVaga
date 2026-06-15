# TSK-11: SystemClock Adapter Implementation

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** Port & Adapter Integration / Testability Isolation  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement the `SystemClock` adapter providing ISO-8601 UTC time strings. This adapter is the concrete implementation of the outbound `IClock` port, ensuring accurate system clock access for production code while allowing tests to mock time.

## ✅ Definition of Ready (DoR)

* [x] TDD Setup: Test file 'tests/test_infra.py' is ready
* [x] Outbound IClock interface defined

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] SystemClock returns correct ISO-8601 UTC timestamp format
* [x] SystemClock correctly maps to python datetime module
* [x] Tests demonstrate mocking and overriding system clock values

