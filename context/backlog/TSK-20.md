# TSK-20: Interactive Configuration Wizard

* **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** Future Enhancements / UX Hardening  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Implement an interactive setup wizard using the console terminal CLI. Instead of editing `config.json` manually with a text editor, administrators should be able to run a simple setup flow that guides them through modifying vacancy TTL, setting up database folders, selecting the system timezone, and specifying log options.

## ✅ Definition of Ready (DoR)

* [ ] `Rich` library console input prompt API reviewed for compatibility.
* [ ] Validation constraints for configuration keys (e.g. valid path structures, positive TTL values) defined in code.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] Implement CLI command route: `filavaga config-wizard`.
* [ ] The wizard prompts for values sequentially, displaying existing defaults and validating entries in real-time.
* [ ] The new parameters are saved atomically to `config.json` upon completion of the wizard flow.
* [ ] Interruption (Ctrl+C) during the wizard cancels gracefully without writing a corrupt or partial configuration.
