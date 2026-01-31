"""The Odds API adapter for fetching real bookmaker odds.

This adapter fetches odds from The Odds API (theoddsapi.com) which aggregates
odds from multiple bookmakers including European bookmakers relevant to the
Netherlands market (Bet365, Unibet, etc.).

API Documentation: https://the-odds-api.com/liveapi/guides/v4/
"""
import os
from typing import List, Dict, Optional
import aiohttp
from dotenv import load_dotenv
from adapters.sources.odds_source import OddsSource, OddsSourceError
from core.models import Outcome

# Load environment variables
load_dotenv()


class OddsAPIClient(OddsSource):
    """Client for The Odds API.

    Fetches odds from multiple European bookmakers via a single API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        region: str = "eu",
        bookmaker_filter: Optional[str] = None
    ):
        """Initialize The Odds API client.

        Args:
            api_key: API key (defaults to ODDS_API_KEY env var)
            base_url: API base URL (defaults to ODDS_API_BASE_URL env var)
            region: Region for bookmakers (eu, uk, us, au)
            bookmaker_filter: Specific bookmaker to filter (optional)
        """
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        self.base_url = base_url or os.getenv(
            "ODDS_API_BASE_URL",
            "https://api.the-odds-api.com/v4"
        )
        self.region = region
        self._bookmaker_filter = bookmaker_filter

        if not self.api_key:
            raise ValueError("ODDS_API_KEY not found in environment variables")

        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def bookmaker_name(self) -> str:
        return self._bookmaker_filter or "TheOddsAPI"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make an API request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            OddsSourceError: If request fails
        """
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"

        # Add API key to params
        params["apiKey"] = self.api_key

        try:
            async with session.get(url, params=params) as response:
                # Check remaining requests
                remaining = response.headers.get("x-requests-remaining")
                used = response.headers.get("x-requests-used")
                if remaining:
                    print(f"📊 API Usage: {used} used, {remaining} remaining")

                if response.status == 401:
                    raise OddsSourceError("Invalid API key")
                elif response.status == 429:
                    raise OddsSourceError("API rate limit exceeded")
                elif response.status != 200:
                    text = await response.text()
                    raise OddsSourceError(
                        f"API request failed: {response.status} - {text}"
                    )

                return await response.json()

        except aiohttp.ClientError as e:
            raise OddsSourceError(f"Network error: {str(e)}")

    async def get_available_sports(self) -> List[Dict]:
        """Get list of available sports.

        Returns:
            List of sports with keys: key, active, title, description
        """
        try:
            sports = await self._make_request("sports", {})
            # Filter to only in-season sports
            return [s for s in sports if s.get("active", False)]
        except Exception as e:
            raise OddsSourceError(f"Failed to get sports: {str(e)}")

    async def get_available_events(self) -> List[dict]:
        """Get available football matches.

        Returns:
            List of event dictionaries
        """
        try:
            # Get soccer odds (soccer_* sports)
            # Most common: soccer_epl, soccer_germany_bundesliga, etc.
            # For Netherlands, we want Eredivisie if available
            events = []

            # Try to get soccer events
            for sport_key in ["soccer_netherlands_eredivisie", "soccer_epl", "soccer_germany_bundesliga"]:
                try:
                    params = {
                        "regions": self.region,
                        "markets": "h2h",  # Head to head (1X2)
                        "oddsFormat": "decimal",
                    }

                    data = await self._make_request(
                        f"sports/{sport_key}/odds",
                        params
                    )

                    for game in data:
                        # Store the full game data for later use
                        event_data = {
                            "id": game["id"],
                            "name": f"{game['home_team']} vs {game['away_team']}",
                            "sport": sport_key,
                            "commence_time": game.get("commence_time"),
                            "_game_data": game,  # Store full data for fetch_odds
                        }
                        events.append(event_data)

                except OddsSourceError:
                    # Sport might not be available, continue
                    continue

            return events

        except Exception as e:
            raise OddsSourceError(f"Failed to get events: {str(e)}")

    async def fetch_odds(self, event_id: str) -> List[Outcome]:
        """Fetch odds for a specific event.

        Args:
            event_id: Event ID from get_available_events()

        Returns:
            List of Outcome objects with odds from different bookmakers

        Note:
            This returns outcomes from ALL bookmakers in the response.
            The scanner will pick the best odds across bookmakers.
        """
        try:
            # Event ID format from The Odds API contains the sport key
            # We need to extract it or store it separately
            # For now, try common soccer leagues

            sport_keys = [
                "soccer_netherlands_eredivisie",
                "soccer_epl",
                "soccer_germany_bundesliga",
                "soccer_spain_la_liga",
                "soccer_italy_serie_a",
                "soccer_france_ligue_one",
            ]

            for sport_key in sport_keys:
                try:
                    params = {
                        "regions": self.region,
                        "markets": "h2h",
                        "oddsFormat": "decimal",
                        "eventIds": event_id,
                    }

                    data = await self._make_request(
                        f"sports/{sport_key}/odds",
                        params
                    )

                    if not data or len(data) == 0:
                        continue

                    # Found the event
                    game = data[0]
                    return self._parse_odds(game)

                except OddsSourceError:
                    continue

            raise OddsSourceError(f"Event {event_id} not found")

        except Exception as e:
            raise OddsSourceError(f"Failed to fetch odds: {str(e)}")

    def _parse_odds(self, game_data: Dict) -> List[Outcome]:
        """Parse odds from API response.

        Args:
            game_data: Game data from The Odds API

        Returns:
            List of Outcome objects for all bookmakers
        """
        outcomes = []
        home_team = game_data["home_team"]
        away_team = game_data["away_team"]

        bookmakers = game_data.get("bookmakers", [])

        for bookmaker in bookmakers:
            bookmaker_name = bookmaker["key"]

            # Apply bookmaker filter if specified
            if self._bookmaker_filter and bookmaker_name != self._bookmaker_filter:
                continue

            markets = bookmaker.get("markets", [])

            for market in markets:
                if market["key"] != "h2h":  # Head to head (1X2)
                    continue

                # Parse outcomes
                for outcome in market["outcomes"]:
                    outcome_name = outcome["name"]
                    odds = outcome["price"]

                    # Map team names to standard market labels
                    if outcome_name == home_team:
                        market_label = "Home Win"
                    elif outcome_name == away_team:
                        market_label = "Away Win"
                    elif outcome_name == "Draw":
                        market_label = "Draw"
                    else:
                        continue

                    outcomes.append(
                        Outcome(
                            bookmaker=bookmaker_name,
                            odds=odds,
                            market=market_label
                        )
                    )

        return outcomes


class OddsAPIMultiSource:
    """Wrapper that creates separate sources for each bookmaker.

    This allows the scanner to treat each bookmaker as a separate source,
    which is better for the arbitrage detection logic.
    """

    def __init__(self, api_key: Optional[str] = None, region: str = "eu"):
        """Initialize multi-source wrapper.

        Args:
            api_key: API key for The Odds API
            region: Region (eu, uk, us, au)
        """
        self.api_key = api_key
        self.region = region

    async def get_sources_for_sport(self, sport_key: str) -> List[OddsSource]:
        """Get list of bookmaker sources available for a sport.

        Args:
            sport_key: Sport key (e.g., 'soccer_netherlands_eredivisie')

        Returns:
            List of OddsSource objects, one per bookmaker
        """
        # Get available bookmakers from API
        client = OddsAPIClient(api_key=self.api_key, region=self.region)

        try:
            params = {
                "regions": self.region,
                "markets": "h2h",
                "oddsFormat": "decimal",
            }

            data = await client._make_request(f"sports/{sport_key}/odds", params)

            if not data or len(data) == 0:
                return []

            # Get unique bookmaker keys
            bookmakers = set()
            for game in data:
                for bookmaker in game.get("bookmakers", []):
                    bookmakers.add(bookmaker["key"])

            # Create a source for each bookmaker
            sources = []
            for bookmaker_key in bookmakers:
                source = OddsAPIClient(
                    api_key=self.api_key,
                    region=self.region,
                    bookmaker_filter=bookmaker_key
                )
                sources.append(source)

            return sources

        finally:
            await client.close()
