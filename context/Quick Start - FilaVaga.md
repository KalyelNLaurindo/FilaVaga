# 📚 **FilaVaga Quick Start Guide**

This guide provides simple, sequential instructions to install, bootstrap, and run the **FilaVaga** application on your local machine.

---

## 📋 Prerequisites

Before setting up the project, make sure you have the following environments installed:

1.  **Python 3.10+** (Runtime Environment)
2.  **pip** (Python Package Manager)
3.  **Git** (Version Control System)

---

## 🚀 Step-by-Step Setup

### Step 1: Clone the Repository
Clone the repository to your local workspace directory using Git:
```bash
git clone https://github.com/KalyelNLaurindo/FilaVaga.git
cd FilaVaga
```

### Step 2: Set Up Virtual Environment (Recommended)
Create and activate a local virtual environment to isolate dependencies:
```bash
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies
Install the package in development mode along with its development/testing tools:
```bash
pip install -e .[dev]
```

### Step 4: Run CLI Engine
Verify the installation by running the help command of the CLI:
```bash
python -m filavaga.main --help
```

---

## ✅ Core Commands Reference

Here are the most frequently used commands to interact with the application:

| Action / Goal | Command Syntax | Description | Example |
| :--- | :--- | :--- | :--- |
| **Get Help/Usage** | `python -m filavaga.main --help` | Displays command line instructions and available subcommands. | `python -m filavaga.main --help` |
| **Register Candidate** | `python -m filavaga.main register --name "<name>" --cbo "<cbo>" --zone "<zone>"` | Registers a new candidate into the appropriate FIFO sub-queue. | `python -m filavaga.main register --name "Alice Smith" --cbo "4110-10" --zone "SUL"` |
| **Match Vacancy** | `python -m filavaga.main match --id "<vacancy_id>"` | Evaluates vacancy TTL and matches it with the top priority candidate. | `python -m filavaga.main match --id "v_01h3nb"` |
| **View TUI Dashboard** | `python -m filavaga.main dashboard` | Launches the interactive TUI console panel view. | `python -m filavaga.main dashboard` |
| **Purge PII Data** | `python -m filavaga.main purge-all` | Securely and permanently deletes all candidate PII databases. | `python -m filavaga.main purge-all` |
| **Run Test Suite** | `python -m pytest` | Runs the automated unit/integration test suite. | `python -m pytest` |

---

## ❓ Troubleshooting & Known Issues

| Error / Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'filavaga'` | Running main entrypoint without package path configurations. | Run the application as a module using: `python -m filavaga.main` instead of `python filavaga/main.py`. |
| `PermissionError: [Errno 13] Permission denied` | System lacks write permission in user home configuration folders (e.g. `~/.filavaga` or `C:\Users\<user>\.filavaga`). | Run the terminal with Administrator privileges or update your user permissions on the configuration home directory. |
| `JSONDecodeError` on state load | Hand-edited database snapshot corrupted or partial write. | Trigger the self-healing routine by executing any CLI command, or run `python -m filavaga.main purge-all` to reset local database states. |

---

🏁 **End of Document:** This guide is designed to get new developers onboarded quickly. For design decisions, domain state transition invariants, or architecture plans, consult the documentation under `context/`.

Made with ❤️ by **Kalyel N. Laurindo / Software Engineer**
