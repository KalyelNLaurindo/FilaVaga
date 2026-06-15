"""
Concrete timezone-safe SystemClock adapter for FilaVaga engine.

Implements the outbound IClock port interface using Python's standard datetime module.
Allows in-memory testing override to mock precise clock values.

Author: Kalyel N. Laurindo / Software Engineer
"""

from datetime import datetime, timezone
from filavaga.application.ports.outbound import IClock


class SystemClock(IClock):
    """
    Timezone-safe SystemClock adapter.
    
    Provides accurate high-precision system UTC time or a mock value
    when configured for isolated unit/integration tests.
    """

    def __init__(self, override_time: datetime | None = None):
        """
        Initialize the system clock adapter.
        
        Args:
            override_time (datetime, optional): A specific timezone-aware datetime value
                to override the system clock for testing purposes.
        """
        self._override_time = override_time

    def now(self) -> datetime:
        """
        Return the current date and time as a timezone-aware UTC datetime.
        
        If an override_time is set, it will be returned instead of the actual system time.
        
        Returns:
            datetime: Timezone-aware UTC datetime.
        """
        if self._override_time is not None:
            return self._override_time
        return datetime.now(timezone.utc)
