# TSK-15: Self-Healing JSON Schema Validator & Backup Recovery

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** Rule 15.2 - Auto-Healing  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement a self-healing startup validation routine. Upon starting, parse the active JSON database; if schema errors or corruption are detected, isolate the corrupt database file to `.err` and automatically recover from the latest `.bak` backup file.

## ✅ Definition of Ready (DoR)

* [ ] TDD Setup: Test file 'tests/test_infra.py' is ready
* [ ] Database recovery and backup naming convention established

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] Startup parses database and catches json.JSONDecodeError or schema issues
* [ ] Isolates corrupt files and successfully restores the .bak snapshot
* [ ] Integration tests simulate database corruption to verify self-healing logic works
