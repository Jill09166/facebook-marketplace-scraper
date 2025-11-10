from typing import Optional

_CATEGORY_TO_PATH = {
    "vehicles": "marketplace/category/vehicles",
    "electronics": "marketplace/category/electronics",
    "classifieds": "marketplace/category/classifieds",
    "housing": "marketplace/category/propertyrentals",
    "homegoods": "marketplace/category/home-garden",
}

def map_category(cat: Optional[str]) -> str:
    """
    Maps a friendly category name to a hypothetical path (used if not in mock).
    """
    if not cat:
        return _CATEGORY_TO_PATH["vehicles"]
    return _CATEGORY_TO_PATH.get(cat.lower(), _CATEGORY_TO_PATH["vehicles"])