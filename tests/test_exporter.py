import json
import os
import sys
from pathlib import Path

# Make src importable
TEST_DIR = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from main import export_csv, export_json  # noqa: E402

def test_export_json_and_csv(tmp_path: Path):
    sample = [
        {
            "id": "1",
            "listing_title": "Test Title",
            "listing_price": "$10",
            "price_amount": 10.0,
            "price_currency": "$",
            "condition": "NEW",
            "location": "Austin, TX",
            "latitude": 30.0,
            "longitude": -97.0,
            "vehicle_make_display_name": None,
            "vehicle_model_display_name": None,
            "vehicle_features": ["A"],
            "seller_name": "Alice",
            "seller_profile_link": "https://www.facebook.com/profile.php?id=1",
            "photos": ["https://example.com/1.jpg"],
            "creation_time": "2024-01-01T00:00:00+00:00",
            "reviews": []
        }
    ]
    json_path = tmp_path / "data.json"
    csv_path = tmp_path / "data.csv"

    export_json(sample, str(json_path))
    export_csv(sample, str(csv_path))

    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded[0]["id"] == "1"

    assert csv_path.exists()
    with open(csv_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Test Title" in content
    assert "listing_title" in content.splitlines()[0]  # header present