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

- [**TSK-01**](backlog/TSK-01.md): Configuration Validation & Directory Setup

  $$ARCH-ENABLER$$
  - _Epic/Requirement Link:_ NFR03 / ADR-001 (Local directory pathing & environment validation)
  - _Metrics:_ Reach: 80 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 240.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done (Pre-bootstrapped workspace)

- [**TSK-02**](backlog/TSK-02.md): Custom Domain Exceptions & Error Mapping

  $$ARCH-ENABLER$$
  - _Epic/Requirement Link:_ Architecture Hardening / System resilience
  - _Metrics:_ Reach: 90 | Impact: 2.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 180.0
  - _TDD Test File:_ `tests/test_domain.py`
  - _Status:_ Done

### **⚙️ Backlog Phase 2: Bounded Domain Context & Core Models**

- [**TSK-03**](backlog/TSK-03.md)**: Candidate Domain Entity & Properties**
  - _Epic/Requirement Link:_ RF01 - FIFO Engine
  - _Metrics:_ Reach: 90 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 270.0
  - _TDD Test File:_ `tests/test_domain.py`
  - _Status:_ Done
- [**TSK-04**](backlog/TSK-04.md)**: Candidate Status State Machine Transition Rules**
  - _Epic/Requirement Link:_ RF01 - State transition rules (`PENDING` ➔ `CONTACTED` ➔ `PLACED` / `REJECTED`)
  - _Metrics:_ Reach: 85 | Impact: 3.0 | Confidence: 0.9 | Effort: 1 (1 SP)
  - _RICE Score:_ 229.5
  - _TDD Test File:_ `tests/test_domain.py`
  - _Status:_ Done
- [**TSK-05**](backlog/TSK-05.md)**: Vacancy Domain Entity with Lazy-Evaluated TTL & Capacity**
  - _Epic/Requirement Link:_ RF02 - Lazy TTL
  - _Metrics:_ Reach: 85 | Impact: 3.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 114.7
  - _TDD Test File:_ `tests/test_domain.py`
  - _Status:_ Done
- [**TSK-06**](backlog/TSK-06.md)**: Queue Aggregate & Inbound Sequence Rules**
  - _Epic/Requirement Link:_ RF01 - FIFO Chronology
  - _Metrics:_ Reach: 90 | Impact: 3.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 121.5
  - _TDD Test File:_ `tests/test_domain.py`
  - _Status:_ Done

### **🧠 Backlog Phase 3: Test-Driven Core Logic (Use Cases)**

- [**TSK-07**](backlog/TSK-07.md)**: Port Abstractions (Inbound & Outbound Interfaces)**
  - _Epic/Requirement Link:_ Clean Architecture Core Isolation
  - _Metrics:_ Reach: 95 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 285.0
  - _TDD Test File:_ `tests/test_usecases.py`
  - _Status:_ Done
- [**TSK-08**](backlog/TSK-08.md)**: QueueManager Application Service Execution Logic**
  - _Epic/Requirement Link:_ RF01 - Candidate registration & state management
  - _Metrics:_ Reach: 95 | Impact: 3.0 | Confidence: 0.8 | Effort: 2 (2 SP)
  - _RICE Score:_ 114.0
  - _TDD Test File:_ `tests/test_usecases.py`
  - _Status:_ Done
- [**TSK-09**](backlog/TSK-09.md)**: MatchEngine Multi-Filter Matching Algorithm**
  - _Epic/Requirement Link:_ RF03 - Multi-Filter & RF02 - Lazy Evaluation
  - _Metrics:_ Reach: 95 | Impact: 3.0 | Confidence: 0.8 | Effort: 3 (3 SP)
  - _RICE Score:_ 76.0
  - _TDD Test File:_ `tests/test_usecases.py`
  - _Status:_ Done

### **🔌 Backlog Phase 4: Interface Adapters & Persistence Adapters**

- [**TSK-10**](backlog/TSK-10.md)**: Thread-Safe Atomic JSON Persistence Engine**
  - _Epic/Requirement Link:_ RF04 - Atomic Save / ADR-002 Concurrency
  - _Metrics:_ Reach: 100 | Impact: 3.0 | Confidence: 0.9 | Effort: 3 (3 SP)
  - _RICE Score:_ 90.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done
- [**TSK-11**](backlog/TSK-11.md)**: SystemClock Adapter Implementation**
  - _Epic/Requirement Link:_ Port & Adapter Integration / Testability Isolation
  - _Metrics:_ Reach: 100 | Impact: 2.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 200.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done
- [**TSK-12**](backlog/TSK-12.md)**: Argparse Command Router & Controller Adapter**
  - _Epic/Requirement Link:_ User Interface / Console Commands Map
  - _Metrics:_ Reach: 80 | Impact: 2.5 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 90.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done
- [**TSK-13**](backlog/TSK-13.md)**: RichConsolePresenter TUI Rendering Engine**
  - _Epic/Requirement Link:_ NFR05 - Accessibility & UI Design System
  - _Metrics:_ Reach: 80 | Impact: 2.5 | Confidence: 0.8 | Effort: 2 (2 SP)
  - _RICE Score:_ 80.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do

### **🛡️ Backlog Phase 5: Diagnostics, Observability & Hardening**

- [**TSK-14**](backlog/TSK-14.md)**: Standard Error Structured JSON Logging & Diagnostics**
  - _Epic/Requirement Link:_ NFR02 - Structured Telemetry
  - _Metrics:_ Reach: 90 | Impact: 2.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 81.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do
- [**TSK-15**](backlog/TSK-15.md)**: Self-Healing JSON Schema Validator & Backup Recovery**
  - _Epic/Requirement Link:_ Rule 15.2 - Auto-Healing
  - _Metrics:_ Reach: 100 | Impact: 3.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 135.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do
- [**TSK-16**](backlog/TSK-16.md)**: LGPD-Compliant "purge-all" Safe Data Scrubber**
  - _Epic/Requirement Link:_ NFR03 - Data Lifecycle Compliance
  - _Metrics:_ Reach: 100 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 300.0 (High Priority Compliance)
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do

### **📦 Backlog Phase 6: Packaging & CI/CD Release**

- [**TSK-17**](backlog/TSK-17.md)**: PyProject Configuration & PyInstaller Standalone Compilation**
  - _Epic/Requirement Link:_ Distribution Strategy / Air-gapped Execution
  - _Metrics:_ Reach: 70 | Impact: 3.0 | Confidence: 0.8 | Effort: 2 (2 SP)
  - _RICE Score:_ 84.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do

## **3. 📋 Basic Markdown Kanban Board**

### **🔴 To Do (Ready for Development)**

- [ ] [**TSK-13**](backlog/TSK-13.md)**:** RichConsolePresenter TUI Rendering Engine (Est. 2 SP)
- [ ] [**TSK-14**](backlog/TSK-14.md)**:** Standard Error Structured JSON Logging & Diagnostics (Est. 2 SP)
- [ ] [**TSK-15**](backlog/TSK-15.md)**:** Self-Healing JSON Schema Validator & Backup Recovery (Est. 2 SP)
- [ ] [**TSK-16**](backlog/TSK-16.md)**:** LGPD-Compliant "purge-all" Safe Data Scrubber (Est. 1 SP)
- [ ] [**TSK-17**](backlog/TSK-17.md)**:** PyProject Configuration & PyInstaller Standalone Compilation (Est. 2 SP)

### **🟡 In Progress (Actively Being Built)**

_None. Waiting for Sprint kickoff._

### **🔵 In Review (QA & Test Verification)**

_None._

### **🟢 Done (Merged & Verified in Main Trunk)**

- [x] [**TSK-01**](backlog/TSK-01.md)**:** Configuration Validation & Directory Setup (1 SP)
- [x] [**TSK-02**](backlog/TSK-02.md)**:** Custom Domain Exceptions & Error Mapping (1 SP)
- [x] [**TSK-03**](backlog/TSK-03.md)**:** Candidate Domain Entity & Properties (1 SP)
- [x] [**TSK-04**](backlog/TSK-04.md)**:** Candidate Status State Machine Transition Rules (1 SP)
- [x] [**TSK-05**](backlog/TSK-05.md)**:** Vacancy Domain Entity with Lazy-Evaluated TTL & Capacity (2 SP)
- [x] [**TSK-06**](backlog/TSK-06.md)**:** Queue Aggregate & Inbound Sequence Rules (2 SP)
- [x] [**TSK-07**](backlog/TSK-07.md)**:** Port Abstractions (Inbound & Outbound Interfaces) (1 SP)
- [x] [**TSK-08**](backlog/TSK-08.md)**:** QueueManager Application Service Execution Logic (2 SP)
- [x] [**TSK-09**](backlog/TSK-09.md)**:** MatchEngine Multi-Filter Matching Algorithm (3 SP)
- [x] [**TSK-10**](backlog/TSK-10.md)**:** Thread-Safe Atomic JSON Persistence Engine (3 SP)
- [x] [**TSK-11**](backlog/TSK-11.md)**:** SystemClock Adapter Implementation (1 SP)
- [x] [**TSK-12**](backlog/TSK-12.md)**:** Argparse Command Router & Controller Adapter (2 SP)

_Signed by:_ Kalyel N. Laurindo / Project Owner
