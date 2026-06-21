# TSK-27: Repository Reference Leak & Mutability Protection

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** NFR04 / DATA INTEGRITY  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Prevent memory-level state divergence and abstraction leaks in `AtomicJsonRepository`. 
Currently, the repository methods return direct references to mutable entities (`Candidate`, `Vacancy`, `Queue`) stored in memory. If the application layer mutates these entities directly (e.g. changing status, capacity, or queue order) without calling `.save_*()`, the in-memory state changes, causing a drift between the active runtime state and the persisted disk snapshot.

This task introduces deep copying (`copy.deepcopy`) on both read operations (returning copies of objects) and write operations (storing copies of objects) inside `AtomicJsonRepository`, ensuring strict encapsulation of repository-managed states.

## ✅ Definition of Ready (DoR)

* [x] Persistence module `AtomicJsonRepository` exists and controls snapshot file generation (TSK-10).
* [x] Core domain entities (`Candidate`, `Vacancy`, `Queue`) are fully modeled with valid state machine constraints.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Testing/Quality - TDD]:** Integration tests verify that modifying an entity returned by `get_candidate`, `get_all_candidates`, `get_vacancy`, `get_all_vacancies`, or `get_queue` does not mutate the internal repository state or the next returned instance of that entity.
* [ ] **[Testing/Quality - TDD]:** Integration tests verify that modifying an entity *after* passing it to `save_candidate`, `save_vacancy`, or `save_queue` does not affect the stored state inside the repository.
* [ ] **[Functional - Read Isolation]:** Methods `get_candidate`, `get_all_candidates`, `get_vacancy`, `get_all_vacancies`, and `get_queue` return deep copies of the internal dict objects using Python's `copy.deepcopy`.
* [ ] **[Functional - Write Isolation]:** Methods `save_candidate`, `save_vacancy`, and `save_queue` store deep copies of the passed domain models in the internal cache maps before invoking `_save_state_to_disk()`.
* [ ] **[Verification]:** `pytest tests/test_infra.py` passes 100% green.
