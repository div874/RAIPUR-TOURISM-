"""
Place Deduplicator.
Performs exact and fuzzy matching across multi-source places.
Preserves highest-fidelity provenance without overwriting strong data with poor data.
"""

import re
import difflib
from typing import List, Dict, Any, Tuple


class PlaceDeduplicator:
    """
    Deduplicates places across discovery sources.
    """

    @staticmethod
    def normalize_name(name: str) -> str:
        """Strips common place suffixes and punctuation for clean matching."""
        clean = (name or "").lower()
        clean = re.sub(r'\b(temple|mandir|restaurant|cafe|hotel|park|lake|sarovar|garden|complex)\b', '', clean)
        clean = re.sub(r'[^a-z0-9]', '', clean)
        return clean

    @classmethod
    def are_potential_duplicates(cls, p1: Dict[str, Any], p2: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Calculates similarity ratio between two place records in the same city.
        """
        if p1.get("city_id") != p2.get("city_id"):
            return False, 0.0

        n1 = cls.normalize_name(p1.get("name", ""))
        n2 = cls.normalize_name(p2.get("name", ""))

        if not n1 or not n2:
            return False, 0.0

        if n1 == n2:
            return True, 1.0

        ratio = difflib.SequenceMatcher(None, n1, n2).ratio()
        return ratio > 0.82, ratio

    @classmethod
    def merge(cls, primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges secondary into primary, retaining the highest quality information.
        """
        merged = dict(primary)

        # Merge source URLs
        p_urls = set(primary.get("source_urls") or [])
        s_urls = set(secondary.get("source_urls") or [])
        merged["source_urls"] = list(p_urls.union(s_urls))

        # Merge secondary categories
        p_sec = set(primary.get("secondary_categories") or [])
        s_sec = set(secondary.get("secondary_categories") or [])
        merged["secondary_categories"] = list(p_sec.union(s_sec))

        # Description: retain the richer/longer description
        if len(secondary.get("description") or "") > len(primary.get("description") or ""):
            merged["description"] = secondary.get("description")

        # Coordinates: fill if primary was missing
        if merged.get("latitude") is None and secondary.get("latitude") is not None:
            merged["latitude"] = secondary.get("latitude")
            merged["longitude"] = secondary.get("longitude")

        # Opening hours: fill if primary missing
        if not merged.get("opening_hours") and secondary.get("opening_hours"):
            merged["opening_hours"] = secondary.get("opening_hours")

        # Official website: fill if primary missing
        if not merged.get("official_website") and secondary.get("official_website"):
            merged["official_website"] = secondary.get("official_website")

        # Image: prefer non-default images
        if "hero_banner" in (merged.get("image_url") or "") and secondary.get("image_url") and "hero_banner" not in secondary["image_url"]:
            merged["image_url"] = secondary.get("image_url")

        return merged

    @classmethod
    def deduplicate(cls, place_pool: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Deduplicates a candidate pool. Returns (unique_places, duplicate_log).
        """
        unique_map: Dict[str, Dict[str, Any]] = {}
        duplicates_logged: List[Dict[str, Any]] = []

        for place in place_pool:
            place_id = place.get("id")
            if not place_id:
                continue

            # Exact ID check
            if place_id in unique_map:
                unique_map[place_id] = cls.merge(unique_map[place_id], place)
                duplicates_logged.append({
                    "type": "exact_id",
                    "id": place_id,
                    "name": place.get("name")
                })
                continue

            # Fuzzy name comparison within same city
            matched = False
            for existing_id, existing_place in list(unique_map.items()):
                is_dup, ratio = cls.are_potential_duplicates(existing_place, place)
                if is_dup:
                    unique_map[existing_id] = cls.merge(existing_place, place)
                    duplicates_logged.append({
                        "type": "fuzzy_name_match",
                        "ratio": round(ratio, 2),
                        "primary": existing_place.get("name"),
                        "secondary": place.get("name")
                    })
                    matched = True
                    break

            if not matched:
                unique_map[place_id] = place

        return list(unique_map.values()), duplicates_logged

