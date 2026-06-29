# TSK-21: Anonymized Placement Analytics Export

* **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** Future Enhancements / System Telemetry and Regional Reporting  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Develop an analytics module to calculate key performance and efficiency indicators (KPIs) like average wait time in queues, candidate placement rates by occupational CBO classification, and vacancy fulfillment speed. To maintain strict compliance with LGPD, all individual names and IDs must be completely omitted from the output.

## ✅ Definition of Ready (DoR)

* [x] Formula and parameters for wait time and placement metrics aligned with SINE criteria.
* [x] Target CSV header schema defined.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] Implement CLI command route: `filavaga export-stats --output <csv_path>`.
* [x] The exported file contains aggregate tables categorized by sector zones and CBO codes.
* [x] No PII (names, specific timestamps, candidate IDs) is written to the output file.
* [x] Unit tests ensure that calculation edge cases (e.g. empty queues, instant matches) do not trigger divide-by-zero errors.
