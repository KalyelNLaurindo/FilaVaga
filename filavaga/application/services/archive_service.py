"""
ArchiveService class implementation.

Coordinates historical candidate records archiving use cases.

Author: Kalyel N. Laurindo / Software Engineer
"""

import datetime as dt
import logging
from filavaga.application.ports.inbound import IArchiveCandidatesUseCase
from filavaga.application.ports.outbound import IClock, IUnitOfWork
from filavaga.core.entities import Candidate

logger = logging.getLogger("filavaga")


class ArchiveService(IArchiveCandidatesUseCase):
    """
    Service responsible for moving candidates with final statuses (PLACED/REJECTED)
    older than a threshold from active to historical storage.
    """

    def __init__(self, uow: IUnitOfWork, clock: IClock):
        self._uow = uow
        self._clock = clock

    def archive_candidates(self, days: int) -> int:
        """
        Filter old PLACED/REJECTED candidates, append them to archive,
        remove from active DB and queues.
        """
        current_time = self._clock.now()
        cutoff_date = current_time - dt.timedelta(days=days)
        logger.info("Starting historical archiving. Days threshold: %d. Cutoff date: %s", days, cutoff_date.isoformat())

        to_archive = []

        with self._uow:
            all_candidates = self._uow.repository.get_all_candidates()
            for cand in all_candidates.values():
                if cand.status in ("PLACED", "REJECTED"):
                    try:
                        cand_time = dt.datetime.fromisoformat(cand.registered_at.replace("Z", "+00:00"))
                        # Ensure timezone alignment: clock.now() is timezone-aware, so cand_time is too.
                        if cand_time < cutoff_date:
                            to_archive.append(cand)
                    except Exception as e:
                        logger.warning("Failed to parse registration timestamp for candidate '%s': %s", cand.id, e)

            if to_archive:
                # Append to archive repository
                if hasattr(self._uow.repository, "save_archived_candidates"):
                    self._uow.repository.save_archived_candidates(to_archive)
                else:
                    logger.warning("Repository does not support save_archived_candidates operation.")
                    return 0

                # Delete from active repository and update professional queues
                for cand in to_archive:
                    self._uow.repository.delete_candidate(cand.id)
                    
                    # Update queue to prevent broken references
                    queue = self._uow.repository.get_queue(cand.profession_code)
                    if queue:
                        queue.remove_candidate(cand.id)
                        self._uow.repository.save_queue(queue)

                self._uow.commit()
                logger.info("Ingested %d candidates into historical archive file successfully.", len(to_archive))

        return len(to_archive)
