# TSK-04: Candidate Status State Machine Transition Rules

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** RF01 - State transition rules (PENDING -> CONTACTED -> PLACED / REJECTED)  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement state machine transition validation rules for a candidate's status. Transitions must strictly flow from `PENDING` -> `CONTACTED` -> `PLACED` or `REJECTED`. Any direct jump (e.g., PENDING -> PLACED) or backward transition must throw a domain exception.

## ✅ Definition of Ready (DoR)

* [x] TDD Setup: Test file 'tests/test_domain.py' is ready for testing state transitions
* [x] Custom Domain Exceptions (TSK-02) and Candidate entity (TSK-03) are defined

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] Candidate state mutation is encapsulated and validates target status before transition
* [x] Incorrect transitions throw DomainStateException
* [x] All state transition tests pass
