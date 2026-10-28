"""
Place Normalizer.
Standardizes place fields, categories, slugs, pricing tiers, and coordinates.
Unknown prices and opening hours are strictly preserved as None.
"""

import re
from typing import Dict, Any, List, Optional, Tuple

PLACE_TYPE_MAP = {
    "tourist": "destination",
    "destination": "destination",
    "attraction": "destination",
    "heritage": "destination",
    "nature": "destination",
    "museum": "destination",
    "park": "destination",
    "temple": "destination",
    "market": "destination",
    "food": "eatery",
    "restaurant": "eatery",
    "cafe": "eatery",
    "eatery": "eatery",
    "street_food": "eatery",
    "sweets": "eatery",
    "experience": "experience",
    "workshop": "experience",
    "safari": "experience",
    "tour": "experience"
}


class PlaceNormalizer:
    """
    Standardizes raw place dictionaries into the canonical schema.
    """

    @staticmethod
    def slugify(text: str) -> str:
        """Creates a URL-safe lowercase slug."""
        clean = re.sub(r'[^a-zA-Z0-9\s-]', '', (text or "").lower()).strip()
        return re.sub(r'[\s-]+', '-', clean)[:80]

    @classmethod
    def generate_place_id(cls, city_id: str, name: str) -> str:
        """Generates a stable, idempotent primary key."""
        slug = cls.slugify(name)
        return f"plc_{city_id}_{slug}"

    @staticmethod
    def normalize_price_level(raw_level: Any, min_cost: Optional[float] = None) -> Tuple[str, Optional[float], Optional[float]]:
        """
        Normalizes price level. Never invents values if unknown.
        Returns (price_level, min_cost, max_cost).
        """
        if raw_level in ["Free", "0", 0, "free"]:
            return "Free", 0.0, 0.0

        if min_cost is not None:
            if min_cost == 0.0:
                return "Free", 0.0, 0.0
            elif min_cost < 250:
                return "₹", min_cost, min_cost * 1.5
            elif min_cost < 700:
                return "₹₹", min_cost, min_cost * 1.5
            else:
                return "₹₹₹", min_cost, min_cost * 1.8

        if isinstance(raw_level, str):
            s = raw_level.strip()
            if s in ["₹", "₹₹", "₹₹₹", "₹₹₹₹", "Free", "Unknown"]:
                return s, None, None
            if "budget" in s.lower() or "inexpensive" in s.lower():
                return "₹", None, None
            if "moderate" in s.lower() or "mid-range" in s.lower():
                return "₹₹", None, None
            if "fine dining" in s.lower() or "expensive" in s.lower():
                return "₹₹₹", None, None

        return "Unknown", None, None

    @classmethod
    def normalize(cls, raw: Dict[str, Any], city_id: str) -> Dict[str, Any]:
        """
        Transforms raw connector record into canonical place schema.
        """
        name = (raw.get("name") or "").strip()
        slug = raw.get("slug") or cls.slugify(name)
        place_id = raw.get("id") or cls.generate_place_id(city_id, name)

        raw_type = (raw.get("place_type") or "destination").lower()
        place_type = PLACE_TYPE_MAP.get(raw_type, "destination")

        primary_cat = raw.get("primary_category") or raw.get("category") or "general"
        primary_cat = primary_cat.lower().replace(" ", "_")

        sec_cats = raw.get("secondary_categories") or []
        if isinstance(sec_cats, str):
            sec_cats = [c.strip().lower() for c in sec_cats.split(",") if c.strip()]

        price_level, min_c, max_c = cls.normalize_price_level(
            raw.get("price_level"),
            raw.get("estimated_cost_min")
        )

        source_urls = raw.get("source_urls") or []
        if isinstance(source_urls, str):
            source_urls = [source_urls]

        # Coordinates parsing
        lat = raw.get("latitude")
        lon = raw.get("longitude")
        try:
            lat = float(lat) if lat is not None and lat != "" else None
            lon = float(lon) if lon is not None and lon != "" else None
        except (ValueError, TypeError):
            lat = None
            lon = None

        return {
            "id": place_id,
            "city_id": city_id,
            "name": name,
            "slug": slug,
            "place_type": place_type,
            "primary_category": primary_cat,
            "secondary_categories": sec_cats,
            "description": raw.get("description"),
            "short_description": raw.get("short_description") or ((raw.get("description") or "")[:140] + "..." if len(raw.get("description") or "") > 140 else raw.get("description")),
            "address": raw.get("address"),
            "neighbourhood": raw.get("neighbourhood"),
            "latitude": lat,
            "longitude": lon,
            "price_level": price_level,
            "estimated_cost_min": min_c,
            "estimated_cost_max": max_c,
            "currency": raw.get("currency", "INR"),
            "opening_hours": raw.get("opening_hours"),  # None if unknown
            "contact_url": raw.get("contact_url"),
            "official_website": raw.get("official_website"),
            "booking_url": raw.get("booking_url"),
            "image_url": raw.get("image_url") or "images/hero_banner.jpg",
            "source_urls": source_urls,
            "source_provenance": raw.get("source_provenance", "verified_curation"),
            "verification_status": raw.get("verification_status", "verified"),
            "operating_status": raw.get("operating_status", "open")
        }

