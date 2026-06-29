"""
AnalyticsService class implementation.

Coordinates anonymized regional telemetry and placement metric reporting.

Author: Kalyel N. Laurindo / Software Engineer
"""

import csv
import os
import logging
import datetime as dt
from filavaga.application.ports.inbound import IExportStatsUseCase
from filavaga.application.ports.outbound import IClock, IUnitOfWork

logger = logging.getLogger("filavaga")


class AnalyticsService(IExportStatsUseCase):
    """
    Service responsible for calculating KPIs (such as waiting times and placement
    fulfillment speed) aggregated by zone and CBO, exported in a PII-free format.
    """

    def __init__(self, uow: IUnitOfWork, clock: IClock):
        self._uow = uow
        self._clock = clock

    def export_stats(self, output_path: str) -> None:
        """
        Consolidate metrics and write CSV file atomically.
        """
        logger.info("Starting anonymized placement statistics calculations.")
        current_time = self._clock.now()

        # Load active candidates and vacancies state
        with self._uow:
            candidates = list(self._uow.repository.get_all_candidates().values())
            vacancies = list(self._uow.repository.get_all_vacancies().values())

        # Determine all unique combinations of (sector_zone, profession_code)
        groups = set()
        for cand in candidates:
            groups.add((cand.sector_zone, cand.profession_code))
        for vac in vacancies:
            groups.add((vac.sector_zone, vac.profession_code))

        # Atomic write file path setup
        tmp_path = output_path + ".tmp"
        parent_dir = os.path.dirname(output_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        try:
            with open(tmp_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Headings
                writer.writerow([
                    "Sector_Zone",
                    "CBO_Code",
                    "Total_Candidates",
                    "Placed_Candidates",
                    "Placement_Rate",
                    "Average_Wait_Time_Seconds",
                    "Average_Fulfillment_Time_Seconds"
                ])

                for zone, cbo in sorted(groups):
                    # Filter elements belonging to this category
                    group_candidates = [c for c in candidates if c.sector_zone == zone and c.profession_code == cbo]
                    group_vacancies = [v for v in vacancies if v.sector_zone == zone and v.profession_code == cbo]

                    total_cand = len(group_candidates)
                    placed_cand = sum(1 for c in group_candidates if c.status == "PLACED")

                    # Calculate placement rate safely
                    placement_rate = 0.0
                    if total_cand > 0:
                        placement_rate = placed_cand / total_cand

                    # Calculate wait times
                    wait_times = []
                    for cand in group_candidates:
                        try:
                            t_cand = dt.datetime.fromisoformat(cand.registered_at.replace("Z", "+00:00"))
                        except Exception:
                            logger.warning("Skipping wait calculation for candidate '%s' due to invalid timestamp.", cand.id)
                            continue

                        if cand.status == "PLACED":
                            # Find corresponding vacancy placement was associated with
                            matching_vac = None
                            for vac in group_vacancies:
                                if cand.id in vac.placed_candidate_ids:
                                    matching_vac = vac
                                    break

                            if matching_vac:
                                try:
                                    t_vac = dt.datetime.fromisoformat(matching_vac.created_at.replace("Z", "+00:00"))
                                    wait_sec = max(0.0, (t_vac - t_cand).total_seconds())
                                    wait_times.append(wait_sec)
                                except Exception:
                                    wait_times.append(0.0)
                            else:
                                wait_times.append(0.0)
                        else:
                            # Candidate is active (PENDING or CONTACTED), waiting duration is compared against clock
                            wait_sec = max(0.0, (current_time - t_cand).total_seconds())
                            wait_times.append(wait_sec)

                    avg_wait_time = 0.0
                    if wait_times:
                        avg_wait_time = sum(wait_times) / len(wait_times)

                    # Calculate vacancy fulfillment speeds
                    fulfillment_speeds = []
                    for vac in group_vacancies:
                        try:
                            t_vac = dt.datetime.fromisoformat(vac.created_at.replace("Z", "+00:00"))
                        except Exception:
                            logger.warning("Skipping speed calculation for vacancy '%s' due to invalid timestamp.", vac.id)
                            continue

                        for c_id in vac.placed_candidate_ids:
                            cand_obj = None
                            for c in group_candidates:
                                if c.id == c_id:
                                    cand_obj = c
                                    break
                            
                            # Fallback lookups across entire candidate database
                            if not cand_obj:
                                for c in candidates:
                                    if c.id == c_id:
                                        cand_obj = c
                                        break

                            if cand_obj:
                                try:
                                    t_cand = dt.datetime.fromisoformat(cand_obj.registered_at.replace("Z", "+00:00"))
                                    ful_sec = max(0.0, (t_cand - t_vac).total_seconds())
                                    fulfillment_speeds.append(ful_sec)
                                except Exception:
                                    fulfillment_speeds.append(0.0)
                            else:
                                fulfillment_speeds.append(0.0)

                    avg_fulfillment_speed = 0.0
                    if fulfillment_speeds:
                        avg_fulfillment_speed = sum(fulfillment_speeds) / len(fulfillment_speeds)

                    # Export record
                    writer.writerow([
                        zone,
                        cbo,
                        total_cand,
                        placed_cand,
                        placement_rate,
                        avg_wait_time,
                        avg_fulfillment_speed
                    ])

            # Swap staging file
            os.replace(tmp_path, output_path)
            logger.info("Successfully exported anonymized regional placement KPIs to '%s'.", output_path)

        except Exception as e:
            logger.error("Failed to execute CSV analytics export: %s", e)
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            raise
