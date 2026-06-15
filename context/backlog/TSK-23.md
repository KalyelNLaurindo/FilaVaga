# TSK-23: Vacancy Capacity Overflow Alerting

* **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** Future / Alerts & Observability  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement an overflow guard in the `Vacancy` domain entity and `QueueManager` to detect and alert when a vacancy's candidate queue attempts to exceed its declared capacity. Currently, the system silently accepts enqueue operations beyond the stated vacancy limit, causing data integrity issues where more candidates are assigned to a vacancy than it can actually fulfill. This task adds a domain-level invariant check and a corresponding CLI alert message so counselors are immediately informed when a vacancy reaches or exceeds capacity.

## ✅ Definition of Ready (DoR)

* [ ] TSK-05 (Vacancy Domain Entity) is complete — `Vacancy.capacity` and `Vacancy.current_fill` fields are defined and stable.
* [ ] TSK-06 (Queue Aggregate) is complete — inbound sequence logic is implemented.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Domain Invariant):** `Vacancy.is_at_capacity()` method returns `True` when `current_fill >= capacity`. Attempting to enqueue a candidate into a full vacancy raises `VacancyCapacityExceededError`.
* [ ] **Criterion 2 (QueueManager Guard):** `QueueManager.enqueue_candidate()` checks vacancy capacity before inserting. If full, it raises `VacancyCapacityExceededError` without modifying queue state.
* [ ] **Criterion 3 (CLI Alert):** The CLI presenter catches `VacancyCapacityExceededError` and renders a formatted Rich warning panel with vacancy ID, declared capacity, and current fill count.
* [ ] **Criterion 4 (Near-Capacity Warning):** When `current_fill / capacity >= 0.9` (90% full), a `[WARNING]` advisory is logged at enqueue time — not an error, just an observability signal.
* [ ] **Criterion 5 (Quality/Test):** Unit tests in `tests/test_domain.py` cover: enqueue at exactly capacity (raises), enqueue at 89% capacity (succeeds), and enqueue at 90% capacity (succeeds with warning logged).
