"""Test the real Odds API integration."""
import asyncio
from adapters.sources.odds_api import OddsAPIClient


async def main():
    """Test The Odds API connection and data fetching."""

    print("=" * 60)
    print("🧪 Testing The Odds API Integration")
    print("=" * 60)
    print()

    client = OddsAPIClient(region="eu")

    try:
        # Test 1: Get available sports
        print("1️⃣ Fetching available sports...")
        sports = await client.get_available_sports()
        print(f"✓ Found {len(sports)} active sports")

        # Show soccer sports
        soccer_sports = [s for s in sports if "soccer" in s["key"]]
        print(f"\n⚽ Soccer leagues available ({len(soccer_sports)}):")
        for sport in soccer_sports[:5]:  # Show first 5
            print(f"   - {sport['key']}: {sport['title']}")

        # Test 2: Get available events
        print("\n2️⃣ Fetching available events...")
        events = await client.get_available_events()
        print(f"✓ Found {len(events)} upcoming matches")

        if events:
            print(f"\n📅 Upcoming matches (showing first 5):")
            for event in events[:5]:
                print(f"   - {event['name']} (ID: {event['id']})")

            # Test 3: Get odds for first event
            print(f"\n3️⃣ Fetching odds for: {events[0]['name']}")
            odds = await client.fetch_odds(events[0]["id"])
            print(f"✓ Found {len(odds)} odds from various bookmakers")

            print("\n📊 Odds breakdown:")
            # Group by market
            by_market = {}
            for outcome in odds:
                if outcome.market not in by_market:
                    by_market[outcome.market] = []
                by_market[outcome.market].append(outcome)

            for market, outcomes in by_market.items():
                print(f"\n   {market}:")
                for outcome in outcomes:
                    print(f"      {outcome.bookmaker:20s} → {outcome.odds:.2f}")

        else:
            print("⚠️  No events found. The API might not have odds for EU region right now.")
            print("   Try checking: https://the-odds-api.com/sports-odds-data/")

        print("\n" + "=" * 60)
        print("✅ API Integration Test Complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API key in .env file")
        print("2. Verify you have API requests remaining")
        print("3. Check https://the-odds-api.com/account/ for usage")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
