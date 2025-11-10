import json
import os
import sys

# Make src importable
TEST_DIR = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.request_handler import MOCK_HTML  # noqa: E402
from modules.listings_parser import parse_listings  # noqa: E402

def test_parse_listings_extracts_core_fields():
    items = parse_listings(MOCK_HTML)
    assert len(items) >= 2

    first = items[0]
    required = [
        "id",
        "listing_title",
        "listing_price",
        "condition",
        "location",
        "latitude",
        "longitude",
        "vehicle_features",
        "seller_name",
        "seller_profile_link",
        "photos",
        "creation_time",
    ]
    for key in required:
        assert key in first

    assert first["id"] == "1384077819184401"
    assert "Nissan" in (first.get("vehicle_make_display_name") or "")
    assert "Rogue" in (first.get("vehicle_model_display_name") or "")
    assert isinstance(first["vehicle_features"], list)
    assert first["seller_profile_link"].startswith("https://www.facebook.com")