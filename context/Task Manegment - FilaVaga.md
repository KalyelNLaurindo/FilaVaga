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
  - _Status:_ Done

### **🛡️ Backlog Phase 5: Diagnostics, Observability & Hardening**

- [**TSK-14**](backlog/TSK-14.md)**: Standard Error Structured JSON Logging & Diagnostics**
  - _Epic/Requirement Link:_ NFR02 - Structured Telemetry
  - _Metrics:_ Reach: 90 | Impact: 2.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 81.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done
- [**TSK-15**](backlog/TSK-15.md)**: Self-Healing JSON Schema Validator & Backup Recovery**
  - _Epic/Requirement Link:_ Rule 15.2 - Auto-Healing
  - _Metrics:_ Reach: 100 | Impact: 3.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 135.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done
- [**TSK-16**](backlog/TSK-16.md)**: LGPD-Compliant "purge-all" Safe Data Scrubber**
  - _Epic/Requirement Link:_ NFR03 - Data Lifecycle Compliance
  - _Metrics:_ Reach: 100 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 300.0 (High Priority Compliance)
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done

- [**TSK-26**](backlog/TSK-26.md)**: File-System Access Permission Hardening**
  - _Epic/Requirement Link:_ NFR03 / SECURITY
  - _Metrics:_ Reach: 90 | Impact: 2.5 | Confidence: 0.9 | Effort: 1 (1 SP)
  - _RICE Score:_ 202.5
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done

### **🔒 Backlog Phase 5.1: Security Hardening & Encapsulation**

- [**TSK-27**](backlog/TSK-27.md)**: Repository Reference Leak & Mutability Protection**
  - _Epic/Requirement Link:_ NFR04 / Data Integrity / State Consistency
  - _Metrics:_ Reach: 100 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 300.0 (High Priority Compliance)
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done

- [**TSK-32**](backlog/TSK-32.md)**: Implement Unit of Work (UoW) Pattern for Multi-Repository Atomic Transactions**
  - _Epic/Requirement Link:_ NFR04 / DATA INTEGRITY
  - _Metrics:_ Reach: 100 | Impact: 3.0 | Confidence: 1.0 | Effort: 2 (2 SP)
  - _RICE Score:_ 150.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done

- [**TSK-33**](backlog/TSK-33.md)**: Refactor Queue Aggregate for DDD Orthodox Self-Sufficiency**
  - _Epic/Requirement Link:_ RF01 / Domain Modeling
  - _Metrics:_ Reach: 95 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 285.0
  - _TDD Test File:_ `tests/test_domain.py`
  - _Status:_ Done

### **🌐 Backlog Phase 5.2: Internationalization (i18n) & Localized UI**

- [**TSK-28**](backlog/TSK-28.md)**: i18n Translation Engine & Language Configuration Loader**
  - _Epic/Requirement Link:_ NFR05 / ACCESSIBILITY & DX
  - _Metrics:_ Reach: 90 | Impact: 2.0 | Confidence: 0.8 | Effort: 2 (2 SP)
  - _RICE Score:_ 72.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do

- [**TSK-29**](backlog/TSK-29.md)**: UI RichConsolePresenter Key-based Translation Mapping**
  - _Epic/Requirement Link:_ NFR05 / ACCESSIBILITY & DX
  - _Metrics:_ Reach: 90 | Impact: 2.0 | Confidence: 0.8 | Effort: 2 (2 SP)
  - _RICE Score:_ 72.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do

### **🎨 Backlog Phase 5.3: Console Accessibility & Interactive UX**

- [**TSK-30**](backlog/TSK-30.md)**: Interactive Shortcuts & Layperson Menu Enhancements**
  - _Epic/Requirement Link:_ NFR05 / ACCESSIBILITY & UX
  - _Metrics:_ Reach: 95 | Impact: 2.5 | Confidence: 0.9 | Effort: 1 (1 SP)
  - _RICE Score:_ 213.75
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do

- [**TSK-31**](backlog/TSK-31.md)**: CLI Accessibility Suite (Support for --no-color and Screen-Reader Linearization)**
  - _Epic/Requirement Link:_ NFR05 / ACCESSIBILITY
  - _Metrics:_ Reach: 95 | Impact: 3.0 | Confidence: 1.0 | Effort: 1 (1 SP)
  - _RICE Score:_ 285.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do


### **📦 Backlog Phase 6: Packaging & CI/CD Release**

- [**TSK-17**](backlog/TSK-17.md)**: PyProject Configuration & PyInstaller Standalone Compilation**
  - _Epic/Requirement Link:_ Distribution Strategy / Air-gapped Execution
  - _Metrics:_ Reach: 70 | Impact: 3.0 | Confidence: 0.8 | Effort: 2 (2 SP)
  - _RICE Score:_ 84.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ Done

### **🔮 Backlog Phase 7: Future Roadmap & Analytical Enhancements**

- [**TSK-18**](backlog/TSK-18.md)**: CSV Data Import Adapter**
  - _Epic/Requirement Link:_ Future Enhancements / Legacy System Data Integration
  - _Metrics:_ Reach: 80 | Impact: 2.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 72.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do
- [**TSK-19**](backlog/TSK-19.md)**: Historical Archiving & Snapshot Optimization**
  - _Epic/Requirement Link:_ Future Enhancements / Database Performance Optimization & LGPD Compliance
  - _Metrics:_ Reach: 90 | Impact: 2.5 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 101.25
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do
- [**TSK-20**](backlog/TSK-20.md)**: Interactive Configuration Wizard**
  - _Epic/Requirement Link:_ Future Enhancements / UX Hardening
  - _Metrics:_ Reach: 75 | Impact: 2.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 67.5
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do
- [**TSK-21**](backlog/TSK-21.md)**: Anonymized Placement Analytics Export**
  - _Epic/Requirement Link:_ Future Enhancements / System Telemetry and Regional Reporting
  - _Metrics:_ Reach: 80 | Impact: 2.0 | Confidence: 0.8 | Effort: 2 (2 SP)
  - _RICE Score:_ 64.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do

### **🔗 Backlog Phase 8: Integração & Extensibilidade da Plataforma**

- [**TSK-22**](backlog/TSK-22.md)**: REST-like In-Process Event Bus**
  - _Epic/Requirement Link:_ Future / Extensibility & Adapter Decoupling
  - _Metrics:_ Reach: 90 | Impact: 3.0 | Confidence: 0.8 | Effort: 4 (4 SP)
  - _RICE Score:_ 54.0
  - _TDD Test File:_ `tests/test_usecases.py`
  - _Status:_ To Do
- [**TSK-23**](backlog/TSK-23.md)**: Vacancy Capacity Overflow Alerting**
  - _Epic/Requirement Link:_ Future / Alerts & Observability
  - _Metrics:_ Reach: 75 | Impact: 3.0 | Confidence: 0.9 | Effort: 1 (1 SP)
  - _RICE Score:_ 202.5
  - _TDD Test File:_ `tests/test_domain.py`
  - _Status:_ To Do
- [**TSK-24**](backlog/TSK-24.md)**: Candidate Profile Schema Validator**
  - _Epic/Requirement Link:_ Future / DX & Data Integrity
  - _Metrics:_ Reach: 90 | Impact: 2.0 | Confidence: 0.9 | Effort: 2 (2 SP)
  - _RICE Score:_ 81.0
  - _TDD Test File:_ `tests/test_domain.py`
  - _Status:_ To Do
- [**TSK-25**](backlog/TSK-25.md)**: Queue Snapshot Serializer & Replay**
  - _Epic/Requirement Link:_ Future / Resilience & Disaster Recovery
  - _Metrics:_ Reach: 80 | Impact: 3.0 | Confidence: 0.8 | Effort: 4 (4 SP)
  - _RICE Score:_ 48.0
  - _TDD Test File:_ `tests/test_infra.py`
  - _Status:_ To Do

## **3. 📋 Basic Markdown Kanban Board**

### **🔴 To Do (Ready for Development)**

- [ ] [**TSK-18**](backlog/TSK-18.md)**:** CSV Data Import Adapter (2 SP)
- [ ] [**TSK-19**](backlog/TSK-19.md)**:** Historical Archiving & Snapshot Optimization (2 SP)
- [ ] [**TSK-20**](backlog/TSK-20.md)**:** Interactive Configuration Wizard (2 SP)
- [ ] [**TSK-21**](backlog/TSK-21.md)**:** Anonymized Placement Analytics Export (2 SP)
- [ ] [**TSK-28**](backlog/TSK-28.md)**:** i18n Translation Engine & Language Configuration Loader (2 SP)
- [ ] [**TSK-29**](backlog/TSK-29.md)**:** UI RichConsolePresenter Key-based Translation Mapping (2 SP)
- [ ] [**TSK-30**](backlog/TSK-30.md)**:** Interactive Shortcuts & Layperson Menu Enhancements (1 SP)
- [ ] [**TSK-31**](backlog/TSK-31.md)**:** CLI Accessibility Suite (Support for --no-color and Screen-Reader Linearization) (1 SP)


**Phase 8 — Integração & Extensibilidade da Plataforma**
- [ ] [**TSK-22**](backlog/TSK-22.md)**:** REST-like In-Process Event Bus (4 SP)
- [ ] [**TSK-23**](backlog/TSK-23.md)**:** Vacancy Capacity Overflow Alerting (1 SP)
- [ ] [**TSK-24**](backlog/TSK-24.md)**:** Candidate Profile Schema Validator (2 SP)
- [ ] [**TSK-25**](backlog/TSK-25.md)**:** Queue Snapshot Serializer & Replay (4 SP)
- [ ] [**TSK-34**](backlog/TSK-34.md)**:** HTTP REST API Backend Server Integration (3 SP)
- [ ] [**TSK-35**](backlog/TSK-35.md)**:** Terminal UI/UX Overhaul — Interactive Shell Visual Redesign (3 SP)



### **🟡 In Progress (Actively Being Built)**

_None._

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
- [x] [**TSK-13**](backlog/TSK-13.md)**:** RichConsolePresenter TUI Rendering Engine (2 SP)
- [x] [**TSK-14**](backlog/TSK-14.md)**:** Standard Error Structured JSON Logging & Diagnostics (2 SP)
- [x] [**TSK-15**](backlog/TSK-15.md)**:** Self-Healing JSON Schema Validator & Backup Recovery (2 SP)
- [x] [**TSK-16**](backlog/TSK-16.md)**:** LGPD-Compliant "purge-all" Safe Data Scrubber (1 SP)
- [x] [**TSK-17**](backlog/TSK-17.md)**:** PyProject Configuration & PyInstaller Standalone Compilation (2 SP)
- [x] [**TSK-26**](backlog/TSK-26.md)**:** File-System Access Permission Hardening (1 SP)
- [x] [**TSK-27**](backlog/TSK-27.md)**:** Repository Reference Leak & Mutability Protection (1 SP)
- [x] [**TSK-32**](backlog/TSK-32.md)**:** Implement Unit of Work (UoW) Pattern for Multi-Repository Atomic Transactions (2 SP)
- [x] [**TSK-33**](backlog/TSK-33.md)**:** Refactor Queue Aggregate for DDD Orthodox Self-Sufficiency (1 SP)

_Signed by:_ Kalyel N. Laurindo / Project Owner
