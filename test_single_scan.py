"""Run a single scan with the real API."""
import asyncio
from scanner_real_api import RealAPIScanner


async def main():
    scanner = RealAPIScanner(bankroll=1000.0, region="eu")
    await scanner.scan_all_events()
    await scanner.client.close()

    print("\n" + "=" * 60)
    print(f"✅ Scan complete!")
    print(f"Total opportunities found: {scanner.opportunities_found}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
