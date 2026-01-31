"""Example usage of the ArbStream core engine.

This demonstrates how the hexagonal architecture keeps the core logic
independent of external data sources.
"""
import asyncio
from core.arbitrage import create_arbitrage_opportunity
from core.models import Outcome


async def main():
    """Demonstrate arbitrage detection and calculation."""

    print("=" * 60)
    print("ArbStream - Arbitrage Detection Engine Demo")
    print("=" * 60)
    print()

    # Example 1: Valid arbitrage opportunity
    print("Example 1: Valid Arbitrage Opportunity")
    print("-" * 60)

    outcomes = [
        Outcome("TOTO", 2.15, "Ajax Win"),
        Outcome("Bet365", 3.75, "Draw"),
        Outcome("Unibet", 4.50, "PSV Win")
    ]

    arb = create_arbitrage_opportunity(
        event_name="Ajax vs PSV",
        outcomes=outcomes,
        total_bankroll=1000.0
    )

    if arb:
        print(f"✓ Arbitrage detected!")
        print(f"Event: {arb.event_name}")
        print(f"Arbitrage Percentage (S): {arb.arbitrage_percentage:.4f}")
        print(f"Profit Margin: {arb.profit_margin:.2f}%")
        print()
        print("Stake Distribution:")
        for outcome, stake in zip(arb.outcomes, arb.stakes):
            print(f"  {outcome.bookmaker:10s} @ {outcome.odds:.2f} → €{stake:.0f}")
        print()
        print(f"Total Investment: €{arb.total_bankroll:.2f}")
        print(f"Guaranteed Profit: €{arb.guaranteed_profit:.2f}")
        print(f"ROI: {arb.roi:.2f}%")
    else:
        print("✗ No arbitrage opportunity detected")

    print()
    print()

    # Example 2: No arbitrage (normal odds)
    print("Example 2: No Arbitrage (Normal Market)")
    print("-" * 60)

    outcomes_no_arb = [
        Outcome("TOTO", 2.00, "Feyenoord Win"),
        Outcome("Bet365", 3.00, "Draw"),
        Outcome("Unibet", 3.50, "AZ Win")
    ]

    arb_no = create_arbitrage_opportunity(
        event_name="Feyenoord vs AZ",
        outcomes=outcomes_no_arb,
        total_bankroll=1000.0
    )

    if arb_no:
        print(f"✓ Arbitrage detected!")
        print(f"Profit: €{arb_no.guaranteed_profit:.2f}")
    else:
        print("✗ No arbitrage opportunity detected")
        # Calculate S to show it's > 1.0
        s = sum(1/o.odds for o in outcomes_no_arb)
        print(f"S value: {s:.4f} (need S < 1.0 for arbitrage)")

    print()
    print("=" * 60)
    print("Core engine is working! Now Member B can build scrapers")
    print("and Member C can build the React dashboard.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
