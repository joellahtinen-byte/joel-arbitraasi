"""Domain models for arbitrage betting.

These models are pure data structures with no external dependencies.
"""
from dataclasses import dataclass
from typing import List
from decimal import Decimal


@dataclass
class Outcome:
    """Represents a single betting outcome."""
    bookmaker: str
    odds: float
    market: str  # e.g., "Home Win", "Draw", "Away Win"


@dataclass
class ArbitrageOpportunity:
    """Represents a detected arbitrage opportunity."""
    event_name: str
    outcomes: List[Outcome]
    arbitrage_percentage: float  # S value from sum(1/odds)
    profit_margin: float  # Percentage profit (1 - S) * 100
    total_bankroll: float
    stakes: List[float]  # Calculated optimal stakes (rounded)
    guaranteed_profit: float
    roi: float  # Return on investment percentage


@dataclass
class BetPlacement:
    """Represents a bet to be placed."""
    bookmaker: str
    event_name: str
    market: str
    odds: float
    stake: float  # Always rounded to whole number
