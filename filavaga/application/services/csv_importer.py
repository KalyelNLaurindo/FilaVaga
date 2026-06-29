"""
CSVImportService class implementation.

Coordinates loading, validating, and persisting candidates and vacancies
imported from legacy CSV formats.

Author: Kalyel N. Laurindo / Software Engineer
"""

import csv
import sys
import re
import uuid
import datetime as dt
import logging
from filavaga.application.ports.inbound import IImportCSVUseCase
from filavaga.application.ports.outbound import IClock, IUnitOfWork
from filavaga.core.entities import Candidate, Vacancy, Queue
from filavaga.core.exceptions import FilaVagaDomainError

logger = logging.getLogger("filavaga")


def _clean_header(h: str) -> str:
    """Normalize headers: lower case, strip, replace accents, replace spaces/dashes with underscores."""
    h = h.strip().lower()
    h = h.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    h = h.replace("ç", "c").replace("ã", "a").replace("õ", "o")
    h = re.sub(r"[\s-]+", "_", h)
    return h


def _align_cbo(cbo: str) -> str:
    """Format CBO codes containing 6 digits without a dash into the standard XXXX-XX format."""
    cbo = cbo.strip()
    if re.match(r"^\d{6}$", cbo):
        return f"{cbo[:4]}-{cbo[4:]}"
    return cbo


def _validate_cbo(cbo: str) -> bool:
    """Validate standard XXXX-XX CBO code structure."""
    return bool(re.match(r"^\d{4}-\d{2}$", cbo))


def _align_zone(zone: str) -> str:
    """Format zone tags to uppercase."""
    return zone.strip().upper()


def _validate_zone(zone: str) -> bool:
    """Validate that the zone is part of SINE divisions."""
    return zone in {"SUL", "NORTE", "LESTE", "OESTE", "CENTRO"}


def _align_timestamp(ts_str: str, default_ts: str) -> str:
    """Ensure timestamp format conforms to ISO-8601 UTC representation."""
    if not ts_str or not ts_str.strip():
        return default_ts
    ts_str = ts_str.strip()
    try:
        # Check standard ISO parsing structure
        dt_val = dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        # Format uniformly with Z suffix
        return dt_val.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        raise ValueError(f"Invalid timestamp: {ts_str}")


class CSVImportService(IImportCSVUseCase):
    """
    Coordinates raw CSV records validation, sanitization, and database ingestion.
    """

    def __init__(self, uow: IUnitOfWork, clock: IClock):
        self._uow = uow
        self._clock = clock

    def import_csv(self, filepath: str) -> dict[str, int]:
        """
        Ingest records from CSV file path, writing skipped row validation warnings to stderr.
        """
        logger.info("Starting CSV data import from '%s'.", filepath)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                try:
                    headers = next(reader)
                except StopIteration:
                    raise FilaVagaDomainError("CSV file is empty.")
                
                rows = list(reader)
        except Exception as e:
            raise FilaVagaDomainError(f"Failed to read CSV file: {e}")

        headers_cleaned = [_clean_header(h) for h in headers]

        # Define candidate synonyms mappings
        candidate_mapping = {
            "name": ["name", "nome", "candidate_name", "candidato", "nome_do_candidato"],
            "cbo": ["cbo", "cbo_code", "profession_code", "cbo_da_profissao", "codigo_cbo", "cbo_code"],
            "zone": ["zone", "zona", "sector_zone", "zona_de_preferencia", "zona_preferencia", "zona_preferência", "zona_preferencia"],
            "id": ["id", "candidate_id", "identificacao", "identificação"],
            "registered_at": ["registered_at", "registration_date", "registrado_em", "data_registro", "data_do_registro", "registration_date"]
        }

        # Define vacancy synonyms mappings
        vacancy_mapping = {
            "title": ["title", "titulo", "título", "vacancy_title"],
            "cbo": ["cbo", "cbo_code", "profession_code", "codigo_cbo"],
            "zone": ["zone", "zona", "sector_zone"],
            "capacity": ["capacity", "capacidade"],
            "id": ["id", "vacancy_id"],
            "created_at": ["created_at", "criado_em", "data_criacao"],
            "expires_at": ["expires_at", "expira_em", "data_expiracao", "data_expira"]
        }

        # Map indices
        cand_indices = {}
        for field, synonyms in candidate_mapping.items():
            for idx, h in enumerate(headers_cleaned):
                if h in synonyms:
                    cand_indices[field] = idx
                    break

        vac_indices = {}
        for field, synonyms in vacancy_mapping.items():
            for idx, h in enumerate(headers_cleaned):
                if h in synonyms:
                    vac_indices[field] = idx
                    break

        is_candidate = "name" in cand_indices
        is_vacancy = "title" in vac_indices and not is_candidate

        if not is_candidate and not is_vacancy:
            raise FilaVagaDomainError("Invalid CSV headers: could not identify candidate or vacancy schema.")

        candidates_imported = 0
        vacancies_imported = 0

        default_now = self._clock.now().isoformat()

        # Row 1 is headers. Data rows start at Row 2.
        for row_idx, row in enumerate(rows, start=2):
            if not row:
                continue

            try:
                if is_candidate:
                    # Parse Candidate fields
                    name_idx = cand_indices.get("name")
                    cbo_idx = cand_indices.get("cbo")
                    zone_idx = cand_indices.get("zone")
                    id_idx = cand_indices.get("id")
                    reg_idx = cand_indices.get("registered_at")

                    if name_idx is None or cbo_idx is None or zone_idx is None:
                        raise ValueError("Missing required fields (Name, CBO, Zone).")

                    if name_idx >= len(row) or cbo_idx >= len(row) or zone_idx >= len(row):
                        raise ValueError("Row length does not match headers size.")

                    raw_name = row[name_idx].strip()
                    raw_cbo = row[cbo_idx].strip()
                    raw_zone = row[zone_idx].strip()

                    if not raw_name:
                        raise ValueError("Candidate name cannot be empty.")

                    aligned_cbo = _align_cbo(raw_cbo)
                    if not _validate_cbo(aligned_cbo):
                        raise ValueError(f"Invalid CBO code format: {raw_cbo}")

                    aligned_zone = _align_zone(raw_zone)
                    if not _validate_zone(aligned_zone):
                        raise ValueError(f"Invalid sector zone: {raw_zone}")

                    cand_id = row[id_idx].strip() if id_idx is not None and id_idx < len(row) and row[id_idx].strip() else f"c_{uuid.uuid4().hex[:13]}"
                    
                    raw_reg = row[reg_idx].strip() if reg_idx is not None and reg_idx < len(row) else ""
                    registered_at = _align_timestamp(raw_reg, default_now)

                    # Instantiate and save Candidate entity
                    candidate = Candidate(
                        id=cand_id,
                        name=raw_name,
                        sector_zone=aligned_zone,
                        profession_code=aligned_cbo,
                        registered_at=registered_at
                    )

                    with self._uow:
                        self._uow.repository.save_candidate(candidate)
                        
                        queue = self._uow.repository.get_queue(aligned_cbo)
                        if not queue:
                            queue = Queue(profession_code=aligned_cbo)
                        
                        queue.add_candidate(candidate.id, candidate.registered_at)
                        self._uow.repository.save_queue(queue)
                        self._uow.commit()

                    candidates_imported += 1

                else:
                    # Parse Vacancy fields
                    title_idx = vac_indices.get("title")
                    cbo_idx = vac_indices.get("cbo")
                    zone_idx = vac_indices.get("zone")
                    cap_idx = vac_indices.get("capacity")
                    id_idx = vac_indices.get("id")
                    created_idx = vac_indices.get("created_at")
                    expires_idx = vac_indices.get("expires_at")

                    if title_idx is None or cbo_idx is None or zone_idx is None or cap_idx is None:
                        raise ValueError("Missing required fields (Title, CBO, Zone, Capacity).")

                    if title_idx >= len(row) or cbo_idx >= len(row) or zone_idx >= len(row) or cap_idx >= len(row):
                        raise ValueError("Row length does not match headers size.")

                    raw_title = row[title_idx].strip()
                    raw_cbo = row[cbo_idx].strip()
                    raw_zone = row[zone_idx].strip()
                    raw_cap = row[cap_idx].strip()

                    if not raw_title:
                        raise ValueError("Vacancy title cannot be empty.")

                    aligned_cbo = _align_cbo(raw_cbo)
                    if not _validate_cbo(aligned_cbo):
                        raise ValueError(f"Invalid CBO code format: {raw_cbo}")

                    aligned_zone = _align_zone(raw_zone)
                    if not _validate_zone(aligned_zone):
                        raise ValueError(f"Invalid sector zone: {raw_zone}")

                    try:
                        capacity = int(raw_cap)
                        if capacity <= 0:
                            raise ValueError()
                    except ValueError:
                        raise ValueError(f"Capacity must be a positive integer: {raw_cap}")

                    vac_id = row[id_idx].strip() if id_idx is not None and id_idx < len(row) and row[id_idx].strip() else f"v_{uuid.uuid4().hex[:13]}"

                    raw_created = row[created_idx].strip() if created_idx is not None and created_idx < len(row) else ""
                    created_at = _align_timestamp(raw_created, default_now)

                    # Default TTL: expires 24 hours after created_at
                    dt_created = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    dt_default_expires = dt_created + dt.timedelta(hours=24)
                    default_expires_str = dt_default_expires.strftime("%Y-%m-%dT%H:%M:%SZ")

                    raw_expires = row[expires_idx].strip() if expires_idx is not None and expires_idx < len(row) else ""
                    expires_at = _align_timestamp(raw_expires, default_expires_str)

                    # Instantiate and save Vacancy entity
                    vacancy = Vacancy(
                        id=vac_id,
                        title=raw_title,
                        profession_code=aligned_cbo,
                        sector_zone=aligned_zone,
                        capacity=capacity,
                        created_at=created_at,
                        expires_at=expires_at
                    )

                    with self._uow:
                        self._uow.repository.save_vacancy(vacancy)
                        self._uow.commit()

                    vacancies_imported += 1

            except Exception as e:
                # Write warnings to sys.stderr instead of failing silently
                print(f"Row {row_idx} Validation Error: {e}", file=sys.stderr)
                logger.warning("Skipping row %d due to validation error: %s", row_idx, e)

        return {"candidates": candidates_imported, "vacancies": vacancies_imported}
