# TSK-25: Queue Snapshot Serializer & Replay

* **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer  
* **Estimated Effort:** 4 Story Points / 16 Hours  
* **Story / Epic Reference:** Future / Resilience & Disaster Recovery  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement a full-state snapshot mechanism for the in-memory queue system. FilaVaga is currently session-based and stateless between runs — all queue data is lost when the process exits. While full persistence is out of scope for the core MVP, this task introduces an opt-in snapshot/replay capability: at any point, the operator can execute `filavaga snapshot --output <path>` to serialize the complete queue state (all candidates, vacancies, statuses, and TTL metadata) to a JSON file. A subsequent `filavaga replay --input <path>` command rehydrates the engine deterministically from that snapshot. This enables disaster recovery for long-running operational sessions without requiring a database.

## ✅ Definition of Ready (DoR)

* [ ] TSK-10 (Thread-Safe Atomic JSON Persistence Engine) is complete — atomic write mechanism is available for reuse.
* [ ] TSK-05 (Vacancy TTL) is complete — TTL metadata is part of the serializable state.
* [ ] All domain entities (`Candidate`, `Vacancy`, `Queue`) are serializable to dict form.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Snapshot Command):** CLI command `filavaga snapshot --output <path>` serializes the full queue state to a valid JSON file using the existing atomic writer. Includes a schema version field for forward compatibility.
* [ ] **Criterion 2 (Replay Command):** CLI command `filavaga replay --input <path>` reads the snapshot file, validates the schema version, and rehydrates all domain entities into the `QueueManager` in-memory state.
* [ ] **Criterion 3 (Deterministic Replay):** After a full snapshot/replay cycle, the results of `filavaga list-queue` and `filavaga match` commands are byte-for-byte identical to the pre-snapshot state for the same inputs.
* [ ] **Criterion 4 (TTL Awareness):** During replay, vacancies whose TTL has already expired at the moment of replay are immediately marked as `EXPIRED` rather than being restored to `ACTIVE` state — preventing stale data resurrection.
* [ ] **Criterion 5 (Corruption Guard):** If the snapshot file is malformed or its schema version is incompatible, `replay` raises `SnapshotCorruptedError` with a clear message and does NOT modify the current in-memory state.
* [ ] **Criterion 6 (Quality/Test):** Integration tests in `tests/test_infra.py` assert: snapshot produces valid JSON, replay restores identical state, expired TTL vacancies are marked correctly on replay, and corrupted input raises `SnapshotCorruptedError` without side effects.
