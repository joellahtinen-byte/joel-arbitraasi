# ArbStream

Automated arbitrage betting application targeting the Netherlands market.

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run example
python example_usage.py

# Run tests
pytest
```

## Architecture

ArbStream uses **Hexagonal Architecture** (Ports and Adapters) to keep the core arbitrage math isolated from external dependencies:

```
/core                    # Pure math logic (no external dependencies)
/adapters/sources        # Odds data (APIs/Scrapers)
/adapters/execution      # Bet placement
/frontend                # React dashboard
```

## Team Division

- **Member A**: Core engine + FastAPI backend
- **Member B**: Playwright scrapers + bet execution
- **Member C**: React frontend

See `CLAUDE.md` for detailed development guidelines.

## How It Works

1. Scrapers collect odds from TOTO.nl, Bet365, Unibet.nl
2. Core engine detects arbitrage using `S = sum(1/odds)`
3. Calculate optimal stakes (rounded to avoid gubbing)
4. Execute bets via Playwright automation
5. Monitor profits in React dashboard
