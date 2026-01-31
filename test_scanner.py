"""Quick test of the scanner with mock data."""
import asyncio
from scanner import ArbitrageScanner
from adapters.sources.mock_source import MockOddsSource


async def main():
    """Run a single scan for testing."""
    sources = [
        MockOddsSource("TOTO", has_arbitrage_bias=True),
        MockOddsSource("Bet365", has_arbitrage_bias=True),
        MockOddsSource("Unibet", has_arbitrage_bias=False),
    ]

    scanner = ArbitrageScanner(sources=sources, bankroll=1000.0)

    print("=" * 60)
    print("🧪 Testing Scanner with Mock Data")
    print("=" * 60)

    await scanner.scan_all_events()

    print(f"\n✓ Test complete. Opportunities found: {scanner.opportunities_found}")


if __name__ == "__main__":
    asyncio.run(main())
