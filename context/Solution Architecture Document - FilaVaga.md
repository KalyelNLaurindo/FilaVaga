# **📋 Solution Architecture & Product Vision: FilaVaga — Automated Queue-Native Vacancy Matching**

**Role:** Product Owner / Solution Architect

**Objective:** Define the strategic, commercial, and technical blueprint for resolving the core problem space mapped during discovery.

**Context:** FilaVaga — A highly optimized, local in-memory queue management engine with dynamic temporal logic designed to eliminate SINE's manual candidate waitlist sorting through structured queue semantics and immediate execution CLI interfaces.

## **🏛️ Project Metadata**

- **Client / Segment:** Public Employment Center (SINE) — Local Branch Operations Tooling
- **Date of Creation:** June 15, 2026
- **Lead Product Owner:** Kalyel N. Laurindo / Project Owner
- **Document Version:** v1.0

## **🚀 1. The Market Opportunity & Strategic Positioning**

### **1.1. Market Size & Opportunity Map (TAM / SAM / SOM)**

- **Field 1.1.1 - Total Addressable Market (TAM):** $\approx 50,000$ public employment centers and local social support offices in emerging markets (particularly Latin America and Sub-Saharan Africa) that manage job-seeker matching with restricted, offline, or legacy local workstation environments.
- **Field 1.1.2 - Serviceable Addressable Market (SAM):** All $1,200$ physical SINE (Sistema Nacional de Emprego) branches in Brazil operating local worker screening workflows.
- **Field 1.1.3 - Serviceable Obtainable Market (SOM):** $150$ municipal/state-level SINE branches in regional clusters experiencing high industrial seasonal hiring peaks where manual spreadsheet limits are severely bottlenecked.

### **1.2. Competitive Landscape & Product Moat**

- **Competitor 1 (Shared Legacy Database / National Portals):** "Mais Emprego" national software.
  - *The Gap / Friction Point:* Extreme high latency, rigid workflows, lack of dynamic, local, desk-level queue awareness. It lacks any operational FIFO visual queues for walk-in counselor optimization.
  - *Our Advantage:* Ultra-lightweight local CLI operating with sub-millisecond in-memory response times, tailored exactly to desk-level operational realities.
- **Competitor 2 (Spreadsheet Workarounds):** Local Shared Excel (`.xlsx`) files.
  - *The Gap / Friction Point:* Highly prone to sorting corruptions, single-write locking limits, no status transitions, zero native temporal alerting or automated expiration checks.
  - *Our Advantage:* Data structures natively enforce FIFO sequence via high-precision timestamps, dynamic TTL vacancy checks, and zero manual sort operations.

## **💰 2. Monetization Strategy, Licensing & Distribution Model**

- **Field 2.1 - Licensing Model:** Permissive Open-Source (MIT) to allow seamless institutional compliance, transparency for public audits, and frictionless developer adaptation.
- **Field 2.2 - Pricing / Business Model:** Free & Open Source (FOSS) / No Monetization (designed as an impact-oriented open source system).
- **Field 2.2.1 - Paid Tier Value Proposition (If Applicable):** N/A - Fully Free/Open Source.
- **Field 2.3 - Distribution Strategy:** Package Manager (`pip` distribution for python-based system integration) / Local Standalone Binary executable (packaged with `PyInstaller` for zero-dependency Windows workstation execution).
- **Field 2.4 - Organic Acquisition & Growth Strategy:** Distribution through GitHub repositories, targeting public IT civil servant communities and state labor department engineers looking for immediate solutions to local workstation bottlenecks.

## **🛠️ 3. Technical Viability & High-Level Architectural Vision**

### **✍️ Technical Challenges Form Entry**

#### **Technical Challenge 3.1: Thread-Safe In-Memory Queue State**

- **Friction Level:** High
- **Architectural Solution:** Utilization of Python's thread-safe collections (`collections.deque` paired with `threading.Lock` primitives) to ensure that multiple operations (such as asynchronous time-of-day updates and manual CLI queries) never trigger memory-level race conditions.

#### **Technical Challenge 3.2: Lazy Evaluation of Vacancy TTL Expirations**

- **Friction Level:** Medium
- **Architectural Solution:** To avoid heavy polling loops in resource-constrained SINE workstations, the system implements a "Lazy Evaluator" design pattern. Vacancy expiration (TTL) checks are run at read/query time whenever a matching candidate is requested, invalidating expired vacancies dynamically.

#### **Technical Challenge 3.3: High-Performance Attribute Indexing**

- **Friction Level:** Medium
- **Architectural Solution:** Flat $O(N)$ linear scans of candidates are eliminated. FilaVaga implements a secondary indexing structure (using Python `dict` mappings) pointing to categorized queues (e.g., partitioned by profession code and availability status), ensuring candidate matching operates at $O(1)$ lookup complexity.

### **3.1. Core Architectural Premises**

- **Decoupling Content/Configuration from Code:** System behaviors, category lists, maximum wait times, and CLI default profiles are loaded from a localized JSON file (`config.json`), permitting behavioral customization without script re-compilation.
- **Human-in-the-Loop (HITL) Validation:** The system generates priority match recommendations; the counselor explicitly inputs structural actions (e.g., `accept`, `decline`, `no-answer`) to transition candidate state, ensuring actual human counseling agency guides the platform.
- **Offline-Resilience / Caching Policy:** FilaVaga is 100% offline-first. Session memory is designed to be highly secure and transient, preserving absolute execution integrity without remote database connectivity.
- **Privacy-First Data Protection:** Candidate names are stored alongside localized obfuscated IDs. High-risk personal identifiers (like Brazilian CPF or physical addresses) are excluded from the runtime memory footprint by design.

### **✍️ Technology & Data Governance Spec**

- **Field 3.4.1 - Core Communication Style:** Local Direct Execution (Python Command Line Interface).
- **Field 3.4.2 - Data Serialization Format:** JSON (used exclusively for local system configuration templates and optional session snapshots).
- **Field 3.5.1 - Database Paradigm:** Flat Files (JSON) & In-Memory Memory Structures (no heavyweight database server dependency).
- **Field 3.5.2 - Primary Source of Truth:** Volatile In-Memory Queue structure, with serialized system snapshots recorded on demand to local user-directory workspace files.

## **📑 4. Requirements Engineering & Feature Specification**

### **🎭 4.1. Scenario-Based Requirements Engineering (SBRE)**

#### **Scenario A: Candidate Queue Admission**

- **Trigger Event:** A candidate arrives at the desk and is registered by the counselor using `filavaga register`.
- **System Action:** The system captures profile variables, timestamps the entry with high-precision ISO-8601 UTC metadata, automatically resolves their index position, and appends them to the end of the matching FIFO sub-queue.

#### **Scenario B: Instant Vacancy Match Matching**

- **Trigger Event:** A new vacancy is entered into the system. The counselor runs `filavaga match --vacancy <VACANCY_ID>`.
- **System Action:** The system validates the vacancy's TTL, fetches the indexed FIFO category queue, screens for active candidate statuses, and returns the single highest-priority eligible match within milliseconds.

#### **Scenario C: Transient Session Export/Recovery**

- **Trigger Event:** SINE branch workstation undergoes a forced operating system reboot.
- **System Action:** On startup, the CLI automatically searches for a local, validated JSON state file (`state_snapshot.json`) to recover the exact pre-crash state, maintaining queue continuity.

### **🎯 4.2. MoSCoW Prioritization Framework**

#### **🔴 Must Have (Critical for Core Value Proposition & MVP Launch)**

- **Requirement RF01: High-Precision FIFO Queue Engine** * *Description:* An in-memory queue manager enforcing chronological sequence based on register timestamps.
  - *JTBD Tracing:* [Section 10.1 - Functional Job: Instant retrieval of ordered eligible lists]
- **Requirement RF02: Temporal Vacancy TTL Manager** * *Description:* Operational checking logic assessing vacancy expiration windows at the moment of match execution.
  - *JTBD Tracing:* [Section 10.3 - Social Job: Ensuring no valid vacancy expires unaddressed]
- **Requirement RF03: Multi-Attribute Candidate Matcher** * *Description:* Filter mechanism querying candidate profile fields (e.g., sector zone, educational level) without breaking queue prioritization.
  - *JTBD Tracing:* [Section 10.1 - Functional Job: Skip manual scan cycles]

#### **🟡 Should Have (High Value, Target for Immediate Post-MVP Release)**

- **Requirement RF04: Auto-Save Snapshot Manager** * *Description:* Automatic background export of in-memory data states to a local JSON payload on every state-changing operation.
  - *JTBD Tracing:* [Section 9.2 - Mitigation of State Corruption Risks]

#### **🟢 Could Have (Desirable, Nice-to-Have, Low Urgency)**

- **Requirement RF05: Standardized Audit Log Export** * *Description:* Compiles an exportable text trace logging exactly when, why, and by whom a candidate was contacted, skipped, or placed.
  - *JTBD Tracing:* [Section 4.3 - Audit & Compliance Regulatory Risks]

## **⚙️ 5. Non-Functional Requirements (NFRs)**

- **NFR01 (Security - Access Control):** The application is scoped as a local CLI tool; system access is governed entirely by standard operating system user profile permissions. No application-level login/password management database is implemented to guarantee zero footprint.
- **NFR02 (Security - Structured Telemetry):** Every execution outputting errors must write to `stderr` using structured JSON logs incorporating UTC Timestamps and UUIDv4 Trace IDs for local system audit compatibility.
- **NFR03 (Compliance - Data Lifecycle):** Adheres to LGPD principles by ensuring personal identifiable information (PII) is kept strictly local on the local machine and easily scrubbed through standard terminal purge commands (`filavaga purge-all`).
- **NFR04 (Availability & SLA):** Immediate application responsiveness. Matches for datasets up to $10,000$ active candidates must render in $<5\text{ms}$ on a basic dual-core legacy SINE CPU.
- **NFR05 (Accessibility):** Fully compatible with standardized terminal screen readers (e.g., NVDA, JAWS) via standard text streams (`stdout` / `stderr`).
- **Field 5.6 - Target Deployment Architecture:** Local Standalone Binary.

## **📦 6. MVP Scope Boundary (Defining the Line in the Sand)**

### **6.1. Product Focus Area (MVP Scope)**

- **Target Segments:** Internal SINE Branch Counselors handling high-volume operational desks.
- **Key Flows Included:** Candidate FIFO registration, Vacancy profile mapping & matching, Candidate status state machine tracking (`PENDING`, `CONTACTED`, `PLACED`, `REJECTED`).

### **6.1.1. FinOps & Operational Constraints**

- **Field 6.3 - Projected Monthly Infrastructure Cost (MVP):** $0.00 (Purely local client-side execution; requires zero cloud databases, cloud runtimes, or SaaS API subscriptions).

### **6.2. Explicitly OUT of Scope (Post-MVP Backlog)**

- ❌ **Out-of-Scope Feature 1:** Cloud-hosted central relational databases (PostgreSQL/SQL Server orchestration).
- ❌ **Out-of-Scope Feature 2:** Automated telephone dialers, WhatsApp API gateway routing, or dynamic SMS messaging integrations.
- ❌ **Out-of-Scope Feature 3:** Web-based UI dashboards or graphical client interfaces.

## **🎯 7. Validation Strategy & Success Metrics**

### **7.1. North Star Metric**

- **Field 7.1.1 - North Star Metric Statement:** **Search & Match Processing Time.** Reduction of the manual waitlist processing loop from an average of $15$ minutes down to $<5$ milliseconds per vacancy placement attempt.

### **7.2. Launch Gates & KPIs**

- **Field 7.2.1 - Commercial/Operational Target:** Successfully match and resolve at least $200$ job placements across pilot branches without a single manual Excel sort collision.
- **Field 7.2.2 - Activation Rate:** $100\%$ of desk counselors at pilot locations transitioning completely from shared spreadsheets to the CLI interface within the first week of installation.
- **Field 7.2.3 - User Feedback Loop:** Zero skipped-in-priority errors reported by supervisors during weekly audit verification rounds.

## **🎨 8. System Architecture Visualization**

- **Field 8.0 - Diagram Strategy:** Local Utility CLI

### **8.1. Level 1 System Context Diagram (Mermaid)**

```
flowchart TD
    Counselor["🌍 SINE Employment Counselor"]
    Supervisor["🛡️ Branch Supervisor"]

    subgraph Local_Workstation ["💻 SINE Local Desktop Runtime"]
        FilaVagaCLI["🚀 FilaVaga CLI Engine\n(Python Executable)"]
        LocalState["📂 Local State Storage\n(state_snapshot.json)"]
    end

    %% Counselor/Supervisor UI interactions
    Counselor -->|Executes matching & registration| FilaVagaCLI
    Supervisor -->|Configures rules & exports audits| FilaVagaCLI
    
    %% Storage operations
    FilaVagaCLI <-->|Reads/Writes transient snapshot| LocalState

    %% Styling
    style FilaVagaCLI fill:#2c3e50,stroke:#34495e,stroke-width:4px,color:#fff
    style Local_Workstation fill:#ecf0f1,stroke:#bdc3c7,stroke-dasharray: 5 5
    style Counselor fill:#3498db,stroke:#2980b9,color:#fff
    style Supervisor fill:#16a085,stroke:#27ae60,color:#fff
    style LocalState fill:#f39c12,stroke:#d35400,color:#fff
```

### **8.2. Level 2 Container Diagram (Mermaid)**

```
graph TD
    User((Desk Counselor))

    subgraph CLI_Interface ["💻 Command Line Wrapper"]
        Parser[Argument Parser\n- argparse / Click -]
        Presenter[Output Formatter\n- stdout Rich Table -]
    end

    subgraph Memory_Engine ["⚙️ Core In-Memory Engine"]
        QueueMgr[Queue Manager\n- FIFO Logic -]
        MatchingEngine[Match Engine\n- Attribute Filtering -]
        TTLWatcher[Temporal Evaluator\n- Lazy TTL Check -]
    end

    subgraph Persistence_IO ["📂 I/O Boundary"]
        Serializer[JSON State Serializer]
        DiskStore[(Local Disk Storage\n- JSON Snapshots -)]
    end

    %% Execution flow
    User -->|Enters CLI command| Parser
    Parser --> MatchingEngine
    MatchingEngine --> QueueMgr
    MatchingEngine --> TTLWatcher
    
    %% Persistence mapping
    QueueMgr <--> Serializer
    Serializer <--> DiskStore
    
    %% Presentation flow
    MatchingEngine --> Presenter
    Presenter -->|Renders formatted text| User

    %% Styling
    style CLI_Interface fill:#d5dbdb,stroke:#95a5a6
    style Memory_Engine fill:#ebf5fb,stroke:#2980b9,stroke-width:2px
    style Persistence_IO fill:#fef9e7,stroke:#f39c12
    style Parser fill:#3498db,color:#fff
    style QueueMgr fill:#2980b9,color:#fff
    style MatchingEngine fill:#2980b9,color:#fff
    style DiskStore fill:#e67e22,color:#fff
```

## **⚠️ 9. Engineering Risks & Architecture Assumptions**

### **✍️ Engineering Risks & Assumptions Form Entry**

#### **Engineering Risk 9.1: Sudden OS Power Termination / Session Data Loss**

- **Severity Level:** High
- **Mitigation Strategy:** Implement state-changing event-driven writes. Immediately serialize memory state to `state_snapshot.json` on any state-changing operations (such as registration or placement confirmation) instead of waiting for application exit.

#### **Engineering Risk 9.2: Workspace System Clock Skewing**

- **Severity Level:** Medium
- **Mitigation Strategy:** Log warning structures if local system time differs drastically from the last known serialized snapshot timestamp.

#### **Engineering Risk 9.3: Directory Writing Permission Lockouts**

- **Severity Level:** Low
- **Mitigation Strategy:** Implement error fallbacks in user profile-specific paths (e.g., `%APPDATA%` on Windows or `~/.config` on Linux) to bypass admin-level path write restrictions.
- **Architecture Assumption 1:** Run-time workstation environment supports Python 3.10+ execution.
- **Architecture Assumption 2:** SINE desks have access to locally readable/writable paths under standard, non-privileged operating system user profiles.

### **Lead Product Owner Approval & Sign-Off**

**Signed by:** Kalyel N. Laurindo / Project Owner

**Date:** June 15, 2026

**Status:** Approved for Core Development Phase