"""
QueueManager application service.

Coordinates candidate admission flows, queue updates, and state persistence.

Author: Kalyel N. Laurindo / Software Engineer
"""

import uuid
from filavaga.application.ports.inbound import IRegisterCandidateUseCase
from filavaga.application.ports.outbound import IClock, IStateRepository
from filavaga.core.entities import Candidate, Queue
from filavaga.core.exceptions import FilaVagaDomainError


class QueueManager(IRegisterCandidateUseCase):
    """
    Service responsible for managing candidate queues.
    
    Implements candidate registration and manages their lifecycle within queues.
    """

    def __init__(self, repository: IStateRepository, clock: IClock):
        self._repository = repository
        self._clock = clock

    def register_candidate(
        self, name: str, profession_code: str, sector_zone: str
    ) -> Candidate:
        """
        Validate input parameters, create a Candidate, save to repository,
        and append to the chronological professional FIFO Queue.
        """
        if not name or not name.strip():
            raise FilaVagaDomainError("Candidate name cannot be empty.")
        if not profession_code or not profession_code.strip():
            raise FilaVagaDomainError("Profession CBO code cannot be empty.")
        if not sector_zone or not sector_zone.strip():
            raise FilaVagaDomainError("Sector zone cannot be empty.")

        # Generate a unique candidate ID
        candidate_id = f"c_{uuid.uuid4().hex[:13]}"
        
        # Get ISO format timezone-aware UTC timestamp
        registered_at = self._clock.now().isoformat()

        # Create Candidate entity
        candidate = Candidate(
            id=candidate_id,
            name=name.strip(),
            sector_zone=sector_zone.strip(),
            profession_code=profession_code.strip(),
            registered_at=registered_at
        )

        # Save candidate entity state
        self._repository.save_candidate(candidate)

        # Get or initialize the professional FIFO Queue
        queue = self._repository.get_queue(profession_code)
        if not queue:
            queue = Queue(profession_code=profession_code)

        # Retrieve all active candidates to allow chronological sorting inside the queue aggregate
        candidates_map = self._repository.get_all_candidates()

        # Add the candidate and let the aggregate handle FIFO chronological order
        queue.add_candidate(candidate, candidates_map)

        # Save updated queue state
        self._repository.save_queue(queue)

        return candidate
