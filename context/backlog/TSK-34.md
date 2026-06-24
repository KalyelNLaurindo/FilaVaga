# TSK-34: HTTP REST API Backend Server Integration

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 5 Hours  
* **Story / Epic Reference:** RF09 / HTTP Backend Services  
* **Development Methodology:** TDD & Port-Adapter Pattern

## 📖 Description & Objectives

This task outlines the implementation of an HTTP REST API server using FastAPI (or a standard library HTTP server if strict zero-dependency is required). This allows FilaVaga to act as a backend, processing queue and candidate management operations via HTTP calls.

The server will expose endpoints mapping to the existing use cases:
1. `POST /candidates` - Register a candidate (triggers `RegisterCandidateUseCase`).
2. `POST /vacancies` - Register a vacancy (triggers `RegisterVacancyUseCase`).
3. `POST /queues/fill` - Try to fill a vacancy with the best candidate (triggers `FillVacancyUseCase`).
4. `GET /queues/status` - Query current queues and statistics.

## ✅ Definition of Ready (DoR)

* [ ] REST API design and endpoint specs outlined.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

### BDD Scenarios (Gherkin Format):

```gherkin
Scenario: Successfully register candidate via POST request
  Given the server is running
  When a POST request is sent to "/candidates" with payload:
    | name | profession_code | zone |
    | John | 4110-10         | LESTE|
  Then the response status code is 201
  And the candidate is registered in the database

Scenario: Attempt to register invalid candidate returns validation error
  Given the server is running
  When a POST request is sent to "/candidates" with missing name payload
  Then the response status code is 400
  And the response contains validation error details
```

* [ ] **[Functional]:** FastAPI/REST API server exposed.
* [ ] **[Functional]:** Endpoints route correctly to existing domain use cases.
* [ ] **[Verification]:** Integration tests using `TestClient` pass 100%.
