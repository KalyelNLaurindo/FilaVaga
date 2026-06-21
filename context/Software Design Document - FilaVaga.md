# **📋 Software Design Document: FilaVaga — Automated Queue-Native Vacancy Matching CLI**

**Role:** Project Owner / System Architect

**Objective:** Detail the technical implementation, architectural patterns, schemas, and structural boundaries of the FilaVaga command-line interface.

**Context:** FilaVaga is a highly optimized, local in-memory queue-management engine featuring high-precision FIFO queues, dynamic lazy-evaluated vacancy time-to-live (TTL) expiration, and atomic JSON persistence, designed to eliminate operational waitlist friction at SINE branches.

## **🏛️ Project Metadata**

- **Client / Segment:** Public Employment Center (SINE — Sistema Nacional de Emprego) — Local Branch Operations Tooling
- **Date of Creation:** June 15, 2026
- **Lead Architect:** Kalyel N. Laurindo / Software Engineer
- **Document Version:** v1.1
- **Associated Solution Architecture Document:** [Solution Architecture & Product Vision: FilaVaga](https://gemini.google.com/app/Solution Architecture Document - FilaVaga.md)

## **🛠️ 1. Technical Stack Overview**

### **1.1. Core Architectural Layers Form**

- **Field 1.1.1 - Frontend / Client Stack:**
  - *Technology/Framework:* Python Native CLI (`argparse` + Unicode TUI layout generator based on standard streams and `Rich` package components).
  - *Technical Rationale:* Eliminates external framework runtime overhead and security vulnerabilities. Guarantees zero installation footprint and 100% compatibility with standard terminal readers (NVDA/JAWS) on legacy Windows/Linux systems.
- **Field 1.1.2 - Backend Core Stack:**
  - *Technology/Framework:* Python 3.10+ Standard Library.
  - *Technical Rationale:* Relies entirely on built-in modules (`collections.deque`, `threading.Lock`, `uuid`, `datetime`) to guarantee zero-dependency execution. Features native type hinting for solid software engineering and static validation.
- **Field 1.1.3 - Database & Storage Engines:**
  - *Technology/Framework:* In-Memory Data Structures indexed via Python `dict` lookups, serialized to disk as flat JSON.
  - *Technical Rationale:* Operates at sub-millisecond speeds in-memory ($O(1)$ lookups). Eliminates external DB engine requirements (SQL Server, SQLite, Postgres) to prevent workspace permission lockouts and driver installation issues on restricted SINE workstations.
- **Field 1.1.4 - Message Brokers & Queue Managers:**
  - *Technology/Framework:* N/A (In-Memory `collections.deque` acts as the FIFO engine with standard synchronization).
  - *Technical Rationale:* The application runs as a single-process local execution lifecycle; complex distributed brokers (RabbitMQ/Kafka) are out of scope.
- **Field 1.1.5 - Gateway, Infrastructure & Orchestration:**
  - *Technology/Framework:* PyInstaller Standalone Executable Packaging.
  - *Technical Rationale:* Enables compilation into a single `.exe` (for Windows) or native binary (for Linux) with an embedded Python interpreter, allowing drag-and-drop deployment on air-gapped computers.
- **Field 1.1.6 - Observability & Telemetry:**
  - *Technology/Framework:* Standard Error Streaming (`stderr`) utilizing Structured JSON output formats.
  - *Technical Rationale:* Permits local piping, file-based logging redirection, and audit trailing without requiring cloud-based APMs or agents.

### **1.2. Technical Traceability Matrix (Pain Point ➔ Technical Module)**

#### **Traceability Entry 1: Qualified candidates skipped out of sequence due to manual sorting**

- **System Requirement ID:** RF01 (High-Precision FIFO Queue Engine)
- **Responsible Technical Module:** `filavaga.core.entities.Queue` & `filavaga.application.services.QueueManager` (guarantees strict monotonic registration timestamps and FIFO sequencing).

#### **Traceability Entry 2: Vacancies expiring unfilled without counselors noticing**

- **System Requirement ID:** RF02 (Temporal Vacancy TTL Manager)
- **Responsible Technical Module:** `filavaga.application.services.MatchEngine` (evaluates vacancy deadlines lazily on queries and rejects expired entries dynamically).

#### **Traceability Entry 3: Lost counselor productivity and spreadsheet file corruption**

- **System Requirement ID:** RF04 (Auto-Save Snapshot Manager) & NFR02
- **Responsible Technical Module:** `filavaga.infra.persistence.AtomicJsonRepository` (implements thread-safe file locks and atomic OS-level file replacement via temporary files).

## **🏗️ 2. Architectural Design & Core Patterns**

- **Field 2.1 - Core Architectural Pattern:** Hexagonal (Ports & Adapters)

### **💡 Architectural Pattern Details**

FilaVaga enforces strict architectural separation boundaries through the **Hexagonal (Ports & Adapters)** pattern. This ensures that the core business domain rules remain pure, testable, and isolated from CLI side effects, filesystem writing, or execution environment variables.

- **Field 2.2 - Design Pattern Description:** 1. **Core Domain:** Houses entities and invariant business logic. It contains no import of external configuration, JSON modules, or OS libraries.
  2. **Application Port Boundary:** Defines inbound ports (interfaces/use cases) executed by the CLI Commands, and outbound ports (e.g., `IStateRepository`) implemented by infrastructure drivers.
  3. **Adapters:** Standardizes CLI argument parsers (Inbound Adapters) and Atomic Serializers (Outbound Adapters) which plug into the ports.

```
                  +-------------------------------------------------+  
                  |               FilaVaga Core CLI                 |  
                  |                                                 |  
[ CLI Command ]  ===> [ CLI Command Controller ]                    |  
(argparse adapter)|         (Inbound Adapter)                       |  
                  |                 ||                              |  
                  |                 \/                              |  
                  |       [ IRegisterCandidate ]                    |  
                  |       [ IMatchVacancyUseCase ]                  |  
                  |          (Inbound Ports)                        |  
                  |                 ||                              |  
                  |                 \/                              |  
                  |    +--------------------------+                 |  
                  |    |      Domain Model        |                 |  
                  |    |  - Candidate (Entity)    |                 |  
                  |    |  - Vacancy (Entity)      |                 |  
                  |    |  - Queue (Aggregate)     |                 |  
                  |    +--------------------------+                 |  
                  |                 ||                              |  
                  |                 \/                              |  
                  |         [ IStateRepository ]                    |  
                  |           (Outbound Port)                       |  
                  |                 ||                              |  
                  +-----------------||------------------------------+  
                                    ||  
                                    \/  
                         [ AtomicJsonRepository ] ===> [ state_snapshot.json ]  
                            (Outbound Adapter)
```

### **2.1.2. Dependency Inversion & SOLID Principles Config**

- **Field 2.3 - Dependency Inversion & Event Dispatching:** Dependency Inversion is fully applied. The Application Use Cases depend on abstract Ports (interfaces like `IStateRepository`). At bootstrap, the concrete `AtomicJsonRepository` is injected into the services. High-precision system timestamps are fetched through a custom `IClock` port to prevent unit test dependency on the real system clock.

### **2.2. Communication Taxonomy**

- **In-Memory Event Bus:** N/A (Direct synchronous execution for local terminal latency optimization).
- **Message Broker / Event Bus:** N/A (Single-process standalone memory space).
- **Job Queues:** N/A (Operations execute synchronously inside the CLI execution lifecycle).

## **🔐 3. Security Architecture & Data Protection**

### **✍️ Security Specification Form**

- **Field 3.1 - Data In Transit Protocol:** Local In-Memory Communication (Zero-network execution; data never traverses a local or public network card).
- **Field 3.2 - Data At Rest Encryption Standard:** Delegated to Operating System Level Encryption (LUKS/BitLocker). Application restricts file permissions on the storage directories and JSON database files (e.g., `0700` for directories and `0600` for files on POSIX, and restricted DACLs on Windows) to prevent local user traversal.
- **Field 3.3 - Password & Key Derivation Function:** N/A (FilaVaga is a local utility execution system with no shared credentials. It executes under the existing host OS session authority).
- **Field 3.4 - Access Delegation Protocol:** OS-Level Access Control Lists & Permission Guards (Restricts read/write permissions at snapshot file creation so only the owning OS user has read/write privileges).
- **Field 3.5 - Emergency Recovery Policy:** If state data corruption occurs, FilaVaga keeps the previous valid session snapshot under `state_snapshot.json.bak`. During initialization, a schema integrity check validates the active file; if corrupted, it auto-restores the backup and displays a warning to `stderr`.

## **🧩 4. Evolutionary Blueprint (Scaling Path)**

- **Module Extraction Path A:** `filavaga.infra.persistence` ➔ Can be extracted into a remote database adapter (e.g., PostgreSQL/SQL Server) by implementing the `IStateRepository` interface, without touching the application use case logic.
- **Module Extraction Path B:** `filavaga.cli` ➔ Can be extracted or expanded into an HTTP REST API adapter (FastAPI/Flask) or a Web UI controller by mapping web payloads to the existing Inbound Ports.

## **📐 5. System Component Diagram (C4 Model — Level 3: Inside Core Backend App)**

```
graph TD
    subgraph SINE_Client [Terminal Shell / UI Adapter]
        CLIParser["Argparse Command Parser<br>(Inbound Adapter)"]
        CLITable["Rich Console Presenter<br>(Output Formatting)"]
    end

    subgraph FilaVaga_Engine [Core Engine Assembly]
        subgraph Inbound_Ports [Inbound Ports]
            IRegUseCase["IRegisterCandidateUseCase<br>(Port Interface)"]
            IMatchUseCase["IMatchVacancyUseCase<br>(Port Interface)"]
        end

        subgraph Application_Services [Application Domain Coordination]
            QueueMgr["QueueManager<br>(Coordinates admissions & states)"]
            MatchEngine["MatchEngine<br>(Executes matching rules)"]
        end

        subgraph Domain_Core [Pure Invariant Domain]
            CandidateEntity["Candidate Entity<br>(Invariants & Status)"]
            VacancyEntity["Vacancy Entity<br>(TTL & Capacity Rules)"]
            QueueAggregate["Queue Aggregate<br>(FIFO Order Enforcement)"]
        end

        subgraph Outbound_Ports [Outbound Ports]
            IRepoPort["IStateRepository<br>(Port Interface)"]
            IClockPort["IClock<br>(System Clock Port)"]
        end

        subgraph Outbound_Adapters [Infrastructure Drivers]
            AtomicRepo["AtomicJsonRepository<br>(Safe disk snapshotting)"]
            SystemClock["SystemClock<br>(ISO UTC datetime driver)"]
        end
    end

    subgraph Disk_Storage [Filesystem Boundary]
        JSONFile[("state_snapshot.json<br>(Encapsulated state)")]
    end

    %% CLI and Port Connections
    CLIParser -->|Invokes| IRegUseCase
    CLIParser -->|Invokes| IMatchUseCase
    
    IRegUseCase -.->|Implemented by| QueueMgr
    IMatchUseCase -.->|Implemented by| MatchEngine

    %% Use Case & Domain Bindings
    QueueMgr -->|Mutates / Validates| QueueAggregate
    QueueAggregate -->|Contains| CandidateEntity
    MatchEngine -->|Evaluates| VacancyEntity
    MatchEngine -->|Iterates| QueueAggregate

    %% Outbound Infrastructure Inversion
    QueueMgr -->|Persists via| IRepoPort
    MatchEngine -->|Checks time via| IClockPort
    
    IRepoPort -.->|Implemented by| AtomicRepo
    IClockPort -.->|Implemented by| SystemClock
    
    AtomicRepo <-->|Reads/Atomic Writes| JSONFile
    CLITable <---|Reads Match Result| MatchEngine
```

## **📂 6. Data Architecture (Relational & Document Design)**

### **✍️ Data Architecture Form Entry**

- **Field 6.1 - Primary Database Schemas:**

  FilaVaga stores state as a normalized, single-document JSON snapshot schema, validating structures against strict structural types.

```
{
  "$schema": "https://filavaga.org/schemas/v1.0/state.json",
  "metadata": {
    "app_id": "filavaga-sine-local",
    "updated_at": "2026-06-15T13:40:00Z",
    "schema_version": "1.0"
  },
  "candidates": {
    "c_01h3nbd7z6r6e": {
      "id": "c_01h3nbd7z6r6e",
      "name": "Maria Silva",
      "sector_zone": "SUL",
      "profession_code": "4110-10",
      "registered_at": "2026-06-15T08:30:15Z",
      "status": "PENDING"
    },
    "c_01h3nbeh8z4y2": {
      "id": "c_01h3nbeh8z4y2",
      "name": "João Santos",
      "sector_zone": "NORTE",
      "profession_code": "4110-10",
      "registered_at": "2026-06-15T09:12:00Z",
      "status": "CONTACTED"
    }
  },
  "vacancies": {
    "v_01h3nbfa4y1z8": {
      "id": "v_01h3nbfa4y1z8",
      "title": "Auxiliar Administrativo",
      "profession_code": "4110-10",
      "sector_zone": "SUL",
      "capacity": 2,
      "created_at": "2026-06-15T10:00:00Z",
      "expires_at": "2026-06-16T10:00:00Z"
    }
  },
  "queues": {
    "4110-10": {
      "profession_code": "4110-10",
      "candidate_ids": [
        "c_01h3nbd7z6r6e",
        "c_01h3nbeh8z4y2"
      ]
    }
  }
}
```

- **Field 6.2 - Indexing & Optimization Strategy:**

  To guarantee matching execution of $<5\text{ms}$ on legacy hardware, the in-memory engine constructs hash indexes during boot:

  1. **Primary Index (`dict`):** Matches candidate ID to their full Python Object $O(1)$.

  2. **Secondary Attribute Map (`dict[str, collections.deque]`):** Groups candidate IDs chronologically by profession code ($O(1)$ queue tail appends).

  3. **Index Lookup Complexity:**

     

     $$\text{Retrieval of FIFO Candidate} = O(1)$$

     $$\text{Attribute-Based Filter Scan (Zone, Status)} = O(K) \quad \text{where } K \ll N \text{ (only scanning active queue subclass indices)}$$

- **Field 6.3 - Database Automation & Lifecycle Events:**

  Because FilaVaga operates entirely on local volatile/file configurations:

  1. **Lazy Garbage Collection:** Candidate entities marked as `PLACED` or `REJECTED` are automatically pruned from active memory indexes after 30 days during boot optimization checks.
  2. **Snapshot Compaction:** Retains structural state consistency while omitting log lists if files exceed $50\text{MB}$.

## **🚀 7. Continuous Integration, Deployment & QA**

- **Test-Driven Development (TDD) Cycle:** * *Red Phase:* Implement unit tests with strict domain assertions (e.g., verifying `Candidate` status validation exceptions when transiting directly from `PENDING` to `PLACED` without going through `CONTACTED`).
  - *Green Phase:* Complete minimal implementations in Python codebase.
  - *Refactor:* Clean code smell signatures, enforce static typing checks with `mypy`, and maintain strict PEP 8 alignment.
- **Automated Architecture Guardrails:**
  - **Zero Leakage Rule:** An automated pre-commit hook runs `import-linter` to block compilation if any file in `filavaga.core` imports from `filavaga.application` or `filavaga.infra`.
- **Test Isolation Pyramid:**
  - **Unit Tests:** Target `filavaga.core` (entities, status validations, invariant integrity). Mocked time constraints are managed by `SystemClock` mock objects.
  - **Integration Tests:** Validate the `AtomicJsonRepository` write behavior. Ensure that if disk space is exhausted during writing, the original state snapshot remains perfectly intact.
  - **End-to-End Tests:** Execute terminal integration CLI invocations (e.g., simulating a user command stream: `filavaga register` -> `filavaga match` -> outputs validation checks in JSON).

## **🎨 8. User Interface Design System (UI Architecture)**

- **Field 8.1 - Design Philosophy & Design Tokens:**

  FilaVaga operates as an expressive CLI. Visual structure is constructed through standard ANSI terminal escape sequences and Unicode box-drawing character maps.

  - *Standard Text Color:* Neutral terminal default (white/gray on dark mode).
  - *Primary Brand Accent:* Teal terminal block for titles (`#008080`).
  - *Priority Alerts:* Bright Amber for warning alerts; Crimson for blocking validation errors.
  - *Interface Border:* Double-lined unicode table cells for clean legibility.

### **8.2. Rich Console Interface & Layout Frames**

To support rapid keyboard execution and visual control, FilaVaga renders distinct, professional TUI (Terminal User Interface) framed layouts mapped below.

#### **TUI Layout A: Interactive Main Dashboard (Command: `filavaga dashboard`)**

Used to inspect total waitlists, expiring vacancies, and system operational parameters.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  FilaVaga :: PAINEL DE CONTROLE DE FILAS (SINE LOCAL)           [ v1.1.0 ]   │
├──────────────────────────────────────────────────────────────────────────────┤
│  ESTADO DO SISTEMA: [ ATIVO ]                       DATABASE: [ OK - LOCAL ] │
├──────────────────────────────────────────────────────────────────────────────┤
│  [ FILAS ATIVAS NO RAMO ]                                                    │
│  ┌─────────────────────────┬─────────────────────────┬────────────────────┐  │
│  │ CÓD. PROFISSÃO (CBO)    │ CANDIDATOS EM ESPERA    │ STATUS DA FILA     │  │
│  ├─────────────────────────┼─────────────────────────┼────────────────────┤  │
│  │ 4110-10 (Aux. Admin.)   │ [ 42 ]                  │ NORMAL             │  │
│  │ 7152-10 (Pedreiro)      │ [ 18 ]                  │ ALTA DEMANDA       │  │
│  │ 5143-20 (Aux. Serviços) │ [ 09 ]                  │ NORMAL             │  │
│  └─────────────────────────┴─────────────────────────┴────────────────────┘  │
│                                                                              │
│  [ VAGAS COM RISCO DE EXPIRAÇÃO (ALERTA TTL - PROX. 24H) ]                   │
│  • Vaga #v_01h3n: Aux. Administrativo (SUL) - Expira em: [ 04h 12m ]         │
│  • Vaga #v_01h8j: Cozinheiro (NORTE)          - Expira em: [ 18h 45m ]         │
├──────────────────────────────────────────────────────────────────────────────┤
│  LEGENDA DE COMANDOS RÁPIDOS:                                                │
│  [D] Dashboard   [R] Cadastrar Candidato   [M] Parear Vaga   [Q] Sair        │
├──────────────────────────────────────────────────────────────────────────────┤
│  FilaVaga CLI > _                                                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### **TUI Layout B: Interactive Match Resolution Screen (Command: `filavaga match --id <v_id>`)**

Renders a structured interface showcasing the targeted vacancy details side-by-side with the highest-priority FIFO candidate match.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  FilaVaga :: PROCESSADOR DE PAREAMENTO (MATCHING ENGINE)                     │
├──────────────────────────────────────────────────────────────────────────────┤
│  [ DADOS DA VAGA REQUERIDA ]                                                 │
│  ID: v_01h3nbfa4y1z8         Título: Auxiliar Administrativo                 │
│  CBO: 4110-10                Zona: SUL               Vagas Abertas: [ 02 ]   │
│  Data Limite (TTL): 2026-06-16T10:00:00Z             Tempo Restante: [ 19h ] │
├──────────────────────────────────────────────────────────────────────────────┤
│  [ CANDIDATO EM TOPO DE FILA ENCONTRADO (CRITÉRIO FIFO SEGUIDO) ]            │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ID: c_01h3nbd7z6r6e                                                    │  │
│  │ Nome Completo: MARIA SILVA                                             │  │
│  │ Data de Inscrição na Fila: 2026-06-15T08:30:15Z (Posição: #1)           │  │
│  │ Zona de Preferência: SUL                       Aptidão Técnica: 100%   │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────┤
│  Deseja prosseguir com o contato com o candidato?                            │  │
│  [S] Confirmar Contato (Transita para CONTACTED)                             │  │
│  [N] Pular Candidato (Gera Skip Log e busca próximo)                          │  │
│  [C] Cancelar Operação                                                       │  │
├──────────────────────────────────────────────────────────────────────────────┤
│  Ação Selecionada > _                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### **TUI Layout C: Built-in Command Reference Manual (Command: `filavaga --help`)**

Displayed when an invalid execution argument is provided or explicitly requested.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  FilaVaga CLI :: GUIA DE COMANDOS & ATALHOS RÁPIDOS                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  Uso Geral: filavaga <comando> [opções]                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│  COMANDOS SUPORTADOS:                                                        │
│                                                                              │
│    register --name "<nome>" --cbo "<cbo>" --zone "<zona>"                    │
│      Adiciona um novo trabalhador no final da fila FIFO correspondente.      │
│                                                                              │
│    match --id "<vaga_id>"                                                    │
│      Roda o motor de busca pelo candidato elegível prioritário de forma      │
│      interativa sem alterar ordens de forma indevida.                        │
│                                                                              │
│    dashboard                                                                 │
│      Renderiza o painel visual com métricas, filas e alertas de TTL.         │
│                                                                              │
│    status-update --candidate "<id>" --to "<PENDING|CONTACTED|PLACED>"        │
│      Altera manualmente o estado de um registro na máquina de estados.       │
│                                                                              │
│    purge-all                                                                 │
│      Remove de forma segura dados locais de PII sob as regras da LGPD.       │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  Dúvidas ou problemas com o snaphost? Contate: suporte@koyosstudios.com.br   │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Field 8.3 - Responsive Viewports & Layouts:**

  Automatically measures system terminal width via `os.get_terminal_size()`. If width is $<80$ characters, detailed candidate metadata arrays collapse into a vertical list to prevent horizontal wrapping and terminal line corruption.

### **8.4. Multi-Language i18n Architecture**

To support non-English or localized SINE environments, FilaVaga abstracts all UI labels, headers, and logs from execution logic:
- **Translation Resource Files (`locales/*.json`):** Independent dictionary files mapped for `pt` (Portuguese), `en` (English), `fr` (French), `es` (Spanish), and `de` (German).
- **Locale Resolution Precedence:**
  1. CLI parameter override (e.g. `--lang fr`).
  2. Configuration profile setting loaded from `config.json` (`"lang": "es"`).
  3. Workstation host environment variable mapping (`LANG` or `LC_ALL`).
  4. Default system fallback (`pt`).
- **Interactive Hotkeys:** Allows layperson dynamic switching at runtime in the active shell using single-character commands.

## **📈 9. Observability & System Monitoring**

- **Field 9.1 - Logging Aggregator Strategy:**

  Standard operations print to standard output `stdout`. System error traces, serialization alerts, and clock drifts are written to `stderr` formatted as structured, single-line JSON logs to allow compatibility with standard log monitoring agents (e.g., Vector, Filebeat).

- **Field 9.2 - Telemetry Metrics collected:**

  Each command execution records execution latency, local system memory footprint, candidate volume queue lengths, and active lock contention durations.

## **🚀 10. Deployment Topology (Transition Plan)**

### **✍️ Deployment Topology Form Entry**

- **Field 10.1 - Local / Development Compute:** Local virtualenv (Python isolated environments running Python 3.10+).
- **Field 10.2 - Production Cloud Compute:** Local CLI Executable (Self-contained executable artifact packaged using PyInstaller, operating fully local, offline, and workstation-native).
- **Field 10.3 - Production Database Engine:** Embedded SQLite DB / Local Flat Files (Flat JSON state snapshot file saved to user's standard platform home configuration folder).
- **Field 10.4 - Routing, DNS & SSL Layer:** N/A (Offline application operating natively at standard process boundaries).

## **📂 11. Codebase Structure & Directory Standards**

- **Field 11.1 - Directory Strategy:** Single Repo Monolith

### **💡 Directory Layout Entry**

```
filavaga-cli/
├── pyproject.toml              # Build specifications, dependencies & tool rules
├── config.json                 # JSON local workspace rules & business TTL limits
├── logs/                       # Local directory for logging exports
├── filavaga/                   # Core application root
│   ├── __init__.py
│   ├── main.py                 # CLI entry point bootstrap coordinator
│   │
│   ├── core/                   # Domain Core Layer (Pure Logic)
│   │   ├── __init__.py
│   │   ├── entities.py         # Invariant Business Models (Candidate, Vacancy, Queue)
│   │   ├── value_objects.py    # Immutable Types (ProfessionCode, SectorZone, Timestamp)
│   │   └── exceptions.py       # Domain-specific validation exceptions
│   │
│   ├── application/            # Application Use Case Layer (Ports & Orchestrators)
│   │   ├── __init__.py
│   │   ├── ports/              # Port Abstractions (Boundary Interfaces)
│   │   │   ├── inbound.py      # IRegisterCandidate, IMatchVacancy
│   │   │   └── outbound.py     # IStateRepository, IClock
│   │   └── services/           # Service Managers (QueueManager, MatchEngine)
│   │
│   ├── infra/                  # Infrastructure Adapter Layer (Concrete Drivers)
│   │   ├── __init__.py
│   │   ├── cli/                # Terminal CLI UI Adapters (Argparse, Presenter)
│   │   │   ├── command_router.py
│   │   │   └── presenter.py
│   │   └── persistence/        # Storage Adapters
│   │       ├── atomic_json.py  # Atomic persistence engine
│   │       └── system_clock.py # Concrete timezone-safe clock adapter
│   │
└── tests/                      # Validation Suite
    ├── __init__.py
    ├── test_domain.py          # Domain invariant checks
    ├── test_usecases.py        # Mocked use case flow matching logic
    └── test_infra.py           # Atomic I/O write recovery assertions
```

## **🧪 12. Validation Strategy & Testing Matrix**

### **✍️ Testing Matrix Form Entry**

- **Field 12.1 - Unit Testing Framework & Targets:** Uses `pytest` targeting pure domain components inside `filavaga.core`. Validates structural queue FIFO integrity, invalid status transitions, and profession string sanitizations without mock frameworks.
- **Field 12.2 - Integration Testing Framework & Targets:** Uses `pytest` and built-in filesystem mock decorators. Asserts integration boundaries of `AtomicJsonRepository` against partial write failures, corrupted configurations, and disk access locks.
- **Field 12.3 - End-to-End Testing Framework & Targets:** Automated CLI integration testing scripts using Python `subprocess` executions. Validates command streams against various console standard error metrics.

## **📝 13. Architecture Decision Records (ADR)**

### **ADR-001 (Primary Database Selection): JSON Flat-File Persistence**

- **Context:** SINE branches run legacy systems with highly restricted workspace admin permissions. DBMS engines (SQL Server, SQLite, Postgres) often fail to install or write due to active IT permissions policies.
- **Decision:** Implement 100% in-memory data structures, serialized on demand to a single JSON flat file on standard local user configurations.
- **Rationale:** Bypasses admin level lockouts, operates with zero database server overhead, allows instant migrations, and achieves sub-millisecond retrieval speeds.

### **ADR-002 (Concurrency Strategy): Thread-Safe Threading Locks**

- **Context:** Counselors may call asynchronous queries or perform CLI snapshot exports concurrently on the same machine session.
- **Decision:** Core application services are protected by a coarse-grained system `threading.Lock` during write transactions.
- **Rationale:** Guarantees absolute sequential operations on in-memory queue arrays, eliminating database-level race condition anomalies.

### **ADR-003 (Time-to-Live Verification): Lazy Matching Evaluations**

- **Context:** Continuous time polling loops consume system CPU cycles on legacy, resource-constrained SINE hardware.
- **Decision:** Apply Lazy Evaluation pattern for vacancy TTL checks at execution query time.
- **Rationale:** Vacancies are assessed and invalidated dynamically when matched against candidates, ensuring zero background processor consumption.

### **ADR-004 (State Mutability and Abstraction Leak Prevention): Deep Copies on Repository Operations**

- **Context:** `AtomicJsonRepository` maintains internal in-memory collections of domain models. If read methods (`get_candidate`, etc.) return direct references or shallow copies to these mutable models, the application layer can mutate their states directly. This bypasses the repository's `.save_*()` methods, causing in-memory state drift that is never serialized to disk and violates repository encapsulation.
- **Decision:** Perform deep copies (`copy.deepcopy`) on all domain objects returned by query/read methods (`get_candidate`, `get_all_candidates`, `get_vacancy`, `get_all_vacancies`, `get_queue`) and on all objects passed to mutation/write methods (`save_candidate`, `save_vacancy`, `save_queue`) before caching them.
- **Rationale:** Deep copying guarantees that the internal repository state cannot be mutated from the outside, enforcing a strict boundary between application runtime mutations and the persistence engine. It preserves encapsulation without requiring heavy refactoring of existing domain entities.

### **ADR-005 (Transactional Consistency & Unit of Work Pattern): context manager commit orchestration**

- **Context:** Sequential writes to multiple independent entities (e.g. saving a candidate status update and then saving the queue aggregate state) in the application layer can result in a "split-brain" database state if a crash or error occurs mid-way.
- **Decision:** Introduce a Unit of Work (`IUnitOfWork`) pattern using Python context managers. All database modifications are staged in-memory within the `with` block and committed atomically to disk as a single transaction upon successful exit. Any exception raised inside the block triggers a rollback of the in-memory cache to prevent dirty states.
- **Rationale:** Guarantees transactional atomic execution (ACID properties) in a local flat-file storage environment without database server overhead.

### **ADR-006 (Aggregate Self-Sufficiency & Domain Encapsulation of Queue Invariants): self-contained Queue sorting via QueueEntry value objects**

- **Context:** Currently, `Queue.add_candidate()` requires an injected parameter `candidates_map: dict[str, Candidate]` to access candidate registration timestamps and sort candidate IDs chronologically. This violates aggregate boundary isolation and creates high coupling by injecting repository-like collections into the domain aggregate root.
- **Decision:** Remodel the relationship so that `Queue` maintains its chronological FIFO ordering invariants internally. Instead of storing raw string IDs, `Queue` will store a list of `QueueEntry` Value Objects, where each `QueueEntry` contains both the `candidate_id` and the `registered_at` timestamp. The `add_candidate` method signature will be refactored to `add_candidate(candidate_id: str, registered_at: str)`.
- **Rationale:** By wrapping the required sorting data in a local Value Object (`QueueEntry`), the `Queue` aggregate root remains self-sufficient and fully protects its internal ordering invariants. It respects the DDD rule of reference-by-ID for cross-aggregate associations (since `Candidate` and `Queue` are distinct aggregate roots) while completely eliminating external parameters/map injection, ensuring clean domain boundaries and loose coupling.

## **🏛️ 14. Code Governance & Naming Standards**

### **✍️ Code Governance Form Entry**

- **Field 14.1 - Domain Entity Naming Style:** Clean naming (e.g., `Candidate`, `Vacancy`, `Queue` represent entities directly to align with SINE's real domain language).
- **Field 14.2 - Value Object Naming Style:** Clean naming (e.g., `ProfessionCode`, `SectorZone`, `RegistrationTimestamp`).
- **Field 14.3 - Ports & Interfaces Prefix/Suffix:** I Prefix (e.g., `IStateRepository`, `IClock`, `IRegisterCandidateUseCase` to guarantee explicit interface definitions in Python duck-typed protocols).
- **Field 14.4 - Adapters Suffix:** Database Name Suffix / Console Name Suffix (e.g., `AtomicJsonRepository` implements `IStateRepository`; `ArgparseCLIAdapter` implements input routing).

## **🛡️ 15. Resilience & Disaster Recovery Plan (DRP)**

### **✍️ Resilience Rules Configurator Form**

- **Rule 15.1 - Atomic State Mutations (Write Isolation):** **INCLUDED.** * *Implementation Strategy:* To protect SINE branches from sudden OS power outages and file corruption, writing data directly to `state_snapshot.json` is strictly forbidden. The system writes state payloads to a unique temporary file (`state_snapshot.json.tmp`) first, validates the JSON parsing structure of this temporary file in-memory, and then performs an atomic OS-level file rename operation (`os.replace()`). This guarantees that if a system crash occurs mid-write, the previous database snapshot remains uncorrupted.
- **Rule 15.2 - Auto-Healing Schema Validation:** **INCLUDED.** * *Implementation:* On startup, the CLI automatically scans the state file schema against v1.0 specifications. If corruption is detected, the initialization routine moves the corrupted file to `corrupted_snapshot.json.err` for analysis, restores the fallback metadata sequence `state_snapshot.json.bak`, and reports a recovery message to the supervisor on terminal `stderr`.
- **Rule 15.3 - Backup and Database Replication Strategy:** **INCLUDED.**
  - *Implementation:* During every atomic rewrite transaction, the prior valid state configuration is cloned to `state_snapshot.json.bak` before updating the active reference pointer.
- **Rule 15.4 - Queue & Job Persistence Strategy:** **INCLUDED.**
  - *Implementation:* High-precision ISO-8601 UTC registration timestamps are hard-persisted inside each candidate node, ensuring absolute queue chronology is retained across reboots.

## **🤝 16. System Service Integration Contracts**

Every change in local queue status outputs a structured CLI log event to terminal standard error streams for monitoring:

```
{  
  "event_id": "89b7b90e-b7d2-43f6-95ff-3d02b85a3c94",  
  "timestamp": "2026-06-15T13:40:02Z",  
  "payload": {  
    "scope_code": "SINE_SUL_01",  
    "category": "CANDIDATE_QUEUE_ADMISSION",  
    "change_type": "CREATE",  
    "raw_diff": {  
      "field": "status",  
      "old_value": null,  
      "new_value": "PENDING"  
    },  
    "summarized_explanation": "Candidate c_01h3nbd7z6r6e admitted to Queue '4110-10' in priority FIFO sequence."  
  }  
}
```

## **📖 17. Ubiquitous Domain Glossary**

- **FIFO Queue Engine:** The priority-ordered structural array mapping SINE candidates to specific profession queues based strictly on chronological registration timestamps.
- **Lazy Expiration Watcher:** The temporal processing routine that validates vacancy TTL limits dynamically at the exact millisecond of matching evaluation.
- **Atomic Persistence Drive:** The file serialization subsystem that isolates disk mutations using temporary staging files and OS-level renames to protect operations against physical power failures.
- **Status State Machine:** The predefined transition path for candidate records (`PENDING` ➔ `CONTACTED` ➔ `PLACED` or `REJECTED`).

🏁 **End of Document:** FilaVaga Software Design Document v1.1. Configured by Kalyel N. Laurindo / Software Engineer.