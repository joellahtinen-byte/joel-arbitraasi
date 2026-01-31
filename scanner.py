"""Arbitrage scanner - continuously checks for opportunities.

This is the main script that:
1. Fetches odds from multiple bookmakers
2. Detects arbitrage opportunities using the core engine
3. Displays opportunities as they're found

Run this script to start scanning for arbitrage.
"""
import asyncio
from typing import List, Dict
from datetime import datetime
from adapters.sources.mock_source import MockOddsSource
from adapters.sources.odds_source import OddsSource
from core.arbitrage import create_arbitrage_opportunity
from core.models import Outcome, ArbitrageOpportunity


class ArbitrageScanner:
    """Scans multiple bookmakers for arbitrage opportunities."""

    def __init__(self, sources: List[OddsSource], bankroll: float = 1000.0):
        """Initialize scanner.

        Args:
            sources: List of odds sources (scrapers/APIs)
            bankroll: Total bankroll to distribute across bets
        """
        self.sources = sources
        self.bankroll = bankroll
        self.opportunities_found = 0

    async def scan_event(self, event_id: str, event_name: str) -> None:
        """Scan a single event across all bookmakers.

        Args:
            event_id: Event identifier
            event_name: Human-readable event name
        """
        print(f"\n🔍 Scanning: {event_name}")
        print("-" * 60)

        # Fetch odds from all sources concurrently
        tasks = [source.fetch_odds(event_id) for source in self.sources]
        try:
            all_outcomes = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"❌ Error fetching odds: {e}")
            return

        # Filter out errors and flatten outcomes
        outcomes_by_market = {}
        for source_outcomes in all_outcomes:
            if isinstance(source_outcomes, Exception):
                continue

            for outcome in source_outcomes:
                market = outcome.market
                if market not in outcomes_by_market:
                    outcomes_by_market[market] = []
                outcomes_by_market[market].append(outcome)

        # Display odds from all bookmakers
        for market, outcomes in outcomes_by_market.items():
            print(f"  {market:12s}: ", end="")
            odds_str = " | ".join(
                f"{o.bookmaker}: {o.odds:.2f}" for o in outcomes
            )
            print(odds_str)

        # Try all combinations to find arbitrage
        # For 3-way markets (Home/Draw/Away), we need one outcome from each market
        if len(outcomes_by_market) == 3:
            arb_found = await self._check_three_way_arbitrage(
                event_name, outcomes_by_market
            )
            if arb_found:
                self.opportunities_found += 1

    async def _check_three_way_arbitrage(
        self, event_name: str, outcomes_by_market: Dict[str, List[Outcome]]
    ) -> bool:
        """Check for arbitrage in 3-way markets (Home/Draw/Away).

        Args:
            event_name: Name of the event
            outcomes_by_market: Dict mapping market names to outcomes

        Returns:
            True if arbitrage found, False otherwise
        """
        markets = list(outcomes_by_market.keys())
        if len(markets) != 3:
            return False

        # Get best odds for each market
        best_outcomes = []
        for market in markets:
            outcomes = outcomes_by_market[market]
            best = max(outcomes, key=lambda x: x.odds)
            best_outcomes.append(best)

        # Check for arbitrage
        arb = create_arbitrage_opportunity(
            event_name=event_name,
            outcomes=best_outcomes,
            total_bankroll=self.bankroll
        )

        if arb:
            self._display_arbitrage_opportunity(arb)
            return True

        return False

    def _display_arbitrage_opportunity(self, arb: ArbitrageOpportunity) -> None:
        """Display an arbitrage opportunity in a clear format.

        Args:
            arb: The arbitrage opportunity to display
        """
        print("\n" + "=" * 60)
        print("🎯 ARBITRAGE OPPORTUNITY FOUND!")
        print("=" * 60)
        print(f"Event: {arb.event_name}")
        print(f"Profit Margin: {arb.profit_margin:.2f}%")
        print(f"Arbitrage Percentage (S): {arb.arbitrage_percentage:.4f}")
        print()
        print("BET INSTRUCTIONS:")
        print("-" * 60)

        for i, (outcome, stake) in enumerate(zip(arb.outcomes, arb.stakes), 1):
            print(f"{i}. {outcome.bookmaker:12s} → "
                  f"Bet €{stake:.0f} on {outcome.market:12s} @ {outcome.odds:.2f}")

        print("-" * 60)
        print(f"Total Investment: €{arb.total_bankroll:.2f}")
        print(f"Guaranteed Profit: €{arb.guaranteed_profit:.2f}")
        print(f"ROI: {arb.roi:.2f}%")
        print("=" * 60)

    async def scan_all_events(self) -> None:
        """Scan all available events from the first source."""
        # Get events from first source (assume all sources cover same events)
        events = await self.sources[0].get_available_events()

        for event in events:
            await self.scan_event(event["id"], event["name"])
            # Small delay between events
            await asyncio.sleep(0.5)

    async def run_continuous_scan(self, interval_seconds: int = 60) -> None:
        """Run continuous scanning loop.

        Args:
            interval_seconds: Time to wait between scans
        """
        print("=" * 60)
        print("🚀 ArbStream Scanner Started")
        print("=" * 60)
        print(f"Scanning {len(self.sources)} bookmakers")
        print(f"Bankroll: €{self.bankroll:.2f}")
        print(f"Scan interval: {interval_seconds}s")
        print("=" * 60)

        scan_count = 0
        while True:
            scan_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n\n📊 Scan #{scan_count} at {timestamp}")

            await self.scan_all_events()

            print(f"\n✓ Scan complete. Opportunities found: {self.opportunities_found}")
            print(f"⏰ Next scan in {interval_seconds} seconds...")

            await asyncio.sleep(interval_seconds)


async def main():
    """Main entry point for the scanner."""

    # Phase 1: Use mock sources for testing
    # Replace these with real scrapers once implemented
    sources = [
        MockOddsSource("TOTO", has_arbitrage_bias=True),
        MockOddsSource("Bet365", has_arbitrage_bias=True),
        MockOddsSource("Unibet", has_arbitrage_bias=False),
    ]

    # TODO: Replace with real scrapers:
    # from adapters.sources.toto_scraper import TotoScraper
    # from adapters.sources.bet365_scraper import Bet365Scraper
    # sources = [
    #     TotoScraper(),
    #     Bet365Scraper(),
    # ]

    scanner = ArbitrageScanner(sources=sources, bankroll=1000.0)

    # Run one scan for testing
    # await scanner.scan_all_events()

    # Or run continuous scanning
    await scanner.run_continuous_scan(interval_seconds=30)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Scanner stopped by user")
