# TSK-33: Refactor Queue Aggregate for DDD Orthodox Self-Sufficiency

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** RF01 / Domain Modeling  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

In the current implementation of `Queue.add_candidate()`, the method requires injecting an external `candidates_map: dict[str, Candidate]` parameter to sort the queue chronologically by candidate registration time. In DDD orthodox terms, this leaks aggregate boundaries and introduces temporal coupling between `Queue` and a repository-like collection map inside the core entity.

To restore aggregate self-sufficiency and clean encapsulation of invariants:
1. Define a Value Object `QueueEntry` or `QueueItem` containing the `candidate_id` and the `registered_at` timestamp.
2. Refactor `Queue` to hold a list of `QueueEntry` objects rather than raw string IDs.
3. Update `add_candidate(candidate_id: str, registered_at: str)` to construct the `QueueEntry` and append it, sorting the list of entries using only internal data.
4. This preserves reference-by-ID across aggregate boundaries (since `Candidate` and `Queue` are separate Aggregate Roots) while making the `Queue` aggregate completely self-sufficient to maintain its chronological FIFO sequence invariant without external map injection.

## ✅ Definition of Ready (DoR)

* [x] Software Design Document updated with ADR-006 outlining the DDD Orthodox self-sufficiency strategy.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

### BDD Scenarios (Gherkin Format):

```gherkin
Scenario: Add candidate to empty queue
  Given an empty Queue for profession code "4110-10"
  When a candidate with ID "c1" registered at "2026-06-21T10:00:00Z" is added
  Then the queue contains exactly one entry with ID "c1"

Scenario: Maintain FIFO chronological sorting internally
  Given a Queue with candidates:
    | candidate_id | registered_at        |
    | c1           | 2026-06-21T10:00:00Z |
    | c3           | 2026-06-21T12:00:00Z |
  When a new candidate with ID "c2" registered at "2026-06-21T11:00:00Z" is added
  Then the queue sorted entries are:
    | candidate_id |
    | c1           |
    | c2           |
    | c3           |

Scenario: Reject duplicate candidates
  Given a Queue containing candidate "c1"
  When candidate "c1" is added again
  Then a DuplicateCandidateError is raised
```

* [ ] **[Functional]:** `Queue` does not receive `candidates_map` in any of its methods.
* [ ] **[Functional]:** Chronological FIFO sequencing is managed purely inside the `Queue` aggregate using `QueueEntry` value objects.
* [ ] **[Verification]:** pytest runs successfully with 100% pass rate. All use case tests and persistence tests are updated to reflect the new method signature.
