"""Arbitrage scanner using real Odds API data.

This version uses The Odds API instead of mock sources.
"""
import asyncio
from typing import List
from datetime import datetime
from adapters.sources.odds_api import OddsAPIClient
from core.arbitrage import create_arbitrage_opportunity
from core.models import Outcome, ArbitrageOpportunity


class RealAPIScanner:
    """Scans The Odds API for arbitrage opportunities."""

    def __init__(self, bankroll: float = 1000.0, region: str = "eu"):
        """Initialize scanner.

        Args:
            bankroll: Total bankroll to distribute across bets
            region: Region for bookmakers (eu, uk, us, au)
        """
        self.bankroll = bankroll
        self.region = region
        self.opportunities_found = 0
        self.client = OddsAPIClient(region=region)

    async def scan_all_events(self) -> None:
        """Scan all available events for arbitrage."""
        print("\n📡 Fetching available matches from The Odds API...")

        events = await self.client.get_available_events()
        print(f"✓ Found {len(events)} upcoming matches\n")

        for event in events:
            await self.scan_event(event)
            # Small delay between events
            await asyncio.sleep(0.3)

    async def scan_event(self, event: dict) -> None:
        """Scan a single event for arbitrage.

        Args:
            event: Event data from get_available_events()
        """
        print(f"🔍 {event['name']}")
        print("-" * 60)

        try:
            # Fetch all odds from all bookmakers for this event
            # The API returns odds from multiple bookmakers
            all_outcomes = []

            if "_game_data" in event:
                # Use cached game data if available
                all_outcomes = self.client._parse_odds(event["_game_data"])
            else:
                # Fetch from API
                all_outcomes = await self.client.fetch_odds(event["id"])

            if not all_outcomes:
                print("  ⚠️  No odds available\n")
                return

            # Group outcomes by market and find best odds
            outcomes_by_market = {}
            for outcome in all_outcomes:
                market = outcome.market
                if market not in outcomes_by_market:
                    outcomes_by_market[market] = []
                outcomes_by_market[market].append(outcome)

            # Display all odds
            for market, outcomes in outcomes_by_market.items():
                print(f"  {market:12s}: ", end="")
                odds_str = " | ".join(
                    f"{o.bookmaker}: {o.odds:.2f}" for o in sorted(outcomes, key=lambda x: -x.odds)[:3]
                )
                print(odds_str)

            # Check for arbitrage using best odds from each market
            if len(outcomes_by_market) >= 3:
                best_outcomes = []
                for market in ["Home Win", "Draw", "Away Win"]:
                    if market in outcomes_by_market:
                        outcomes = outcomes_by_market[market]
                        best = max(outcomes, key=lambda x: x.odds)
                        best_outcomes.append(best)

                if len(best_outcomes) == 3:
                    arb = create_arbitrage_opportunity(
                        event_name=event["name"],
                        outcomes=best_outcomes,
                        total_bankroll=self.bankroll
                    )

                    if arb:
                        self._display_arbitrage_opportunity(arb)
                        self.opportunities_found += 1

            print()

        except Exception as e:
            print(f"  ❌ Error: {e}\n")

    def _display_arbitrage_opportunity(self, arb: ArbitrageOpportunity) -> None:
        """Display an arbitrage opportunity."""
        print()
        print("  " + "=" * 56)
        print("  🎯 ARBITRAGE OPPORTUNITY FOUND!")
        print("  " + "=" * 56)
        print(f"  Profit Margin: {arb.profit_margin:.2f}%")
        print(f"  Arbitrage Percentage (S): {arb.arbitrage_percentage:.4f}")
        print()
        print("  BET INSTRUCTIONS:")
        print("  " + "-" * 56)

        for i, (outcome, stake) in enumerate(zip(arb.outcomes, arb.stakes), 1):
            print(f"  {i}. {outcome.bookmaker:15s} → "
                  f"€{stake:.0f} on {outcome.market:12s} @ {outcome.odds:.2f}")

        print("  " + "-" * 56)
        print(f"  Total Investment: €{arb.total_bankroll:.2f}")
        print(f"  Guaranteed Profit: €{arb.guaranteed_profit:.2f}")
        print(f"  ROI: {arb.roi:.2f}%")
        print("  " + "=" * 56)

    async def run_continuous_scan(self, interval_seconds: int = 300) -> None:
        """Run continuous scanning loop.

        Args:
            interval_seconds: Time to wait between scans (default 5 minutes)
        """
        print("=" * 60)
        print("🚀 ArbStream Real API Scanner Started")
        print("=" * 60)
        print(f"Region: {self.region}")
        print(f"Bankroll: €{self.bankroll:.2f}")
        print(f"Scan interval: {interval_seconds}s")
        print("=" * 60)

        scan_count = 0
        try:
            while True:
                scan_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n\n📊 Scan #{scan_count} at {timestamp}")
                print("=" * 60)

                await self.scan_all_events()

                print(f"✓ Scan complete. Opportunities found: {self.opportunities_found}")
                print(f"⏰ Next scan in {interval_seconds} seconds...")

                await asyncio.sleep(interval_seconds)

        finally:
            await self.client.close()


async def main():
    """Main entry point for the real API scanner."""

    scanner = RealAPIScanner(bankroll=1000.0, region="eu")

    # Run one scan for testing
    # await scanner.scan_all_events()
    # await scanner.client.close()

    # Or run continuous scanning (every 5 minutes to conserve API calls)
    await scanner.run_continuous_scan(interval_seconds=300)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Scanner stopped by user")
