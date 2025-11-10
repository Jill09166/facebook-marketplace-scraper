from typing import Dict, Optional

from src.utils.data_cleaner import ensure_full_facebook_url

def extract_seller(name: Optional[str], href: Optional[str]) -> Dict[str, Optional[str]]:
    return {
        "seller_name": (name or "").strip() or None,
        "seller_profile_link": ensure_full_facebook_url(href),
        "seller_profile_image": None,  # Not present in mock; left for future extension
    }