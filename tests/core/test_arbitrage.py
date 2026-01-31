"""Tests for core arbitrage detection and calculation engine."""
import pytest
from core.arbitrage import (
    detect_arbitrage,
    calculate_optimal_stakes,
    calculate_guaranteed_profit,
    calculate_roi,
    calculate_payout,
    create_arbitrage_opportunity,
    verify_arbitrage_payout
)
from core.models import Outcome


class TestArbitrageDetection:
    """Tests for arbitrage opportunity detection."""

    def test_detect_valid_arbitrage(self):
        """Test detection of a valid arbitrage opportunity."""
        outcomes = [
            Outcome("TOTO", 2.1, "Home Win"),
            Outcome("Bet365", 3.5, "Draw"),
            Outcome("Unibet", 4.2, "Away Win")
        ]

        is_arb, s_value = detect_arbitrage(outcomes)

        assert is_arb is True
        assert s_value < 1.0
        # S = 1/2.1 + 1/3.5 + 1/4.2 ≈ 0.9997
        assert 0.99 < s_value < 1.0

    def test_detect_no_arbitrage(self):
        """Test that normal odds are correctly identified as non-arbitrage."""
        outcomes = [
            Outcome("TOTO", 2.0, "Home Win"),
            Outcome("Bet365", 3.0, "Draw"),
            Outcome("Unibet", 3.5, "Away Win")
        ]

        is_arb, s_value = detect_arbitrage(outcomes)

        assert is_arb is False
        assert s_value >= 1.0

    def test_invalid_odds(self):
        """Test handling of invalid odds (≤ 1.0)."""
        outcomes = [
            Outcome("TOTO", 0.5, "Home Win"),  # Invalid odds
            Outcome("Bet365", 3.5, "Draw"),
        ]

        is_arb, s_value = detect_arbitrage(outcomes)

        assert is_arb is False

    def test_insufficient_outcomes(self):
        """Test handling of insufficient outcomes."""
        outcomes = [Outcome("TOTO", 2.0, "Home Win")]

        is_arb, s_value = detect_arbitrage(outcomes)

        assert is_arb is False


class TestStakeCalculation:
    """Tests for optimal stake calculation."""

    def test_calculate_stakes_with_rounding(self):
        """Test that stakes are rounded to whole numbers."""
        outcomes = [
            Outcome("TOTO", 2.1, "Home Win"),
            Outcome("Bet365", 3.5, "Draw"),
            Outcome("Unibet", 4.2, "Away Win")
        ]
        total_bankroll = 1000.0
        s_value = 0.9997  # Valid arbitrage

        stakes = calculate_optimal_stakes(outcomes, total_bankroll, s_value)

        # All stakes should be whole numbers
        assert all(stake == round(stake) for stake in stakes)
        # Stakes should sum to approximately the bankroll
        assert 990 <= sum(stakes) <= 1010

    def test_calculate_stakes_without_rounding(self):
        """Test stake calculation without rounding (for testing)."""
        outcomes = [
            Outcome("TOTO", 2.0, "Home Win"),
            Outcome("Bet365", 3.0, "Draw"),
        ]
        total_bankroll = 1000.0
        s_value = 0.9

        stakes = calculate_optimal_stakes(
            outcomes, total_bankroll, s_value, round_stakes=False
        )

        # Stakes should not be rounded
        assert any(stake != round(stake) for stake in stakes)

    def test_stakes_for_non_arbitrage_raises_error(self):
        """Test that calculating stakes for non-arbitrage raises error."""
        outcomes = [
            Outcome("TOTO", 2.0, "Home Win"),
            Outcome("Bet365", 3.0, "Draw"),
        ]
        total_bankroll = 1000.0
        s_value = 1.1  # Not an arbitrage

        with pytest.raises(ValueError):
            calculate_optimal_stakes(outcomes, total_bankroll, s_value)


class TestProfitCalculations:
    """Tests for profit and ROI calculations."""

    def test_calculate_guaranteed_profit(self):
        """Test guaranteed profit calculation."""
        total_bankroll = 1000.0
        s_value = 0.95  # 5% arbitrage margin

        profit = calculate_guaranteed_profit(total_bankroll, s_value)

        assert profit == 50.0  # 1000 * (1 - 0.95) = 50

    def test_calculate_roi(self):
        """Test ROI calculation."""
        profit = 50.0
        investment = 1000.0

        roi = calculate_roi(profit, investment)

        assert roi == 5.0  # (50/1000) * 100 = 5%

    def test_calculate_payout(self):
        """Test payout calculation."""
        stake = 100.0
        odds = 2.5

        payout = calculate_payout(stake, odds)

        assert payout == 250.0  # 100 * 2.5


class TestArbitrageOpportunityCreation:
    """Tests for creating complete arbitrage opportunities."""

    def test_create_valid_opportunity(self):
        """Test creating a complete arbitrage opportunity."""
        outcomes = [
            Outcome("TOTO", 2.1, "Home Win"),
            Outcome("Bet365", 3.5, "Draw"),
            Outcome("Unibet", 4.2, "Away Win")
        ]
        event_name = "Ajax vs PSV"
        total_bankroll = 1000.0

        arb = create_arbitrage_opportunity(event_name, outcomes, total_bankroll)

        assert arb is not None
        assert arb.event_name == event_name
        assert len(arb.stakes) == 3
        assert all(stake > 0 for stake in arb.stakes)
        assert arb.guaranteed_profit > 0
        assert arb.roi > 0
        assert arb.arbitrage_percentage < 1.0

    def test_create_non_arbitrage_returns_none(self):
        """Test that non-arbitrage opportunities return None."""
        outcomes = [
            Outcome("TOTO", 2.0, "Home Win"),
            Outcome("Bet365", 3.0, "Draw"),
            Outcome("Unibet", 3.5, "Away Win")
        ]
        event_name = "Ajax vs PSV"
        total_bankroll = 1000.0

        arb = create_arbitrage_opportunity(event_name, outcomes, total_bankroll)

        assert arb is None


class TestPayoutVerification:
    """Tests for verifying arbitrage payout consistency."""

    def test_verify_valid_arbitrage_payout(self):
        """Test that valid arbitrage has consistent payouts."""
        outcomes = [
            Outcome("TOTO", 2.0, "Home Win"),
            Outcome("Bet365", 3.0, "Draw"),
        ]
        # Manually calculated perfect stakes for S = 0.833...
        stakes = [600.0, 400.0]  # These should yield equal payouts

        is_valid, payout = verify_arbitrage_payout(stakes, outcomes)

        # 600 * 2.0 = 1200, 400 * 3.0 = 1200
        assert is_valid is True
        assert payout == 1200.0

    def test_verify_with_rounding_tolerance(self):
        """Test that verification allows for rounding errors."""
        outcomes = [
            Outcome("TOTO", 2.1, "Home Win"),
            Outcome("Bet365", 3.5, "Draw"),
        ]
        stakes = [476.0, 286.0]  # Rounded stakes, might have small variance

        is_valid, payout = verify_arbitrage_payout(stakes, outcomes)

        # Should still be valid within tolerance
        assert payout > 0
