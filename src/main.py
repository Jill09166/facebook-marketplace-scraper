import argparse
import csv
import json
import logging
import os
from typing import Any, Dict, List, Tuple

from src.modules.category_mapper import map_category
from src.modules.listings_parser import parse_listings
from src.utils.data_cleaner import dedupe_listings
from src.utils.request_handler import configure_logging, ensure_dirs, fetch_html, load_settings

def build_url(base: str, path: str, query: str) -> str:
    base = base.rstrip("/")
    path = path.lstrip("/")
    if query:
        return f"{base}/{path}?q={query}"
    return f"{base}/{path}"

def export_json(data: List[Dict[str, Any]], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_csv(data: List[Dict[str, Any]], out_path: str) -> None:
    if not data:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return
    fieldnames = list(data[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def resolve_output_paths(settings: Dict[str, Any]) -> Tuple[str, str]:
    base_dir = os.path.dirname(__file__)
    outputs_dir = os.path.normpath(os.path.join(base_dir, settings.get("outputs_dir", "../outputs")))
    os.makedirs(outputs_dir, exist_ok=True)
    return (
        os.path.join(outputs_dir, "data.json"),
        os.path.join(outputs_dir, "data.csv"),
    )

def run(category: str, query: str, limit: int) -> List[Dict[str, Any]]:
    settings = load_settings()
    ensure_dirs(settings)
    configure_logging(settings)
    logger = logging.getLogger("main")

    logger.info("Starting scrape | category=%s query=%s limit=%s", category, query, limit)

    cat_path = map_category(category)
    url = build_url("https://www.facebook.com", cat_path, query)

    html = fetch_html(url, settings, category=category, query=query)
    items = parse_listings(html)
    items = items[:limit] if limit else items
    items = dedupe_listings(items)

    logger.info("Parsed %s listings", len(items))

    json_path, csv_path = resolve_output_paths(settings)
    export_json(items, json_path)
    export_csv(items, csv_path)

    logger.info("Exported JSON to %s", json_path)
    logger.info("Exported CSV to %s", csv_path)

    return items

def main():
    parser = argparse.ArgumentParser(description="Facebook Marketplace Scraper (mock-capable)")
    parser.add_argument("--category", default=None, help="Category like vehicles, electronics")
    parser.add_argument("--query", default="", help="Search query")
    parser.add_argument("--limit", type=int, default=None, help="Max listings to return")
    args = parser.parse_args()

    settings = load_settings()
    limit = args.limit or int(settings.get("default_limit", 50))
    category = args.category or settings.get("mock_category", "vehicles")

    items = run(category=category, query=args.query, limit=limit)
    print(json.dumps({"count": len(items), "sample": items[:1]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()