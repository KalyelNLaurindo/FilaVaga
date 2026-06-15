# TSK-06: Queue Aggregate & Inbound Sequence Rules

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** RF01 - FIFO Chronology  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Design the `Queue` aggregate protecting FIFO (First-In, First-Out) array constraints. Candidates added to the queue must be ordered and retrieved strictly based on their `registered_at` ISO-8601 timestamps, preventing any duplicate candidate IDs.

## ✅ Definition of Ready (DoR)

* [x] TDD Setup: Test file 'tests/test_domain.py' is ready for Queue aggregate validation
* [x] Queue aggregate boundaries, state, and methods sketched out

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] Queue aggregate strictly guarantees FIFO ordering
* [x] Candidate duplicate insertion is prevented and raises a domain exception
* [x] All FIFO extraction and ordering unit tests pass
