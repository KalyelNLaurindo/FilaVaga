# TSK-09: MatchEngine Multi-Filter Matching Algorithm

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** RF03 - Multi-Filter & RF02 - Lazy Evaluation  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Develop the `MatchEngine` service implementing `IMatchVacancyUseCase`. It must iterate and match queued candidates to active vacancies using secondary fast-index mappings. Exclude any vacancies that have expired (lazy TTL check) or reached maximum capacity.

## ✅ Definition of Ready (DoR)

* [ ] TDD Setup: Test file 'tests/test_usecases.py' is ready
* [ ] Lazy-evaluated TTL and matching filters defined

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] Matches candidates to vacancies based on sector, role code, and availability
* [ ] Expired vacancies are skipped dynamically during matching
* [ ] Unit tests verify edge cases for partially filled, fully filled, and expired vacancies
