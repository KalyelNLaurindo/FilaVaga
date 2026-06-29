# 📋 **FilaVaga — Eliminating Vacancy Queue Management Friction & Placement Latency**

### **High-Performance In-Memory Local CLI Vacancy Matching Engine with Dynamic Temporal Logic**

[![Stack Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-8A2BE2?style=for-the-badge)](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero_External-success?style=for-the-badge)](https://docs.python.org/3/)
[![Testing Paradigm](https://img.shields.io/badge/Testing-TDD_Red_Green_Refactor-green?style=for-the-badge)](https://docs.pytest.org/)
[![Compliance](https://img.shields.io/badge/LGPD-Compliant-blueviolet?style=for-the-badge)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)

---

## **🏛️ Repository Metadata & Context**

| Property               | Description                                                                                 |
| :--------------------- | :------------------------------------------------------------------------------------------ |
| **Role**               | Core Repository Architecture / Project Lead                                                 |
| **Target Segment**     | Public Employment Center Counselors (SINE — Sistema Nacional de Emprego)                    |
| **Architecture Style** | Hexagonal Architecture (Ports & Adapters)                                                   |
| **Execution Engine**   | In-Memory thread-safe queues (`collections.deque`) with atomic flat-file JSON serialization |
| **Date of Creation**   | June 15, 2026                                                                               |
| **Current Version**    | v1.2.0                                                                                      |

---

## **🚀 1. The Product Vision & Core Problem**

### **1.1. The Macro Pain Space**

Traditional public employment centers (such as SINE in Brazil) typically rely on centralized, high-latency legacy systems or informal local workarounds — like shared Excel sheets or paper registers — to manage candidate waitlists and job openings.

In these operational setups, counselors manually search through flat tables to match incoming vacancies with job-seekers. Because these lists lack temporal awareness, automatic sorting, and state synchronization:

*   **FIFO Priority is routinely violated**, skipping qualified candidates who registered early.
*   **Vacancies expire unfilled** because expiration windows (TTL) are not proactively tracked.
*   **Counselor efficiency drops by 40–60%** due to time wasted navigating spreadsheet conflicts and manual status lookups.
*   **Data corruption** occurs frequently from concurrent spreadsheet writes.

### **1.2. The Core Solution Paradigm Shift**

**FilaVaga** solves this operational bottleneck by introducing a lightweight, queue-native command-line application that runs locally on restricted SINE workstations. It transitions operations from a passive database-query model to a high-speed, structured FIFO queue matching flow.

*   **Strategic Paradigm Shift:** FilaVaga replaces slow, error-prone manual Excel filters with an in-memory queue manager that instantly returns the highest-priority, eligible matching candidate for any given vacancy based on registration timestamps and CBO (Classificação Brasileira de Ocupações) codes.

---

#### **📌 REFERENCE: Queue Matching Flow Model**

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ 1. PASSIVE HAPPY-PATH MODEL (Traditional Excel Workflow)                   │
│                                                                           │
│ [Vacancy Arrives] ──► [Open Shared Excel?] ──► (Locked by colleague)      │
│                                │                                          │
│                                └─► [Save Delayed / FIFO Order Lost]       │
│                                                                           │
│ [Manual Search] ──► [Eligible Candidate?] ──► (Expired Slot / Out-of-     │
│                                                 Order Call / Unfilled)    │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 2. PROACTIVE QUEUE RESILIENCE MODEL (FilaVaga)                            │
│                                                                           │
│ [filavaga match --id <v_id>] ──► [Read CLI In-Memory Index]               │
│                                          │                                │
│                                          ▼                                │
│                              [Lazy TTL Expiration Check]                  │
│                                          │                                │
│                        ┌─────────────────┴──────────────────┐            │
│                    (Expired)                             (Valid)          │
│                        │                                     │            │
│                        ▼                                     ▼            │
│               [Mark Expired / Return Error]    [Fetch Top FIFO Candidate] │
│                                                             │             │
│                                                             ▼             │
│                                            [Auto Transition Candidate     │
│                                             Status: PENDING ► CONTACTED]  │
│                                                             │             │
│                                                             ▼             │
│                                            [Atomic Disk Write: os.replace]│
└───────────────────────────────────────────────────────────────────────────┘
```

To guarantee business integrity, FilaVaga implements the following operational SLA constraint: **Candidate matching queries for datasets containing up to 10,000 active candidates must render in less than 5 milliseconds on a basic dual-core workstation.**

---

## **🎮 2. CLI / Interface Usage Reference**

The command-line interface is optimized for high keyboard throughput. Use the following core execution commands:

| Command / Action                | Syntax                                                      | Description                                                                               | Example                                                                 |
| :------------------------------ | :---------------------------------------------------------- | :---------------------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| **Global Language Option**      | `--lang <lang>` or `-l <lang>`                              | Sets the active session language (supports: `pt`, `en`, `es`, `fr`, `de`).               | `filavaga --lang en dashboard`                                          |
| **Accessibility: Disable Color**| `--no-color`                                                | Disables all color/ANSI escape output sequences (also respects the `NO_COLOR` env var).   | `filavaga --no-color dashboard`                                         |
| **Accessibility: Linear Output**| `--linear` or `--accessible`                                | Renders console layouts in a linear stream for screen readers, avoiding complex grids.    | `filavaga --linear dashboard`                                           |
| **Register Candidate**          | `register --name "<name>" --cbo "<cbo>" --zone "<zone>"`    | Appends a new candidate to the tail of the matching FIFO sub-queue.                       | `filavaga register --name "Maria Silva" --cbo "4110-10" --zone "SUL"`   |
| **Interactive Match**           | `match --id "<vacancy_id>"`                                 | Validates vacancy TTL, pulls priority candidate, and starts interactive matching session. | `filavaga match --id "v_01h3nbfa4y1z8"`                                 |
| **Interactive Dashboard**       | `dashboard`                                                 | Launches the interactive TUI shell manager supporting single-character hotkey actions.    | `filavaga dashboard`                                                    |
| **Update Status Manually**      | `status-update --candidate "<id>" --to "<status>"`          | Transitions candidate state machine (`PENDING`, `CONTACTED`, `PLACED`, `REJECTED`).      | `filavaga status-update --candidate "c_01h3n" --to "PLACED"`            |
| **Import CSV Legacy Data**      | `import-csv --file "<path>"`                                | Batch-imports candidates from a CSV file into the active FIFO queues.                     | `filavaga import-csv --file "./legacy_candidates.csv"`                  |
| **Archive Placed Candidates**   | `archive`                                                   | Moves all `PLACED` and `REJECTED` candidates to an immutable historical archive snapshot. | `filavaga archive`                                                      |
| **Placement Analytics Export**  | `analyze --output "<path.json>"`                            | Exports anonymized placement rate statistics as a structured JSON report.                 | `filavaga analyze --output "./report_2026_q2.json"`                     |
| **Configuration Wizard**        | `configure`                                                 | Launches the interactive setup wizard to review and update `config.json` settings.        | `filavaga configure`                                                    |
| **Purge PII (LGPD Compliance)** | `purge-all`                                                 | Clears all personal identifiable information (PII) from local data directories.           | `filavaga purge-all`                                                    |

> [!TIP]
> **Dashboard Interactive Shortcuts:**
> * `[C]` / `[c]` — Interactively registers a new candidate.
> * `[M]` / `[m]` — Interactively matches a vacancy to the highest priority candidate.
> * `[L]` / `[l]` — Launches the dynamic language selection dialog (1: pt, 2: en, 3: es, 4: fr, 5: de).
> * `[Q]` / `[q]` — Exits the interactive TUI session.

> [!NOTE]
> **Data & Validation Rules:**
>
> - **CBO Codes:** Candidate and vacancy classifications must align with standard Brazilian CBO formats (e.g., `4110-10`).
> - **State Machines:** Candidate statuses can only transition along defined paths: `PENDING` ➔ `CONTACTED` ➔ `PLACED` or `REJECTED`. Direct transitions from `PENDING` to `PLACED` are prohibited.
> - **Write Atomicity:** Local data is saved by writing first to a `.tmp` file and then executing a platform-native rename to avoid state corruption during power failures.

#### **📌 REFERENCE: Candidate State Machine**

```text
┌─────────────────────────────────────────────────────────────┐
│ CANDIDATE STATUS STATE MACHINE                              │
│                                                             │
│          ┌─────────┐                                        │
│          │ PENDING │  ◄── Initial registration state        │
│          └────┬────┘                                        │
│               │  (match --id issued)                        │
│               ▼                                             │
│       ┌───────────┐                                         │
│       │ CONTACTED │  ◄── Counselor call initiated           │
│       └─────┬─────┘                                         │
│             │                                               │
│     ┌───────┴────────┐                                      │
│     ▼                ▼                                      │
│  ┌────────┐    ┌──────────┐                                 │
│  │ PLACED │    │ REJECTED │  ◄── Final terminal states      │
│  └────────┘    └──────────┘                                 │
│                                                             │
│  ✗ PENDING ──► PLACED (direct skip) is PROHIBITED          │
└─────────────────────────────────────────────────────────────┘
```

---

## **🛠️ 3. Technical Stack Overview**

FilaVaga relies on a streamlined, near-zero-dependency local footprint to bypass administrative execution restrictions on restricted SINE workstations.

| Architectural Layer        | Component / Technology                                       | Technical Rationale                                                                      |
| :------------------------- | :----------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
| **Client / Presenter**     | Python Native CLI (Argparse) + `rich>=12.0.0`                | Ensures 100% compatibility with terminal screen readers (NVDA/JAWS) and legacy consoles. |
| **i18n Translation Engine**| Custom Translation Service (`translation.py` + JSON locales) | Resolves active language using strict precedence rules with directory traversal safety.   |
| **Execution Engine**       | Python 3.10+ Standard Library                                | Eliminates runtime compilation issues. Uses standard collections (`collections.deque`).  |
| **Memory Management**      | Reentrant Thread Locks (`threading.RLock`)                   | Prevents in-memory race conditions during concurrent CLI session exports.                |
| **Database & Ledger**      | In-Memory Index Hashmaps (`dict`)                            | Achieves sub-millisecond query lookups (O(1)) without DBMS server dependencies.          |
| **Persistence Drive**      | Atomic JSON Serializer (`state_snapshot.json`)               | Protects data state by using double-buffer writes (temp files + atomic renames).         |
| **Analytics Engine**       | `analytics_service.py` — In-memory aggregation               | Calculates placement rates and CBO demand heatmaps from live queue snapshots.            |
| **Archive Module**         | `archive_service.py` — Snapshot compressor                   | Moves finalized candidate records to immutable historical archives (LGPD lifecycle).     |
| **CSV Importer**           | `csv_importer.py` — Batch ingestion adapter                  | Parses and validates legacy spreadsheet data, injecting records into FIFO queues.        |
| **Config Wizard**          | `config_wizard.py` — Interactive setup runtime               | Guided TUI flow to review and persist workspace settings in `config.json`.               |
| **Standalone Distribution**| PyInstaller (`filavaga.spec`)                                | Compiles the entire application into a single air-gapped executable for SINE stations.   |

---

## **🏗️ 4. Core Architectural Premises**

Specify the architectural rules, coding standards, and validation strategies.

*   **Premise 4.1 — Hexagonal Boundaries:** Business rules (`filavaga.core`) are completely isolated. They do not import from persistence, presentation layers, or OS-level standard modules. Cross-layer imports are rejected at code review.
*   **Premise 4.2 — Test-Driven Development (TDD):** A strict Red-Green-Refactor development cycle is enforced for all tasks. Invariants, state machine transitions, and edge-case paths are fully covered before implementation merges.
*   **Premise 4.3 — Privacy & Local Compliance:** In accordance with LGPD, no PII (Brazilian CPFs, full names in plain text, exact addresses) is stored in snapshot files. Obfuscated UUID keys are used as internal references throughout.
*   **Premise 4.4 — Lazy Evaluation of Deadlines:** Rather than running background daemon processes that consume CPU cycles on restricted hardware, vacancy deadlines (TTL) are validated lazily at query/evaluation time using the `SystemClock` adapter.

---

## **📂 5. Codebase Structure & Directory Standards**

```text
FilaVaga/
├── pyproject.toml              # Build specifications, dependencies & tool rules
├── config.json                 # JSON local workspace rules & business TTL limits
├── filavaga.spec               # PyInstaller standalone compilation manifest
├── logs/                       # Local directory for structured JSON logging exports
├── filavaga/                   # Core application root
│   ├── __init__.py
│   ├── main.py                 # CLI entry point bootstrap coordinator
│   │
│   ├── locales/                # JSON Translation locale resources (i18n)
│   │   ├── pt.json
│   │   ├── en.json
│   │   ├── es.json
│   │   ├── fr.json
│   │   └── de.json
│   │
│   ├── core/                   # Domain Core Layer (Pure Business Logic — No I/O)
│   │   ├── __init__.py
│   │   ├── entities.py         # Invariant Business Models (Candidate, Vacancy, Queue)
│   │   ├── value_objects.py    # Immutable Types (ProfessionCode, SectorZone, Timestamp)
│   │   └── exceptions.py       # Domain-specific validation exceptions
│   │
│   ├── application/            # Application Use Case Layer (Ports & Orchestrators)
│   │   ├── __init__.py
│   │   ├── ports/              # Port Abstractions (Boundary Interfaces)
│   │   │   ├── inbound.py      # Use case boundaries (IRegisterCandidate, IMatchVacancy)
│   │   │   └── outbound.py     # Port abstractions (IStateRepository, IClock)
│   │   └── services/           # Application Services (Orchestration & Business Flows)
│   │       ├── __init__.py
│   │       ├── queue_manager.py     # FIFO queue orchestration & candidate state manager
│   │       ├── match_engine.py      # Multi-filter FIFO candidate-to-vacancy matching
│   │       ├── analytics_service.py # Anonymized placement rate & CBO demand analytics
│   │       ├── archive_service.py   # Historical snapshot archiving (LGPD lifecycle)
│   │       ├── config_wizard.py     # Interactive TUI configuration wizard runtime
│   │       └── csv_importer.py      # Batch CSV ingestion adapter for legacy data
│   │
│   └── infra/                  # Infrastructure Adapter Layer (Concrete Drivers)
│       ├── __init__.py
│       ├── logger.py           # Structured JSON logging configurations
│       ├── translation.py      # i18n Translation Service engine
│       ├── cli/                # Terminal CLI UI Adapters (Argparse, Presenter)
│       │   ├── command_router.py    # Argparse command dispatcher & controller adapter
│       │   └── presenter.py         # Rich TUI rendering engine (tables, panels, grids)
│       └── persistence/        # Storage Adapters
│           ├── atomic_json.py  # Atomic persistence engine (UoW + self-healing validator)
│           └── system_clock.py # Concrete timezone-safe clock adapter
│
└── tests/                      # Validation Suite (14 modules)
    ├── __init__.py
    ├── test_domain.py              # Domain invariant & state machine checks
    ├── test_usecases.py            # Mocked use case flow & matching logic
    ├── test_infra.py               # Atomic I/O write recovery & persistence assertions
    ├── test_i18n.py                # Translation resolution logic validation
    ├── test_interactive.py         # Menu loop and hotkey validation
    ├── test_presenter_i18n.py      # Localized console rendering validation
    ├── test_accessibility.py       # --no-color & --linear screen-reader compliance
    ├── test_analytics.py           # Analytics service aggregation & export validation
    ├── test_archive.py             # Archive snapshot correctness & LGPD compliance
    ├── test_config_wizard.py       # Configuration wizard flow & persistence validation
    ├── test_coverage_hardening.py  # Edge-case coverage hardening & regression suite
    ├── test_csv_importer.py        # CSV batch import adapter correctness & schema checks
    └── test_tui_overhaul.py        # Terminal UI/UX visual redesign regression tests
```

---

## **💻 6. Local Engineering Development Setup**

### **6.1. Core System Prerequisites**

Before setting up the project, make sure you have the following environments installed:

- **Language Environment:** Python 3.10+ installed on the host system.
- **Package Manager:** `pip` (bundled with Python) and `virtualenv` recommended.
- **External Services:** None — FilaVaga is a 100% offline-first, air-gapped application.

> [!NOTE]
> **ASCII Fallback Mode:**
> If you are running the application in a legacy terminal or using screen readers that do not support unicode box-drawing characters, set the environment variable `FILAVAGA_ASCII=1` to force the UI presenter to render clean ASCII-only tables and borders.

### **6.2. Initial Bootstrap Sequence**

1. Clone this repository to your local workstation:

   ```bash
   git clone https://github.com/KalyelNLaurindo/filavaga.git
   cd filavaga
   ```

2. **Step 6.2.1 — Environment Setup:**
   Create and activate an isolated Python virtual environment to avoid dependency conflicts:

   ```bash
   python -m venv .venv

   # On Windows (PowerShell):
   .venv\Scripts\activate

   # On Unix/macOS:
   source .venv/bin/activate
   ```

3. **Step 6.2.2 — Application / Main Engine Setup:**
   Install the application in development mode (editable install, includes all dev dependencies):

   ```bash
   pip install -e ".[dev]"
   ```

   Verify the CLI entry point is registered correctly:

   ```bash
   filavaga --help
   ```

4. **Step 6.2.3 — Standalone Executable Compilation (Optional):**
   To compile a single air-gapped executable for SINE workstation distribution:

   ```bash
   pyinstaller filavaga.spec
   # Output binary will be located at: dist/filavaga.exe
   ```

### **6.3. Automated Verification Commands**

Ensure your modifications pass the repository quality gates before submitting a Pull Request:

- **Execute full test suite with coverage report**:

  ```bash
  pytest tests/ --cov=filavaga --cov-report=term-missing
  ```

- **Execute primary test engine (without coverage)**:

  ```bash
  pytest tests/
  ```

- **Verify static type constraints**:

  ```bash
  mypy filavaga/
  ```

- **Run code quality linter checks**:

  ```bash
  flake8 filavaga/
  ```

---

## **✅ 7. Delivered Features — Sprint 1 Completions (v1.2.0)**

The following capabilities were fully implemented and tested as part of the Sprint 1 completion cycle:

| Task   | Feature                                    | CLI Command               | Test File                   |
| :----- | :----------------------------------------- | :------------------------ | :--------------------------- |
| TSK-18 | CSV Data Import Adapter                    | `import-csv`              | `test_csv_importer.py`       |
| TSK-19 | Historical Archiving & Snapshot Compressor | `archive`                 | `test_archive.py`            |
| TSK-20 | Interactive Configuration Wizard           | `configure`               | `test_config_wizard.py`      |
| TSK-21 | Anonymized Placement Analytics Export      | `analyze`                 | `test_analytics.py`          |
| TSK-31 | CLI Accessibility Suite                    | `--no-color` / `--linear` | `test_accessibility.py`      |
| TSK-35 | Terminal UI/UX Visual Redesign             | `dashboard`               | `test_tui_overhaul.py`       |

---

## **🔮 8. Planned Roadmap: HTTP REST API Backend**

As detailed in task [TSK-34](context/backlog/TSK-34.md), we are planning to integrate a lightweight REST API server (using FastAPI) to expose the core matching engine and candidate queues over HTTP. This will allow FilaVaga to be run as an active backend service accessible to multiple SINE workstations simultaneously:

*   `POST /candidates` — Register a candidate.
*   `POST /vacancies` — Register a vacancy.
*   `POST /queues/fill` — Attempt to match and place a candidate.
*   `GET /queues/status` — Live status of all profession queues.

---

🏁 **End of Document:** This repository README serves as the definitive engineering portal for the **FilaVaga** ecosystem. Changes to stack versions, core patterns, or installation requirements must follow official pull-request governance.

Made with ❤️ by **Kalyel N. Laurindo / Software Engineer**
