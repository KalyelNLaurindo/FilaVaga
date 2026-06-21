# TSK-26: File-System Access Permission Hardening

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** NFR03 / SECURITY  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Ensure candidate personal data (PII) processed locally is protected against unauthorized local access by other users on the same machine. This task implements strict file-system access control lists (ACLs/permissions) during data directory and state snapshot creation. 
On POSIX platforms, enforce `0700` permissions on the data directory and `0600` on the `state_snapshot.json` and backup files. On Windows systems, enforce restricted DACLs allowing access only to the current executing user and local SYSTEM account.

## ✅ Definition of Ready (DoR)

* [x] Persistence module `AtomicJsonRepository` exists and controls snapshot file generation (TSK-10).
* [x] Safe data scrubber `purge-all` implemented (TSK-16).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Testing/Quality - TDD]:** Unit/Integration tests verify that newly created snapshot and backup files are assigned restricted permissions matching the expected octal mode (`0600`) on Unix systems.
* [ ] **[Functional - Security]:** At repository startup and during write stages, directory permissions are validated/updated to ensure only the owner has read/write/traverse rights (`0700`).
* [ ] **[Functional - Windows ACLs]:** On Windows hosts, use standard system library calls to ensure the file security descriptor prevents other local users from opening the database.
* [ ] **[Verification]:** `pytest tests/test_infra.py` passes 100% green.
