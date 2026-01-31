"""Mock odds source for testing the system without real scrapers.

This simulates what a real scraper would return. Use this to test
the entire pipeline before implementing real Playwright scrapers.
"""
from typing import List
import random
from adapters.sources.odds_source import OddsSource
from core.models import Outcome


class MockOddsSource(OddsSource):
    """Mock odds source that generates realistic (sometimes arbitrage) odds."""

    def __init__(self, bookmaker_name: str, has_arbitrage_bias: bool = False):
        """Initialize mock source.

        Args:
            bookmaker_name: Name of the bookmaker to simulate
            has_arbitrage_bias: If True, occasionally generate arb-friendly odds
        """
        self._bookmaker_name = bookmaker_name
        self._has_arbitrage_bias = has_arbitrage_bias

    @property
    def bookmaker_name(self) -> str:
        return self._bookmaker_name

    async def fetch_odds(self, event_id: str) -> List[Outcome]:
        """Generate mock odds for an event.

        Args:
            event_id: Event identifier

        Returns:
            List of outcomes with simulated odds
        """
        # Simulate some processing time
        import asyncio
        await asyncio.sleep(0.1)

        # Generate realistic odds
        if self._has_arbitrage_bias and random.random() < 0.3:
            # 30% chance of generating arbitrage-friendly odds
            return self._generate_arb_friendly_odds(event_id)
        else:
            return self._generate_normal_odds(event_id)

    def _generate_normal_odds(self, event_id: str) -> List[Outcome]:
        """Generate normal (non-arbitrage) odds."""
        # Typical odds sum to S > 1.0 (bookmaker margin)
        base_home = random.uniform(1.8, 3.0)
        base_draw = random.uniform(2.8, 4.0)
        base_away = random.uniform(2.0, 5.0)

        # Add bookmaker margin (lower odds)
        margin = random.uniform(0.05, 0.15)
        home_odds = round(base_home * (1 - margin), 2)
        draw_odds = round(base_draw * (1 - margin), 2)
        away_odds = round(base_away * (1 - margin), 2)

        return [
            Outcome(self.bookmaker_name, home_odds, "Home Win"),
            Outcome(self.bookmaker_name, draw_odds, "Draw"),
            Outcome(self.bookmaker_name, away_odds, "Away Win"),
        ]

    def _generate_arb_friendly_odds(self, event_id: str) -> List[Outcome]:
        """Generate odds that might create arbitrage with other bookmakers."""
        # One outcome has unusually high odds
        outcomes = []

        if random.random() < 0.33:
            # High home odds
            outcomes = [
                Outcome(self.bookmaker_name, random.uniform(2.3, 2.8), "Home Win"),
                Outcome(self.bookmaker_name, random.uniform(3.0, 3.5), "Draw"),
                Outcome(self.bookmaker_name, random.uniform(3.5, 4.5), "Away Win"),
            ]
        elif random.random() < 0.66:
            # High draw odds
            outcomes = [
                Outcome(self.bookmaker_name, random.uniform(2.0, 2.5), "Home Win"),
                Outcome(self.bookmaker_name, random.uniform(4.0, 5.0), "Draw"),
                Outcome(self.bookmaker_name, random.uniform(3.0, 4.0), "Away Win"),
            ]
        else:
            # High away odds
            outcomes = [
                Outcome(self.bookmaker_name, random.uniform(2.0, 2.5), "Home Win"),
                Outcome(self.bookmaker_name, random.uniform(3.0, 3.5), "Draw"),
                Outcome(self.bookmaker_name, random.uniform(4.5, 6.0), "Away Win"),
            ]

        # Round to 2 decimal places
        for outcome in outcomes:
            outcome.odds = round(outcome.odds, 2)

        return outcomes

    async def get_available_events(self) -> List[dict]:
        """Return mock list of available events."""
        return [
            {"id": "ajax-psv", "name": "Ajax vs PSV", "sport": "Football"},
            {"id": "feyenoord-az", "name": "Feyenoord vs AZ", "sport": "Football"},
            {"id": "utrecht-twente", "name": "Utrecht vs Twente", "sport": "Football"},
        ]
