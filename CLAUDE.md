# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ArbStream** is an automated arbitrage betting web application targeting the Netherlands market (TOTO.nl, Bet365, Unibet.nl).

**Tech Stack:**
- Backend: Python/FastAPI
- Automation: Playwright (for web scraping and bet execution)
- Frontend: React dashboard
- Architecture: Hexagonal (Ports and Adapters)

**Architecture Philosophy:**
The hexagonal architecture isolates the core math engine from unstable scraper logic. The core domain (`/core`) contains pure mathematical functions that are independent of data sources. Adapters (`/adapters`) handle external integrations and can be swapped without modifying the core logic.

## Development Commands

### Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd frontend && npm install
```

### Testing
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/core/test_arbitrage.py

# Run with coverage
pytest --cov=core --cov=adapters

# Run in watch mode
pytest-watch
```

### Running
```bash
# Start backend (FastAPI)
uvicorn main:app --reload --port 8000

# Start frontend (React)
cd frontend && npm start

# Run scrapers in development
python -m adapters.sources.scraper_runner
```

### Linting
```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy core/ adapters/
```

## Architecture

### Hexagonal Architecture (Ports and Adapters)

```
/core                    # Domain logic (pure math, no dependencies)
  ├── arbitrage.py       # Arbitrage detection & stake calculation
  └── models.py          # Domain models (ArbitrageOpportunity, etc.)

/adapters                # External integrations
  ├── sources/           # Odds data sources (APIs/Scrapers)
  │   ├── toto_scraper.py
  │   ├── bet365_scraper.py
  │   └── unibet_scraper.py
  └── execution/         # Bet placement
      └── playwright_executor.py

/frontend                # React dashboard
```

### Data Flow

1. **Odds Collection**: Adapters fetch odds from bookmakers (API or Playwright scraper)
2. **Arbitrage Detection**: Core engine analyzes odds using `S = sum(1/odds)` formula
3. **Stake Calculation**: Core calculates optimal stake distribution (rounded to avoid detection)
4. **Execution**: Execution adapter places bets via Playwright automation
5. **Monitoring**: Frontend displays opportunities and tracks bet status

### Coding Guidelines

**Always use async/await**: All I/O operations (scraping, API calls, bet execution) must be async.

**Round stakes to whole numbers**: Use `round()` on all stake calculations to avoid bookmaker gubbing (account limiting). Never place bets with decimal cents.

**Isolate core from adapters**: The `/core` directory should never import from `/adapters`. Data flows inward through domain models.

**Error handling**: Scrapers fail frequently. Always wrap scraper calls in try/except and implement retry logic with exponential backoff.

**Type hints**: Use Python type hints everywhere. The core math must be type-safe.

## Team Division

**Member A (Quant/Backend)**: Focus on `/core` math engine, FastAPI endpoints, arbitrage algorithms, and optimization logic.

**Member B (Automation)**: Focus on `/adapters/sources` and `/adapters/execution`. Implement Playwright scrapers and bet placement automation.

**Member C (Frontend)**: Focus on `/frontend` React dashboard. Build real-time opportunity display, bet tracking, and profit analytics.

## Critical Formulas

**Arbitrage Detection**: `S = sum(1/odds_i)`. If S < 1.0, an arbitrage opportunity exists.

**Stake Distribution**: `stake_i = (total_bankroll / odds_i) / S`. Round each stake to whole numbers.

**Guaranteed Profit**: `profit = total_bankroll * (1 - S)`

**ROI**: `roi = profit / total_bankroll * 100`

## External Dependencies

- **TOTO.nl**: Primary Dutch bookmaker (requires scraping, no API)
- **Bet365**: International bookmaker (API available for odds, scraping for execution)
- **Unibet.nl**: Dutch market (scraping required)
- **Playwright**: Headless browser automation for scraping and bet placement
