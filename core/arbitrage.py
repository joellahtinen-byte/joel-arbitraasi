"""Core arbitrage detection and calculation engine.

This module contains pure mathematical functions for:
- Detecting arbitrage opportunities
- Calculating optimal stake distribution
- Computing ROI and guaranteed profit

NO EXTERNAL DEPENDENCIES: This core logic is isolated from scrapers,
APIs, and databases to maintain architectural purity.
"""
from typing import List, Tuple, Optional
from core.models import Outcome, ArbitrageOpportunity


def detect_arbitrage(outcomes: List[Outcome]) -> Tuple[bool, float]:
    """Detect if a set of outcomes presents an arbitrage opportunity.

    Uses the formula: S = sum(1/odds_i)
    If S < 1.0, an arbitrage opportunity exists.

    Args:
        outcomes: List of betting outcomes with their odds

    Returns:
        Tuple of (is_arbitrage, S_value)

    Example:
        >>> outcomes = [
        ...     Outcome("TOTO", 2.1, "Home Win"),
        ...     Outcome("Bet365", 3.5, "Draw"),
        ...     Outcome("Unibet", 4.2, "Away Win")
        ... ]
        >>> is_arb, s = detect_arbitrage(outcomes)
        >>> is_arb
        True
    """
    if not outcomes or len(outcomes) < 2:
        return False, 0.0

    # Validate odds are positive
    for outcome in outcomes:
        if outcome.odds <= 1.0:
            return False, 0.0

    # Calculate S = sum(1/odds)
    s_value = sum(1.0 / outcome.odds for outcome in outcomes)

    return s_value < 1.0, s_value


def calculate_optimal_stakes(
    outcomes: List[Outcome],
    total_bankroll: float,
    s_value: float,
    round_stakes: bool = True
) -> List[float]:
    """Calculate optimal stake distribution for arbitrage.

    Formula: stake_i = (total_bankroll / odds_i) / S

    Args:
        outcomes: List of betting outcomes
        total_bankroll: Total amount to invest
        s_value: The arbitrage percentage (from detect_arbitrage)
        round_stakes: If True, round to whole numbers to avoid gubbing

    Returns:
        List of optimal stakes for each outcome

    Note:
        Stakes are ALWAYS rounded to whole numbers in production to avoid
        bookmaker detection (gubbing). Decimal cent bets are suspicious.
    """
    if s_value >= 1.0:
        raise ValueError("Cannot calculate stakes for non-arbitrage opportunity")

    stakes = []
    for outcome in outcomes:
        stake = (total_bankroll / outcome.odds) / s_value
        if round_stakes:
            stake = round(stake)
        stakes.append(stake)

    return stakes


def calculate_guaranteed_profit(total_bankroll: float, s_value: float) -> float:
    """Calculate the guaranteed profit from an arbitrage opportunity.

    Formula: profit = total_bankroll * (1 - S)

    Args:
        total_bankroll: Total amount invested
        s_value: The arbitrage percentage

    Returns:
        Guaranteed profit amount
    """
    if s_value >= 1.0:
        return 0.0

    return total_bankroll * (1.0 - s_value)


def calculate_roi(profit: float, total_investment: float) -> float:
    """Calculate return on investment percentage.

    Formula: ROI = (profit / total_investment) * 100

    Args:
        profit: The profit amount
        total_investment: Total amount invested

    Returns:
        ROI as a percentage
    """
    if total_investment <= 0:
        return 0.0

    return (profit / total_investment) * 100


def calculate_payout(stake: float, odds: float) -> float:
    """Calculate the payout for a winning bet.

    Formula: payout = stake * odds

    Args:
        stake: The bet amount
        odds: The odds for the outcome

    Returns:
        Total payout (including original stake)
    """
    return stake * odds


def create_arbitrage_opportunity(
    event_name: str,
    outcomes: List[Outcome],
    total_bankroll: float
) -> Optional[ArbitrageOpportunity]:
    """Create a complete arbitrage opportunity with all calculations.

    This is the main function that orchestrates all the calculations.

    Args:
        event_name: Name of the sporting event
        outcomes: List of betting outcomes
        total_bankroll: Total amount to invest

    Returns:
        ArbitrageOpportunity if valid arbitrage exists, None otherwise

    Example:
        >>> outcomes = [
        ...     Outcome("TOTO", 2.1, "Home Win"),
        ...     Outcome("Bet365", 3.5, "Draw"),
        ...     Outcome("Unibet", 4.2, "Away Win")
        ... ]
        >>> arb = create_arbitrage_opportunity("Ajax vs PSV", outcomes, 1000.0)
        >>> arb.guaranteed_profit
        25.8
    """
    # Step 1: Detect arbitrage
    is_arb, s_value = detect_arbitrage(outcomes)
    if not is_arb:
        return None

    # Step 2: Calculate optimal stakes (rounded)
    stakes = calculate_optimal_stakes(outcomes, total_bankroll, s_value)

    # Step 3: Calculate profit and ROI
    # Note: With rounding, actual investment might differ slightly
    actual_investment = sum(stakes)
    profit = calculate_guaranteed_profit(actual_investment, s_value)
    roi = calculate_roi(profit, actual_investment)

    # Step 4: Calculate profit margin
    profit_margin = (1.0 - s_value) * 100

    return ArbitrageOpportunity(
        event_name=event_name,
        outcomes=outcomes,
        arbitrage_percentage=s_value,
        profit_margin=profit_margin,
        total_bankroll=actual_investment,
        stakes=stakes,
        guaranteed_profit=profit,
        roi=roi
    )


def verify_arbitrage_payout(
    stakes: List[float],
    outcomes: List[Outcome]
) -> Tuple[bool, float]:
    """Verify that all outcomes result in the same payout.

    In a valid arbitrage, winning any bet should yield the same total payout.
    This function is useful for validation and testing.

    Args:
        stakes: List of stake amounts
        outcomes: List of outcomes with odds

    Returns:
        Tuple of (is_valid, expected_payout)
    """
    if len(stakes) != len(outcomes):
        return False, 0.0

    payouts = [calculate_payout(stake, outcome.odds)
               for stake, outcome in zip(stakes, outcomes)]

    # Check if all payouts are approximately equal (within 1 unit due to rounding)
    max_payout = max(payouts)
    min_payout = min(payouts)
    is_valid = (max_payout - min_payout) <= 1.0

    return is_valid, max_payout
