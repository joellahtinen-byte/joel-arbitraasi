# How to Implement Real Scrapers

The mock sources are working. Now here's how to implement a real scraper.

## Step 1: Inspect the Bookmaker Site

```bash
# Install Playwright browsers
playwright install chromium

# Open browser to inspect HTML structure
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://www.toto.nl/sport/voetbal')
    input('Press Enter to close...')
"
```

## Step 2: Find the CSS Selectors

Open the site in the browser and use DevTools (F12) to find:

1. **Event list elements** - where matches are listed
2. **Odds elements** - where the numbers are displayed
3. **Market labels** - "1" (Home), "X" (Draw), "2" (Away)

Example selectors you might find:
```css
.match-row           /* Each match */
.team-name           /* Team names */
.odds-button         /* Odds values */
.market-home         /* Home win odds */
.market-draw         /* Draw odds */
.market-away         /* Away win odds */
```

## Step 3: Update toto_scraper.py

Replace the placeholder logic in `/adapters/sources/toto_scraper.py`:

```python
async def _extract_odds_from_page(self, page: Page, event_id: str) -> List[Outcome]:
    """Extract odds using real selectors."""

    outcomes = []

    # Wait for odds to load
    await page.wait_for_selector('.odds-button')

    # Extract home odds
    home_element = await page.query_selector('.market-home .odds-button')
    if home_element:
        home_text = await home_element.inner_text()
        home_odds = float(home_text.replace(',', '.'))
        outcomes.append(Outcome(self.bookmaker_name, home_odds, "Home Win"))

    # Extract draw odds
    draw_element = await page.query_selector('.market-draw .odds-button')
    if draw_element:
        draw_text = await draw_element.inner_text()
        draw_odds = float(draw_text.replace(',', '.'))
        outcomes.append(Outcome(self.bookmaker_name, draw_odds, "Draw"))

    # Extract away odds
    away_element = await page.query_selector('.market-away .odds-button')
    if away_element:
        away_text = await away_element.inner_text()
        away_odds = float(away_text.replace(',', '.'))
        outcomes.append(Outcome(self.bookmaker_name, away_odds, "Away Win"))

    return outcomes
```

## Step 4: Handle Dynamic Content

Many betting sites load odds via JavaScript. Use Playwright's waiting features:

```python
# Wait for specific element
await page.wait_for_selector('.odds-button', timeout=5000)

# Wait for network to be idle
await page.wait_for_load_state('networkidle')

# Wait for specific text to appear
await page.wait_for_function('document.querySelector(".odds-button").innerText !== ""')
```

## Step 5: Test the Real Scraper

Replace mock source in `scanner.py`:

```python
from adapters.sources.toto_scraper import TotoScraper

sources = [
    TotoScraper(),
    MockOddsSource("Bet365", has_arbitrage_bias=True),  # Still mock for now
]
```

Run the scanner:
```bash
python3 scanner.py
```

## Step 6: Add Error Handling

Real scrapers fail often. Add robust error handling:

```python
async def fetch_odds(self, event_id: str) -> List[Outcome]:
    """Fetch odds with retry logic."""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Set timeout
                page.set_default_timeout(10000)

                await page.goto(url, wait_until="networkidle")
                outcomes = await self._extract_odds_from_page(page, event_id)
                await browser.close()

                return outcomes

        except Exception as e:
            print(f"⚠️  Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise OddsSourceError(f"Failed after {max_retries} attempts")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Common Issues

**Issue**: Odds not loading
- **Solution**: Increase wait time, check if JavaScript is blocking

**Issue**: "Element not found"
- **Solution**: Selectors changed. Re-inspect the HTML

**Issue**: Getting blocked/captcha
- **Solution**: Add user-agent, slow down requests, use residential proxies

**Issue**: Odds in wrong format (e.g., "2,10" instead of 2.10)
- **Solution**: Use `.replace(',', '.')` before `float()`

## Quick Test Script

Create `test_scraper.py`:

```python
import asyncio
from adapters.sources.toto_scraper import TotoScraper

async def test():
    scraper = TotoScraper()

    # Test getting events
    events = await scraper.get_available_events()
    print(f"Found {len(events)} events")

    if events:
        # Test getting odds for first event
        event = events[0]
        print(f"\nFetching odds for: {event['name']}")
        odds = await scraper.fetch_odds(event['id'])

        for outcome in odds:
            print(f"  {outcome.market}: {outcome.odds}")

asyncio.run(test())
```

Run it:
```bash
python3 test_scraper.py
```
