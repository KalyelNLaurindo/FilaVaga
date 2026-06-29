# TSK-28: i18n Translation Engine & Language Configuration Loader

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** NFR05 / ACCESSIBILITY & DX  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Establish a lightweight dynamic translation provider (i18n) to support Portuguese, English, French, Spanish, and German in the FilaVaga console application using only standard Python libraries.

The translation system will:
1. Define a `locales/` directory containing JSON translation resources for each language (e.g. `pt.json`, `en.json`, `fr.json`, `es.json`, `de.json`).
2. Implement a `TranslationService` that parses these resources at boot.
3. Automatically resolve the active language based on configuration file (`config.json`), CLI arguments (`--lang`), or system environment variables (`LANG` / `LC_ALL`), falling back to Portuguese (`pt`) if none is defined.

## ✅ Definition of Ready (DoR)

* [x] Core configuration system loads settings from `config.json` (TSK-01).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Testing/Quality - TDD]:** Unit tests verify that `TranslationService` successfully loads translation JSON keys and formats parameterized strings correctly for all 5 languages.
* [x] **[Functional - Resolution]:** `TranslationService` resolves the correct locale according to precedence: 1. CLI flag, 2. `config.json` entry, 3. OS Env variables, 4. Default fallback (`pt`).
* [x] **[Functional - Security]:** The file path resolver for locales sanitizes language input strings and blocks any directory traversal or arbitrary file access.
* [x] **[Verification]:** `pytest tests/test_infra.py` passes 100% green.
