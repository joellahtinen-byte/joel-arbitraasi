"""Port interface for odds data sources.

This defines the contract that all odds sources (APIs, scrapers) must implement.
This is a key part of the hexagonal architecture - the core depends on this
interface, not on concrete implementations.
"""
from abc import ABC, abstractmethod
from typing import List
from core.models import Outcome


class OddsSource(ABC):
    """Abstract interface for fetching odds data.

    Implementations can use APIs, web scraping, or any other method.
    The core domain logic doesn't care about the implementation details.
    """

    @abstractmethod
    async def fetch_odds(self, event_id: str) -> List[Outcome]:
        """Fetch odds for a specific event.

        Args:
            event_id: Unique identifier for the sporting event

        Returns:
            List of outcomes with odds from this bookmaker

        Raises:
            OddsSourceError: If fetching fails
        """
        pass

    @abstractmethod
    async def get_available_events(self) -> List[dict]:
        """Get list of available events from this source.

        Returns:
            List of event dictionaries with keys: id, name, sport, start_time
        """
        pass

    @property
    @abstractmethod
    def bookmaker_name(self) -> str:
        """Return the name of the bookmaker."""
        pass


class OddsSourceError(Exception):
    """Raised when odds fetching fails."""
    pass
