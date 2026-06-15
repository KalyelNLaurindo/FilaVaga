# TSK-18: CSV Data Import Adapter

- **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer
- **Estimated Effort:** 2 Story Points / 8 Hours
- **Story / Epic Reference:** Future Enhancements / Legacy System Data Integration
- **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Build an inbound CLI command adapter and application port to import candidate registers and vacancy definitions from raw CSV files (e.g. legacy SINE spreadsheet exports) into the local atomic JSON database. The engine must automatically validate fields, align formats, and sanitize/obfuscate PII to protect candidate privacy.

## ✅ Definition of Ready (DoR)

- [ ] Target test file `tests/test_usecases.py` and `tests/test_infra.py` have test templates ready for CSV parsing errors and success runs.
- [ ] The CBO code mapping and sector zones schema definitions are finalized.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

- [ ] Implements the `--file` input flag under a new CLI route: `filavaga import-csv --file <path>`.
- [ ] Automatically matches and parses headers in a case-insensitive manner, reporting detailed row-by-row syntax or value errors (like invalid CBO codes or zone fields) to standard error instead of failing silently.
- [ ] Ensure all imported records are successfully appended to the corresponding FIFO queues.
- [ ] All tests pass without regression.
