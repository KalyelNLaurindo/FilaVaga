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
from filavaga.application.ports.outbound import IStateRepository
from filavaga.core.entities import Candidate, Vacancy, Queue


class AtomicJsonRepository(IStateRepository):
    """
    Local JSON file repository for atomic state mutations.
    
    Protects read/write operations using threading.Lock.
    Uses temp staging files and os.replace to prevent file corruption.
    """

    def __init__(self, filepath: str):
        self._filepath = os.path.abspath(filepath)
        self._lock = threading.Lock()
        self._candidates = {}
        self._vacancies = {}
        self._queues = {}
        self._load_state_from_disk()

    def get_candidate(self, candidate_id: str) -> Candidate | None:
        with self._lock:
            return self._candidates.get(candidate_id)

    def save_candidate(self, candidate: Candidate) -> None:
        with self._lock:
            self._candidates[candidate.id] = candidate
            self._save_state_to_disk()

    def get_all_candidates(self) -> dict[str, Candidate]:
        with self._lock:
            return dict(self._candidates)

    def get_vacancy(self, vacancy_id: str) -> Vacancy | None:
        with self._lock:
            return self._vacancies.get(vacancy_id)

    def save_vacancy(self, vacancy: Vacancy) -> None:
        with self._lock:
            self._vacancies[vacancy.id] = vacancy
            self._save_state_to_disk()

    def get_all_vacancies(self) -> dict[str, Vacancy]:
        with self._lock:
            return dict(self._vacancies)

    def get_queue(self, profession_code: str) -> Queue | None:
        with self._lock:
            return self._queues.get(profession_code)

    def save_queue(self, queue: Queue) -> None:
        with self._lock:
            self._queues[queue.profession_code] = queue
            self._save_state_to_disk()

    def _load_state_from_disk(self) -> None:
        """Read snapshot from disk and rebuild domain objects in memory."""
        if not os.path.exists(self._filepath):
            return

        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
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
                self._queues[q_code] = Queue(
                    profession_code=q_val["profession_code"],
                    candidate_ids=q_val.get("candidate_ids", [])
                )
        except Exception:
            # Under resilient guidelines, if the active snapshot is corrupted,
            # we try to restore from .bak
            bak_path = self._filepath + ".bak"
            if os.path.exists(bak_path):
                # Swap and reload
                try:
                    shutil.copy2(bak_path, self._filepath)
                    self._load_state_from_disk()
                except Exception:
                    pass

    def _save_state_to_disk(self) -> None:
        """Serialize memory index structures and write atomically to disk."""
        # Ensure parent directory exists
        parent_dir = os.path.dirname(self._filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

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

        # 1. Write to temporary file first
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        # 2. Backup the old active file if it exists
        if os.path.exists(self._filepath):
            shutil.copy2(self._filepath, bak_path)

        # 3. Perform OS atomic replace (rename staging to active)
        os.replace(tmp_path, self._filepath)
