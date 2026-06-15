# TSK-19: Historical Archiving & Snapshot Optimization

* **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** Future Enhancements / Database Performance Optimization & LGPD Compliance  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Create an automated archiving routine to move candidates with final statuses (`PLACED` or `REJECTED`) older than 30 days out of the active database (`state_snapshot.json`) and store them in a secondary archive file (`archive_snapshot.json`). This keeps the active data light and ensures lookup operations remain well under the 5ms performance SLA.

## ✅ Definition of Ready (DoR)

* [ ] Custom outbound port `IArchiveRepository` defined.
* [ ] Mock system clock configured to test time-based transitions.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] Implement CLI command route: `filavaga archive --days <number_of_days>`.
* [ ] Atomic write guarantees apply to both the active file and the archive file during the transition, preventing data loss in case of system power failure.
* [ ] Unit tests verify that matching lookups exclude archived candidates, and active query latency remains extremely low.
