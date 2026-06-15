"""
MatchEngine application service.

Coordinates the vacancy matching logic by selecting the highest priority candidate
from the FIFO queue that matches the vacancy criteria (CBO, zone, and availability).

Author: Kalyel N. Laurindo / Software Engineer
"""

import logging
from filavaga.application.ports.inbound import IMatchVacancyUseCase
from filavaga.application.ports.outbound import IClock, IStateRepository
from filavaga.core.entities import Candidate
from filavaga.core.exceptions import EntityNotFoundError

logger = logging.getLogger("filavaga")


class MatchEngine(IMatchVacancyUseCase):
    """
    Service responsible for matching candidates to vacancies.
    
    Implements vacancy matching heuristics and processes candidate status transitions.
    """

    def __init__(self, repository: IStateRepository, clock: IClock):
        self._repository = repository
        self._clock = clock

    def match_vacancy(self, vacancy_id: str) -> Candidate | None:
        """
        Evaluate vacancy, retrieve the matching FIFO candidate, transition their status,
        and update state storage.
        """
        logger.info("Evaluating match for vacancy ID '%s'.", vacancy_id)
        # Retrieve vacancy
        vacancy = self._repository.get_vacancy(vacancy_id)
        if not vacancy:
            logger.warning("Vacancy '%s' not found.", vacancy_id)
            raise EntityNotFoundError(f"Vacancy {vacancy_id} not found.")

        # Invariant checks: dynamic lazy-evaluated TTL and capacity verification
        # These methods raise EntityExpiredError / CapacityLimitExceededError if violated
        current_time = self._clock.now()
        
        # Trigger validations in Vacancy entity before processing queue
        if vacancy.is_expired(current_time):
            # Explicit call to trigger exception raising logic
            vacancy.place_candidate("validation_trigger_dummy", current_time)
        if vacancy.is_full():
            # Explicit call to trigger exception raising logic
            vacancy.place_candidate("validation_trigger_dummy", current_time)

        # Retrieve the queue for the vacancy's profession CBO code
        queue = self._repository.get_queue(vacancy.profession_code)
        if not queue:
            logger.warning("No FIFO queue found for profession CBO '%s'.", vacancy.profession_code)
            return None

        # Search candidates in FIFO queue priority sequence (already sorted)
        for c_id in queue.candidate_ids:
            candidate = self._repository.get_candidate(c_id)
            if not candidate:
                continue

            # Filtering heuristics: must be PENDING and zone preference must match vacancy zone
            if candidate.status == "PENDING" and candidate.sector_zone == vacancy.sector_zone:
                # 1. State machine transition Candidate -> CONTACTED
                candidate.transition_to("CONTACTED")
                self._repository.save_candidate(candidate)

                # 2. Place candidate in vacancy
                vacancy.place_candidate(candidate.id, current_time)
                self._repository.save_vacancy(vacancy)

                logger.info("Successfully matched candidate '%s' (ID: %s) to vacancy '%s'.", candidate.name, candidate.id, vacancy_id)
                return candidate

        logger.warning("No pending candidate in FIFO queue matching requirements for vacancy '%s'.", vacancy_id)
        return None
