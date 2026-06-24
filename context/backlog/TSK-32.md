# TSK-32: Implement Unit of Work (UoW) Pattern for Multi-Repository Atomic Transactions

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** NFR04 / DATA INTEGRITY  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement the **Unit of Work** design pattern in FilaVaga using Python's context manager interface (`with` blocks) to guarantee referential integrity and transaction atomic behavior across multiple repositories.

Currently, use cases (like `QueueManager` and `MatchEngine`) perform sequential writes directly on individual repositories (e.g. `save_candidate`, `save_queue`). If a power failure or disk error happens mid-operation, the in-memory database becomes split-brain (e.g., candidate status shifts to `CONTACTED` but queue fails to update).

This task will:
1. Create a `IUnitOfWork` context interface and concrete repository-backed manager.
2. Ensure changes remain volatile/in-memory and are only flushed atomically to disk upon successful completion of the `with` block (`commit()`).
3. Roll back memory modifications on exception events to prevent state pollution.

## ✅ Definition of Ready (DoR)

* [x] Persistence module `AtomicJsonRepository` exists and supports database saves (TSK-10).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Testing/Quality - TDD]:** Test cases verify that if an exception is thrown inside a use case transaction, no changes are written to the JSON file database (Rollback).
* [x] **[Functional - UoW]:** Refactor `QueueManager` and application use cases to run all write queries within the `UnitOfWork` context manager.
* [x] **[Functional - Atomic Commit]:** The JSON database snapshot file on disk is only written once at the exit of the UoW context block instead of multiple times per operation.
* [x] **[Verification]:** `pytest tests/test_infra.py` passes 100% green.
