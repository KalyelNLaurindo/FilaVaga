"""
Atomic JSON Persistence Engine Adapter.

Implements IStateRepository with thread-safe lock mechanisms and
atomic file-system writes (tmp staging + os.replace).

Author: Kalyel N. Laurindo / Software Engineer
"""

import os
import json
import shutil
import threading
import logging
import copy
from filavaga.application.ports.outbound import IStateRepository, IUnitOfWork
from filavaga.core.entities import Candidate, Vacancy, Queue, QueueEntry

logger = logging.getLogger("filavaga")


class AtomicJsonRepository(IStateRepository):
    """
    Local JSON file repository for atomic state mutations.
    
    Protects read/write operations using threading.Lock.
    Uses temp staging files and os.replace to prevent file corruption.
    """

    def __init__(self, filepath: str):
        self._filepath = os.path.abspath(filepath)
        self._lock = threading.RLock()
        self._candidates = {}
        self._vacancies = {}
        self._queues = {}
        self._in_transaction = False
        
        # Ensure parent directory exists and apply secure permissions
        parent_dir = os.path.dirname(self._filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
            self._apply_secure_permissions(parent_dir, is_dir=True)
            
        self._load_state_from_disk()

    def _apply_secure_permissions(self, path: str, is_dir: bool = False) -> None:
        """
        Enforce strict file-system access control lists/permissions on both POSIX and Windows.
        POSIX: 0700 for directories, 0600 for files.
        Windows: Disable inheritance and grant Full Control only to current user and SYSTEM.
        """
        if not os.path.exists(path):
            return

        if os.name != "nt":
            # POSIX permission hardening
            mode = 0o700 if is_dir else 0o600
            try:
                os.chmod(path, mode)
            except Exception as e:
                logger.warning("Failed to apply POSIX permissions on %s: %s", path, e)
        else:
            # Windows security hardening (using native icacls utility)
            import subprocess
            import getpass
            try:
                # 1. Disable inheritance and remove all inherited ACEs
                subprocess.run(
                    ["icacls", path, "/inheritance:r"],
                    capture_output=True, check=True, text=True
                )
                
                # 2. Grant Full Control (F) to SYSTEM (S-1-5-18)
                inherit_flag = "(OI)(CI)" if is_dir else ""
                subprocess.run(
                    ["icacls", path, "/grant:r", f"*S-1-5-18:{inherit_flag}F"],
                    capture_output=True, check=True, text=True
                )
                
                # 3. Grant Full Control (F) to the current user
                username = getpass.getuser()
                subprocess.run(
                    ["icacls", path, "/grant:r", f"{username}:{inherit_flag}F"],
                    capture_output=True, check=True, text=True
                )
            except Exception as e:
                logger.warning("Failed to apply Windows DACL permissions on %s: %s", path, e)


    @property
    def filepath(self) -> str:
        """
        Return the absolute filepath of the state repository database.
        """
        return self._filepath

    def get_candidate(self, candidate_id: str) -> Candidate | None:
        with self._lock:
            candidate = self._candidates.get(candidate_id)
            return copy.deepcopy(candidate) if candidate else None

    def save_candidate(self, candidate: Candidate) -> None:
        with self._lock:
            self._candidates[candidate.id] = copy.deepcopy(candidate)
            if not self._in_transaction:
                self._save_state_to_disk()

    def get_all_candidates(self) -> dict[str, Candidate]:
        with self._lock:
            return {c_id: copy.deepcopy(c) for c_id, c in self._candidates.items()}

    def get_vacancy(self, vacancy_id: str) -> Vacancy | None:
        with self._lock:
            vacancy = self._vacancies.get(vacancy_id)
            return copy.deepcopy(vacancy) if vacancy else None

    def save_vacancy(self, vacancy: Vacancy) -> None:
        with self._lock:
            self._vacancies[vacancy.id] = copy.deepcopy(vacancy)
            if not self._in_transaction:
                self._save_state_to_disk()

    def get_all_vacancies(self) -> dict[str, Vacancy]:
        with self._lock:
            return {v_id: copy.deepcopy(v) for v_id, v in self._vacancies.items()}

    def get_queue(self, profession_code: str) -> Queue | None:
        with self._lock:
            queue = self._queues.get(profession_code)
            return copy.deepcopy(queue) if queue else None

    def save_queue(self, queue: Queue) -> None:
        with self._lock:
            self._queues[queue.profession_code] = copy.deepcopy(queue)
            if not self._in_transaction:
                self._save_state_to_disk()

    def _load_state_from_disk(self) -> None:
        """Read snapshot from disk, validate its schema and rebuild domain objects in memory."""
        if not os.path.exists(self._filepath):
            logger.info("No existing snapshot found at %s. Initializing empty state.", self._filepath)
            return

        try:
            logger.debug("Loading state snapshot from %s.", self._filepath)
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if not isinstance(data, dict):
                raise ValueError("Root element of state snapshot must be a JSON object.")
                
            required_sections = ["metadata", "candidates", "vacancies", "queues"]
            for section in required_sections:
                if section not in data:
                    raise KeyError(f"Missing required section '{section}' in state snapshot.")
                
            candidates_data = data.get("candidates", {})
            for c_id, c_val in candidates_data.items():
                self._candidates[c_id] = Candidate(
                    id=c_val["id"],
                    name=c_val["name"],
                    sector_zone=c_val["sector_zone"],
                    profession_code=c_val["profession_code"],
                    registered_at=c_val["registered_at"],
                    status=c_val["status"]
                )

            vacancies_data = data.get("vacancies", {})
            for v_id, v_val in vacancies_data.items():
                self._vacancies[v_id] = Vacancy(
                    id=v_val["id"],
                    title=v_val["title"],
                    profession_code=v_val["profession_code"],
                    sector_zone=v_val["sector_zone"],
                    capacity=v_val["capacity"],
                    created_at=v_val["created_at"],
                    expires_at=v_val["expires_at"],
                    placed_candidate_ids=v_val.get("placed_candidate_ids", [])
                )

            queues_data = data.get("queues", {})
            for q_code, q_val in queues_data.items():
                entries = []
                for c_id in q_val.get("candidate_ids", []):
                    c_obj = self._candidates.get(c_id)
                    if c_obj:
                        entries.append(QueueEntry(candidate_id=c_id, registered_at=c_obj.registered_at))
                self._queues[q_code] = Queue(
                    profession_code=q_val["profession_code"],
                    entries=entries
                )
            logger.info("Successfully loaded state snapshot from disk.")
        except Exception as e:
            logger.warning("Active snapshot file at %s is corrupted or violates schema. Error: %s. Isolating to .err and attempting backup recovery.", self._filepath, e)
            
            # Isolate the corrupt file
            err_path = self._filepath + ".err"
            try:
                if os.path.exists(self._filepath):
                    if os.path.exists(err_path):
                        os.remove(err_path)
                    os.rename(self._filepath, err_path)
                    self._apply_secure_permissions(err_path, is_dir=False)
            except Exception as isolation_err:
                logger.error("Failed to isolate corrupted file to %s. Error: %s", err_path, isolation_err)
                
            bak_path = self._filepath + ".bak"
            if os.path.exists(bak_path):
                # Restore backup
                try:
                    logger.info("Restoring backup from %s.", bak_path)
                    shutil.copy2(bak_path, self._filepath)
                    self._apply_secure_permissions(self._filepath, is_dir=False)
                    self._load_state_from_disk()
                except Exception as ex:
                    logger.error("Failed to restore backup snapshot. Error: %s. Resetting to empty state.", ex)
                    self._candidates.clear()
                    self._vacancies.clear()
                    self._queues.clear()
            else:
                logger.error("No backup snapshot file found at %s. Initializing clean empty state.", bak_path)
                self._candidates.clear()
                self._vacancies.clear()
                self._queues.clear()

    def _save_state_to_disk(self) -> None:
        """Serialize memory index structures and write atomically to disk."""
        # Ensure parent directory exists
        parent_dir = os.path.dirname(self._filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
            self._apply_secure_permissions(parent_dir, is_dir=True)

        # Build payload dicts
        candidates_json = {
            c_id: {
                "id": c.id,
                "name": c.name,
                "sector_zone": c.sector_zone,
                "profession_code": c.profession_code,
                "registered_at": c.registered_at,
                "status": c.status
            }
            for c_id, c in self._candidates.items()
        }

        vacancies_json = {
            v_id: {
                "id": v.id,
                "title": v.title,
                "profession_code": v.profession_code,
                "sector_zone": v.sector_zone,
                "capacity": v.capacity,
                "created_at": v.created_at,
                "expires_at": v.expires_at,
                "placed_candidate_ids": list(v.placed_candidate_ids)
            }
            for v_id, v in self._vacancies.items()
        }

        queues_json = {
            q_code: {
                "profession_code": q.profession_code,
                "candidate_ids": list(q.candidate_ids)
            }
            for q_code, q in self._queues.items()
        }

        payload = {
            "metadata": {
                "app_id": "filavaga-sine-local",
                "schema_version": "1.0"
            },
            "candidates": candidates_json,
            "vacancies": vacancies_json,
            "queues": queues_json
        }

        tmp_path = self._filepath + ".tmp"
        bak_path = self._filepath + ".bak"

        try:
            logger.debug("Writing temporary snapshot state to %s.", tmp_path)
            # 1. Write to temporary file first
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            # Apply secure permissions to temporary file
            self._apply_secure_permissions(tmp_path, is_dir=False)

            # 2. Backup the old active file if it exists
            if os.path.exists(self._filepath):
                logger.debug("Backing up active snapshot file to %s.", bak_path)
                shutil.copy2(self._filepath, bak_path)
                self._apply_secure_permissions(bak_path, is_dir=False)

            # 3. Perform OS atomic replace (rename staging to active)
            os.replace(tmp_path, self._filepath)
            self._apply_secure_permissions(self._filepath, is_dir=False)
            logger.info("Successfully saved state snapshot atomically to %s.", self._filepath)
        except Exception as e:
            logger.error("Failed to save state snapshot to disk. Error: %s", e)
            raise


class JsonUnitOfWork(IUnitOfWork):
    """
    Concrete implementation of Unit of Work for Json persistence.
    
    Guarantees that state changes are kept in memory and only written
    to disk upon successful completion and explicit commit().
    """

    def __init__(self, repository: AtomicJsonRepository):
        self._repository = repository
        self._committed = False
        self._snapshot = None

    def __enter__(self) -> 'JsonUnitOfWork':
        self._repository._lock.acquire()
        # Take deepcopy snapshot of caches
        self._snapshot = (
            copy.deepcopy(self._repository._candidates),
            copy.deepcopy(self._repository._vacancies),
            copy.deepcopy(self._repository._queues)
        )
        self._repository._in_transaction = True
        self._committed = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is not None or not self._committed:
                self.rollback()
        finally:
            self._repository._in_transaction = False
            self._snapshot = None
            self._repository._lock.release()

    def commit(self) -> None:
        self._repository._save_state_to_disk()
        self._committed = True

    def rollback(self) -> None:
        if self._snapshot:
            self._repository._candidates = self._snapshot[0]
            self._repository._vacancies = self._snapshot[1]
            self._repository._queues = self._snapshot[2]

    @property
    def repository(self) -> IStateRepository:
        return self._repository

