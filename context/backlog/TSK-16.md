# TSK-16: LGPD-Compliant "purge-all" Safe Data Scrubber

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** NFR03 - Data Lifecycle Compliance  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement a secure, LGPD-compliant data scrubber. Build a clean command `purge-all` that safely and permanently wipes out all candidate history, database records, and backups from the local file system.

## ✅ Definition of Ready (DoR)

* [x] TDD Setup: Test file 'tests/test_infra.py' is ready
* [x] LGPD privacy requirements and file wiping procedure defined

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] Execution of 'purge-all' deletes database, backup (.bak), and log files completely
* [x] Performs system checks to ensure no file handles prevent complete deletion
* [x] Tests verify that after running the purge, no trace of candidate data remains
