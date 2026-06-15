# TSK-05: Vacancy Domain Entity with Lazy-Evaluated TTL & Capacity

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** RF02 - Lazy TTL  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Build the `Vacancy` domain entity. Implement the capacity logic and lazy-evaluated TTL (Time-To-Live) validation: a vacancy expires when the current system clock surpasses `expires_at`. The vacancy must evaluate expiration dynamically based on the provided timestamp.

## ✅ Definition of Ready (DoR)

* [ ] TDD Setup: Test file 'tests/test_domain.py' is ready to test Vacancy logic
* [ ] Vacancy entity attributes (id, role, capacity, expires_at) designed

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] Vacancy class implements `is_expired(current_time)` dynamically
* [ ] State checks reject candidate placement if vacancy is full (capacity reached) or expired
* [ ] Tests mock or pass varying timestamps to check active vs expired status
