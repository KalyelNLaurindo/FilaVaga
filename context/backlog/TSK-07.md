# TSK-07: Port Abstractions (Inbound & Outbound Interfaces)

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** Clean Architecture Core Isolation  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement Clean Architecture Port interfaces. Design inbound ports (`IRegisterCandidateUseCase`, `IMatchVacancyUseCase`) and outbound ports (`IStateRepository`, `IClock`) to isolate the core application service layer from UI and persistence infrastructure.

## ✅ Definition of Ready (DoR)

* [ ] TDD Setup: Test file 'tests/test_usecases.py' is ready
* [ ] Contracts and interfaces mapped out for clean separation

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] Interfaces are defined as Python Abstract Base Classes (ABCs) with abstract methods
* [ ] Domain and application services import only interfaces, not concrete adapters
* [ ] Type hints match the defined contracts perfectly
