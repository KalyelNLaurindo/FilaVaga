# **📋 Agile Backlog & Task Management: FilaVaga**

**Role:** Agile Coach / Tech Lead / Project Manager

**Objective:** Maintain a prioritizable backlog of atomic, SMART tasks, tracking their progress across a basic Markdown Kanban board from planning to verification.

**Context:** FilaVaga — Highly optimized, local in-memory queue-management engine featuring high-precision FIFO queues, dynamic lazy-evaluated vacancy TTL expiration, and atomic JSON persistence.

## **🏛️ Backlog Metadata**

- **Project Owner:** Kalyel N. Laurindo / Project Owner
- **Lead Tech Lead:** Kalyel N. Laurindo / Software Engineer
- **Current Sprint / Iteration:** Sprint 1 (Foundational & Core Engine)
- **Target Delivery Date:** July 15, 2026
- **Document Version:** v1.2

## **1. 📊 Prioritization & Task Sizing Framework**

- **Field 1.0 - Prioritization & Estimation Framework:** Hybrid RICE Score & Fibonacci Story Points.

### **1.1. RICE Score Calculation Formula**

$$RICE = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

- **Reach (1-100):** Proportion of system flows or user touchpoints affected.
- **Impact (0.5-3.0):** Contribution to product vision ($3.0 = \text{Massive}$, $2.0 = \text{High}$, $1.0 = \text{Medium}$, $0.5 = \text{Low}$).
- **Confidence (0.5-1.0):** Certainty of technical/operational estimates ($1.0 = \text{High/100\%}$, $0.8 = \text{Medium/80\%}$, $0.5 = \text{Low/50\%}$).
- **Effort (1-5 Story Points / Complexity):** Total engineering effort ($1 = \text{Low/Very simple}$, $5 = \text{High/Very complex}$).

## **2. 🗂️ Prioritized Product Backlog Ledger**

Tasks are mapped bottom-up matching the hexagonal boundaries and dependencies.

### **📦 Backlog Phase 1: Backing Infrastructure & Configuration Setup**

- [**TSK-01**](https://gemini.google.com/app/tasks/TSK-01.md): Configuration Validation & Directory Setup 

  $$ARCH-ENABLER$$

  - *Epic/Requirement Link:* NFR03 / ADR-001 (Local directory pathing & environment validation)
  - *Metrics:* Reach: 80 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - *RICE Score:* 240.0
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* Done (Pre-bootstrapped workspace)

- [**TSK-02**](https://gemini.google.com/app/tasks/TSK-02.md): Custom Domain Exceptions & Error Mapping 

  $$ARCH-ENABLER$$

  - *Epic/Requirement Link:* Architecture Hardening / System resilience
  - *Metrics:* Reach: 90 | Impact: 2.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - *RICE Score:* 180.0
  - *TDD Test File:* `tests/test_domain.py`
  - *Status:* Done

### **⚙️ Backlog Phase 2: Bounded Domain Context & Core Models**

- [**TSK-03**](https://gemini.google.com/app/tasks/TSK-03.md)**: Candidate Domain Entity & Properties**
  - *Epic/Requirement Link:* RF01 - FIFO Engine
  - *Metrics:* Reach: 90 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - *RICE Score:* 270.0
  - *TDD Test File:* `tests/test_domain.py`
  - *Status:* To Do
- [**TSK-04**](https://gemini.google.com/app/tasks/TSK-04.md)**: Candidate Status State Machine Transition Rules**
  - *Epic/Requirement Link:* RF01 - State transition rules (`PENDING` ➔ `CONTACTED` ➔ `PLACED` / `REJECTED`)
  - *Metrics:* Reach: 85 | Impact: 3.0 | Confidence: 0.9 | Effort: 1 (1 SP)
  - *RICE Score:* 229.5
  - *TDD Test File:* `tests/test_domain.py`
  - *Status:* To Do
- [**TSK-05**](https://gemini.google.com/app/tasks/TSK-05.md)**: Vacancy Domain Entity with Lazy-Evaluated TTL & Capacity**
  - *Epic/Requirement Link:* RF02 - Lazy TTL
  - *Metrics:* Reach: 85 | Impact: 3.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - *RICE Score:* 114.7
  - *TDD Test File:* `tests/test_domain.py`
  - *Status:* To Do
- [**TSK-06**](https://gemini.google.com/app/tasks/TSK-06.md)**: Queue Aggregate & Inbound Sequence Rules**
  - *Epic/Requirement Link:* RF01 - FIFO Chronology
  - *Metrics:* Reach: 90 | Impact: 3.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - *RICE Score:* 121.5
  - *TDD Test File:* `tests/test_domain.py`
  - *Status:* To Do

### **🧠 Backlog Phase 3: Test-Driven Core Logic (Use Cases)**

- [**TSK-07**](https://gemini.google.com/app/tasks/TSK-07.md)**: Port Abstractions (Inbound & Outbound Interfaces)**
  - *Epic/Requirement Link:* Clean Architecture Core Isolation
  - *Metrics:* Reach: 95 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - *RICE Score:* 285.0
  - *TDD Test File:* `tests/test_usecases.py`
  - *Status:* To Do
- [**TSK-08**](https://gemini.google.com/app/tasks/TSK-08.md)**: QueueManager Application Service Execution Logic**
  - *Epic/Requirement Link:* RF01 - Candidate registration & state management
  - *Metrics:* Reach: 95 | Impact: 3.0 | Confidence: 0.8 | Effort: 2 (2 SP)
  - *RICE Score:* 114.0
  - *TDD Test File:* `tests/test_usecases.py`
  - *Status:* To Do
- [**TSK-09**](https://gemini.google.com/app/tasks/TSK-09.md)**: MatchEngine Multi-Filter Matching Algorithm**
  - *Epic/Requirement Link:* RF03 - Multi-Filter & RF02 - Lazy Evaluation
  - *Metrics:* Reach: 95 | Impact: 3.0 | Confidence: 0.8 | Effort: 3 (3 SP)
  - *RICE Score:* 76.0
  - *TDD Test File:* `tests/test_usecases.py`
  - *Status:* To Do

### **🔌 Backlog Phase 4: Interface Adapters & Persistence Adapters**

- [**TSK-10**](https://gemini.google.com/app/tasks/TSK-10.md)**: Thread-Safe Atomic JSON Persistence Engine**
  - *Epic/Requirement Link:* RF04 - Atomic Save / ADR-002 Concurrency
  - *Metrics:* Reach: 100 | Impact: 3.0 | Confidence: 0.9 | Effort: 3 (3 SP)
  - *RICE Score:* 90.0
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* To Do
- [**TSK-11**](https://gemini.google.com/app/tasks/TSK-11.md)**: SystemClock Adapter Implementation**
  - *Epic/Requirement Link:* Port & Adapter Integration / Testability Isolation
  - *Metrics:* Reach: 100 | Impact: 2.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - *RICE Score:* 200.0
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* To Do
- [**TSK-12**](https://gemini.google.com/app/tasks/TSK-12.md)**: Argparse Command Router & Controller Adapter**
  - *Epic/Requirement Link:* User Interface / Console Commands Map
  - *Metrics:* Reach: 80 | Impact: 2.5 | Confidence: 0.9 | Effort: 2 (2 SP)
  - *RICE Score:* 90.0
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* To Do
- [**TSK-13**](https://gemini.google.com/app/tasks/TSK-13.md)**: RichConsolePresenter TUI Rendering Engine**
  - *Epic/Requirement Link:* NFR05 - Accessibility & UI Design System
  - *Metrics:* Reach: 80 | Impact: 2.5 | Confidence: 0.8 | Effort: 2 (2 SP)
  - *RICE Score:* 80.0
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* To Do

### **🛡️ Backlog Phase 5: Diagnostics, Observability & Hardening**

- [**TSK-14**](https://gemini.google.com/app/tasks/TSK-14.md)**: Standard Error Structured JSON Logging & Diagnostics**
  - *Epic/Requirement Link:* NFR02 - Structured Telemetry
  - *Metrics:* Reach: 90 | Impact: 2.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - *RICE Score:* 81.0
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* To Do
- [**TSK-15**](https://gemini.google.com/app/tasks/TSK-15.md)**: Self-Healing JSON Schema Validator & Backup Recovery**
  - *Epic/Requirement Link:* Rule 15.2 - Auto-Healing
  - *Metrics:* Reach: 100 | Impact: 3.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - *RICE Score:* 135.0
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* To Do
- [**TSK-16**](https://gemini.google.com/app/tasks/TSK-16.md)**: LGPD-Compliant "purge-all" Safe Data Scrubber**
  - *Epic/Requirement Link:* NFR03 - Data Lifecycle Compliance
  - *Metrics:* Reach: 100 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - *RICE Score:* 300.0 (High Priority Compliance)
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* To Do

### **📦 Backlog Phase 6: Packaging & CI/CD Release**

- [**TSK-17**](https://gemini.google.com/app/tasks/TSK-17.md)**: PyProject Configuration & PyInstaller Standalone Compilation**
  - *Epic/Requirement Link:* Distribution Strategy / Air-gapped Execution
  - *Metrics:* Reach: 70 | Impact: 3.0 | Confidence: 0.8 | Effort: 2 (2 SP)
  - *RICE Score:* 84.0
  - *TDD Test File:* `tests/test_infra.py`
  - *Status:* To Do

## **3. 📋 Basic Markdown Kanban Board**

### **🔴 To Do (Ready for Development)**

- [ ] [**TSK-03**](https://gemini.google.com/app/tasks/TSK-03.md)**:** Candidate Domain Entity & Properties (Est. 1 SP)
- [ ] [**TSK-04**](https://gemini.google.com/app/tasks/TSK-04.md)**:** Candidate Status State Machine Transition Rules (Est. 1 SP)
- [ ] [**TSK-05**](https://gemini.google.com/app/tasks/TSK-05.md)**:** Vacancy Domain Entity with Lazy-Evaluated TTL & Capacity (Est. 2 SP)
- [ ] [**TSK-06**](https://gemini.google.com/app/tasks/TSK-06.md)**:** Queue Aggregate & Inbound Sequence Rules (Est. 2 SP)
- [ ] [**TSK-07**](https://gemini.google.com/app/tasks/TSK-07.md)**:** Port Abstractions (Inbound & Outbound Interfaces) (Est. 1 SP)
- [ ] [**TSK-08**](https://gemini.google.com/app/tasks/TSK-08.md)**:** QueueManager Application Service Execution Logic (Est. 2 SP)
- [ ] [**TSK-09**](https://gemini.google.com/app/tasks/TSK-09.md)**:** MatchEngine Multi-Filter Matching Algorithm (Est. 3 SP)
- [ ] [**TSK-10**](https://gemini.google.com/app/tasks/TSK-10.md)**:** Thread-Safe Atomic JSON Persistence Engine (Est. 3 SP)
- [ ] [**TSK-11**](https://gemini.google.com/app/tasks/TSK-11.md)**:** SystemClock Adapter Implementation (Est. 1 SP)
- [ ] [**TSK-12**](https://gemini.google.com/app/tasks/TSK-12.md)**:** Argparse Command Router & Controller Adapter (Est. 2 SP)
- [ ] [**TSK-13**](https://gemini.google.com/app/tasks/TSK-13.md)**:** RichConsolePresenter TUI Rendering Engine (Est. 2 SP)
- [ ] [**TSK-14**](https://gemini.google.com/app/tasks/TSK-14.md)**:** Standard Error Structured JSON Logging & Diagnostics (Est. 2 SP)
- [ ] [**TSK-15**](https://gemini.google.com/app/tasks/TSK-15.md)**:** Self-Healing JSON Schema Validator & Backup Recovery (Est. 2 SP)
- [ ] [**TSK-16**](https://gemini.google.com/app/tasks/TSK-16.md)**:** LGPD-Compliant "purge-all" Safe Data Scrubber (Est. 1 SP)
- [ ] [**TSK-17**](https://gemini.google.com/app/tasks/TSK-17.md)**:** PyProject Configuration & PyInstaller Standalone Compilation (Est. 2 SP)

### **🟡 In Progress (Actively Being Built)**

*None. Waiting for Sprint kickoff.*

### **🔵 In Review (QA & Test Verification)**

*None.*

### **🟢 Done (Merged & Verified in Main Trunk)**

- [x] [**TSK-01**](https://gemini.google.com/app/tasks/TSK-01.md)**:** Configuration Validation & Directory Setup (1 SP)
- [x] [**TSK-02**](https://gemini.google.com/app/tasks/TSK-02.md)**:** Custom Domain Exceptions & Error Mapping (1 SP)

*Signed by:* Kalyel N. Laurindo / Project Owner