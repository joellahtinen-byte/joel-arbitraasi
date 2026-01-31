"""FastAPI server that provides arbitrage opportunities via REST API.

This backend serves the web dashboard and continuously scans for opportunities.
"""
import asyncio
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from adapters.sources.odds_api import OddsAPIClient
from core.arbitrage import create_arbitrage_opportunity
from core.models import ArbitrageOpportunity, Outcome

app = FastAPI(title="ArbStream API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
opportunities_cache: List[dict] = []
last_scan_time: Optional[datetime] = None
scan_in_progress = False


class OpportunityResponse(BaseModel):
    """API response model for arbitrage opportunities."""
    event_name: str
    profit_margin: float
    guaranteed_profit: float
    roi: float
    total_investment: float
    bets: List[dict]
    timestamp: str


class ScanStatus(BaseModel):
    """API response for scan status."""
    last_scan: Optional[str]
    opportunities_count: int
    scan_in_progress: bool


async def scan_for_opportunities(bankroll: float = 1000.0):
    """Background task to scan for arbitrage opportunities."""
    global opportunities_cache, last_scan_time, scan_in_progress

    if scan_in_progress:
        return

    scan_in_progress = True
    opportunities_cache = []

    try:
        client = OddsAPIClient(region="eu")
        events = await client.get_available_events()

        for event in events:
            try:
                if "_game_data" not in event:
                    continue

                all_outcomes = client._parse_odds(event["_game_data"])

                if not all_outcomes:
                    continue

                # Group by market and find best odds
                outcomes_by_market = {}
                for outcome in all_outcomes:
                    market = outcome.market
                    if market not in outcomes_by_market:
                        outcomes_by_market[market] = []
                    outcomes_by_market[market].append(outcome)

                # Check for arbitrage
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
                            total_bankroll=bankroll
                        )

                        if arb:
                            # Convert to dict for JSON serialization
                            opp_dict = {
                                "event_name": arb.event_name,
                                "profit_margin": arb.profit_margin,
                                "guaranteed_profit": arb.guaranteed_profit,
                                "roi": arb.roi,
                                "total_investment": arb.total_bankroll,
                                "bets": [
                                    {
                                        "bookmaker": outcome.bookmaker,
                                        "market": outcome.market,
                                        "odds": outcome.odds,
                                        "stake": stake,
                                        "bet_url": get_bookmaker_url(outcome.bookmaker)
                                    }
                                    for outcome, stake in zip(arb.outcomes, arb.stakes)
                                ],
                                "timestamp": datetime.now().isoformat()
                            }
                            opportunities_cache.append(opp_dict)

            except Exception as e:
                print(f"Error processing event {event.get('name')}: {e}")
                continue

        # Sort by profit margin (highest first)
        opportunities_cache.sort(key=lambda x: x["profit_margin"], reverse=True)
        last_scan_time = datetime.now()

        await client.close()

    except Exception as e:
        print(f"Scan error: {e}")
    finally:
        scan_in_progress = False


def get_bookmaker_url(bookmaker_key: str) -> str:
    """Get the URL for a bookmaker."""
    bookmaker_urls = {
        "unibet_nl": "https://www.unibet.nl/",
        "bet365": "https://www.bet365.com/",
        "betfair_ex_eu": "https://www.betfair.com/",
        "matchbook": "https://www.matchbook.com/",
        "onexbet": "https://1xbet.com/",
        "pinnacle": "https://www.pinnacle.com/",
        "coolbet": "https://www.coolbet.com/",
        "betsson": "https://www.betsson.com/",
        "nordicbet": "https://www.nordicbet.com/",
    }
    return bookmaker_urls.get(bookmaker_key, "https://www.google.com/search?q=" + bookmaker_key)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ArbStream API", "version": "1.0.0"}


@app.get("/api/opportunities", response_model=List[OpportunityResponse])
async def get_opportunities():
    """Get current arbitrage opportunities."""
    return opportunities_cache


@app.get("/api/status", response_model=ScanStatus)
async def get_status():
    """Get scan status."""
    return {
        "last_scan": last_scan_time.isoformat() if last_scan_time else None,
        "opportunities_count": len(opportunities_cache),
        "scan_in_progress": scan_in_progress
    }


@app.post("/api/scan")
async def trigger_scan(background_tasks: BackgroundTasks):
    """Trigger a new scan."""
    if scan_in_progress:
        return {"message": "Scan already in progress"}

    background_tasks.add_task(scan_for_opportunities)
    return {"message": "Scan started"}


@app.on_event("startup")
async def startup_event():
    """Run initial scan on startup."""
    asyncio.create_task(scan_for_opportunities())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
