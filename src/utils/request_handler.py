import json
import logging
import os
import time
from typing import Optional

import requests

# Canned mock HTML that mimics a minimal Marketplace grid.
MOCK_HTML = """
<!doctype html>
<html lang="en">
  <body>
    <section id="marketplace">
      <article class="listing" data-id="1384077819184401">
        <h2 class="title">2013 Nissan Rogue · SV w/SL Pkg Sport Utility 4D</h2>
        <span class="price" data-currency="USD">$3,500</span>
        <div class="condition">USED</div>
        <div class="location" data-city="New York" data-state="NY" data-lat="40.7180786" data-lng="-73.9984130">New York, NY</div>
        <time class="created" datetime="2023-11-10T08:15:00Z">Nov 10, 2023</time>
        <div class="vehicle">
          <span class="make">Nissan</span>
          <span class="model">Rogue</span>
        </div>
        <ul class="features">
          <li>Leather Seats</li>
          <li>Moon Roof</li>
          <li>Navigation</li>
          <li>Bluetooth</li>
          <li>Backup Camera</li>
        </ul>
        <div class="photos">
          <img src="https://cdn.example.com/395461179_24825490330375167.jpg"/>
          <img src="https://cdn.example.com/395623847_24825485130375687.jpg"/>
        </div>
        <a class="seller" href="https://www.facebook.com/profile.php?id=1000123456789">Ray Goberdhan</a>
      </article>

      <article class="listing" data-id="9845012399123456">
        <h2 class="title">iPhone 13 Pro Max 256GB</h2>
        <span class="price" data-currency="USD">$680</span>
        <div class="condition">LIKE_NEW</div>
        <div class="location" data-city="Austin" data-state="TX" data-lat="30.2672" data-lng="-97.7431">Austin, TX</div>
        <time class="created" datetime="2024-05-02T12:22:00Z">May 2, 2024</time>
        <ul class="features">
          <li>Face ID</li>
          <li>ProMotion</li>
          <li>128 MP Camera</li>
        </ul>
        <div class="photos">
          <img src="https://cdn.example.com/iphone13_1.jpg"/>
        </div>
        <a class="seller" href="/profile.php?id=1000987654321">Eliza</a>
      </article>
    </section>
  </body>
</html>
"""

def load_settings() -> dict:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    cfg_path = os.path.join(base_dir, "config", "settings.json")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_dirs(settings: dict) -> None:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    out_dir = os.path.normpath(os.path.join(base_dir, settings.get("outputs_dir", "../outputs")))
    logs_dir = os.path.normpath(os.path.join(base_dir, settings.get("logs_dir", "../outputs/logs")))
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

def configure_logging(settings: dict) -> None:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    log_dir = os.path.normpath(os.path.join(base_dir, settings.get("logs_dir", "../outputs/logs")))
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "run.log")

    # Avoid duplicate handlers in test runs
    for h in list(logging.root.handlers):
        logging.root.removeHandler(h)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler()
        ],
    )

def fetch_html(url: Optional[str], settings: dict, *, category: Optional[str] = None, query: Optional[str] = None) -> str:
    """
    Fetch HTML either from the network or from MOCK_HTML based on settings.
    """
    logger = logging.getLogger("request_handler")
    if settings.get("use_mock", False):
        logger.info("Using mock HTML for category=%s query=%s", category, query)
        return MOCK_HTML

    if not url:
        raise ValueError("A URL must be provided when use_mock is false.")

    headers = {
        "User-Agent": settings.get("user_agent", "Mozilla/5.0"),
        "Accept-Language": "en-US,en;q=0.9",
    }
    timeout = int(settings.get("request_timeout_seconds", 20))
    retries = int(settings.get("retries", 2))

    last_exc = None
    for attempt in range(retries + 1):
        try:
            logger.info("Fetching URL (attempt %s): %s", attempt + 1, url)
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            last_exc = exc
            logger.warning("Request failed on attempt %s: %s", attempt + 1, exc)
            time.sleep(min(2 ** attempt, 5))

    assert last_exc is not None
    raise last_exc