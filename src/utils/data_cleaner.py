import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from dateutil import parser as dateparser

logger = logging.getLogger("data_cleaner")

_PRICE_RE = re.compile(r"([€$£₹])?\s*([\d,.]+)", re.U)

def normalize_price(raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {"amount": None, "currency": None, "formatted": None}
    m = _PRICE_RE.search(raw.strip())
    if not m:
        return {"amount": None, "currency": None, "formatted": raw.strip()}
    currency = m.group(1) or None
    num_str = m.group(2).replace(",", "")
    try:
        amount = float(num_str)
    except ValueError:
        amount = None
    return {"amount": amount, "currency": currency, "formatted": raw.strip()}

def normalize_location(city: Optional[str], state: Optional[str], lat: Optional[str], lng: Optional[str]) -> Dict[str, Any]:
    try:
        lat_v = float(lat) if lat is not None else None
    except ValueError:
        lat_v = None
    try:
        lng_v = float(lng) if lng is not None else None
    except ValueError:
        lng_v = None

    parts = [p for p in [city, state] if p]
    label = ", ".join(parts) if parts else None
    return {"city": city, "state": state, "latitude": lat_v, "longitude": lng_v, "label": label}

def parse_timestamp(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    try:
        dt = dateparser.parse(raw)
    except Exception:
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception:
            logger.debug("Failed to parse timestamp: %s", raw)
            return None
    return dt.astimezone().isoformat()

def dedupe_listings(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for it in items:
        _id = it.get("id")
        if _id and _id not in seen:
            seen.add(_id)
            out.append(it)
        elif not _id:
            out.append(it)
    return out

def ensure_full_facebook_url(href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    href = href.strip()
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return f"https://www.facebook.com{href}"
    return f"https://www.facebook.com/{href}"