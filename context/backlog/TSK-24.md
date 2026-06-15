# TSK-24: Candidate Profile Schema Validator

* **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** Future / DX & Data Integrity  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement a schema validation layer for candidate data at the point of registration in the `QueueManager`. Currently, the `Candidate` domain entity accepts any dict-like structure at creation time, with minimal field-level validation. This task introduces a declarative schema (using Python dataclass field validators or a lightweight `TypedDict` + validation function) that enforces required fields (`name`, `registration_date`, `profile_type`, `availability_flag`), correct types, and business-rule constraints (e.g., `registration_date` cannot be in the future, `profile_type` must be a valid CBO code prefix). Invalid registrations are rejected before reaching the domain entity, keeping the core clean.

## ✅ Definition of Ready (DoR)

* [ ] TSK-03 (Candidate Domain Entity) is complete — field definitions are stable.
* [ ] Final list of required candidate fields and valid value ranges is agreed upon.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Schema Definition):** `CandidateSchema` defined in `filavaga/domain/schemas.py` with explicit field rules: required fields, types, and constraint predicates.
* [ ] **Criterion 2 (Validation Function):** `validate_candidate_payload(data: dict) -> CandidateSchema` raises `InvalidCandidatePayloadError` with a descriptive message listing all violated constraints when the input is invalid.
* [ ] **Criterion 3 (QueueManager Integration):** `QueueManager.register_candidate()` invokes the validator before constructing the `Candidate` entity. If validation fails, no candidate is created or added to the queue.
* [ ] **Criterion 4 (CLI Error Rendering):** `InvalidCandidatePayloadError` is caught at the CLI layer and rendered as a formatted Rich error table showing field name, expected type/constraint, and received value.
* [ ] **Criterion 5 (Quality/Test):** Unit tests in `tests/test_domain.py` assert: valid payload passes through, missing required field raises, future `registration_date` raises, invalid `profile_type` prefix raises, and error message contains the offending field name.
