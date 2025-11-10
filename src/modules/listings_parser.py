from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from src.modules.seller_extractor import extract_seller
from src.utils.data_cleaner import normalize_location, normalize_price, parse_timestamp

def _text(el) -> Optional[str]:
    return el.get_text(strip=True) if el else None

def parse_listings(html: str) -> List[Dict[str, Any]]:
    """
    Parse Marketplace-like HTML to structured listings.
    """
    soup = BeautifulSoup(html, "html.parser")
    out: List[Dict[str, Any]] = []

    for card in soup.select("article.listing"):
        _id = card.get("data-id")

        title = _text(card.select_one(".title"))
        price_el = card.select_one(".price")
        price = normalize_price(_text(price_el))
        currency_attr = price_el.get("data-currency") if price_el else None
        if currency_attr and not price["currency"]:
            price["currency"] = currency_attr

        condition = _text(card.select_one(".condition"))

        loc_el = card.select_one(".location")
        location = normalize_location(
            city=loc_el.get("data-city") if loc_el else None,
            state=loc_el.get("data-state") if loc_el else None,
            lat=loc_el.get("data-lat") if loc_el else None,
            lng=loc_el.get("data-lng") if loc_el else None,
        )

        created_el = card.select_one("time.created")
        creation_time = parse_timestamp(created_el.get("datetime") if created_el else None)

        vehicle = card.select_one(".vehicle")
        make = _text(vehicle.select_one(".make")) if vehicle else None
        model = _text(vehicle.select_one(".model")) if vehicle else None

        features = [f.get_text(strip=True) for f in card.select(".features li")]

        photos = [img.get("src") for img in card.select(".photos img") if img.get("src")]

        seller_a = card.select_one("a.seller")
        seller = extract_seller(_text(seller_a), seller_a.get("href") if seller_a else None)

        item: Dict[str, Any] = {
            "id": _id,
            "listing_title": title,
            "listing_price": price["formatted"],
            "price_amount": price["amount"],
            "price_currency": price["currency"],
            "condition": condition,
            "location": location["label"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "vehicle_make_display_name": make,
            "vehicle_model_display_name": model,
            "vehicle_features": features,
            "seller_name": seller["seller_name"],
            "seller_profile_link": seller["seller_profile_link"],
            "photos": photos,
            "creation_time": creation_time,
            "reviews": [],  # Not present in mock
        }
        out.append(item)

    return out