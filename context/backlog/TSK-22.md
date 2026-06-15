# TSK-22: REST-like In-Process Event Bus

* **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer  
* **Estimated Effort:** 4 Story Points / 16 Hours  
* **Story / Epic Reference:** Future / Extensibility & Adapter Decoupling  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement a lightweight, synchronous, in-process event bus to decouple the `QueueManager` application service from its downstream consumers (CLI presenter, persistence adapter, analytics). Currently, business events such as `CandidateEnqueued`, `VacancyExpired`, and `MatchFound` are tightly coupled to direct method calls, making it impossible to add new adapters (e.g., a future REST API, WebSocket notifier, or file exporter) without modifying core domain logic. The event bus introduces a `publish/subscribe` pattern internal to the process — no network sockets, no external broker — keeping the architecture clean, testable, and ready for future port-based extensions.

## ✅ Definition of Ready (DoR)

* [ ] TSK-07 (Port Abstractions) is complete — inbound/outbound interfaces are defined and stable.
* [ ] TSK-08 (QueueManager) is complete — all domain events are identifiable in the application service.
* [ ] Event taxonomy agreed upon: `CandidateEnqueued`, `CandidateStatusChanged`, `VacancyExpired`, `MatchFound`, `QueueFlushed`.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Core Mechanism):** `EventBus` class implemented in `filavaga/infra/event_bus.py` with `subscribe(event_type, handler)` and `publish(event)` methods. Handlers are callables registered per event type.
* [ ] **Criterion 2 (Domain Event Objects):** Dataclass-based event objects defined in `filavaga/domain/events.py` for each event in the agreed taxonomy. Each event carries a timestamp and the relevant domain identifiers.
* [ ] **Criterion 3 (QueueManager Integration):** `QueueManager` publishes domain events via the injected `EventBus` instance at each state transition. No direct calls to presenters or adapters remain inside the application service.
* [ ] **Criterion 4 (Backward Compatibility):** Existing CLI behavior is unchanged — the CLI handler subscribes to relevant events and triggers the `RichConsolePresenter` as before.
* [ ] **Criterion 5 (Quality/Test):** Unit tests in `tests/test_usecases.py` assert that publishing `CandidateEnqueued` triggers all registered subscribers exactly once, and that unregistered event types are silently ignored without raising exceptions.
