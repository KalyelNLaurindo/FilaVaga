# TSK-12: Argparse Command Router & Controller Adapter

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** User Interface / Console Commands Map  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement the `ArgparseCLIAdapter` command router. Map CLI console arguments (e.g., register candidate, match vacancy, show queue status) to corresponding application services and use cases.

## ✅ Definition of Ready (DoR)

* [ ] TDD Setup: Test file 'tests/test_infra.py' is ready
* [ ] CLI command inputs, options, and expected arguments designed

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] CLI router correctly parses command line arguments and routes execution
* [ ] Provides helpful error messages and usage documentation under --help
* [ ] Integration tests verify commands execute correctly using simulated sys.argv
