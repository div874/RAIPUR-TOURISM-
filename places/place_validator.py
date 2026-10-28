"""
Place Validator.
Ensures place physical reality, city geographic boundaries,
operating status integrity, and valid verification classification.
"""

import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("PlaceValidator")

CITY_KEYWORDS = {
    "raipur": [
        "raipur", "chhattisgarh", "chattisgarh", "naya raipur", "nava raipur",
        "telibandha", "gole bazaar", "pandri", "civil lines", "shankar nagar",
        "samta colony", "devendra nagar", "vip road", "tatibandh", "sirpur",
        "champaran", "purkhauti", "durg", "bhilai", "bastar"
    ],
    "pune": [
        "pune", "maharashtra", "kothrud", "deccan", "viman nagar", "baner",
        "aundh", "wakad", "hinjewadi", "koregaon park", "camp", "shivajinagar",
        "swargate", "hadapsar", "pcmc"
    ]
}


class PlaceValidator:
    """
    Validates permanent places for geographical fidelity, completeness, and non-fabrication.
    """

    @classmethod
    def validate(cls, place: Dict[str, Any], city_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Validates that a place is legitimate, correctly localized, and not an upcoming event.
        """
        name = (place.get("name") or "").strip()
        if len(name) < 3:
            return False, "Place name is missing or too short"

        city_id = place.get("city_id", "").lower()
        address = (place.get("address") or "").lower()
        description = (place.get("description") or "").lower()
        combined = f"{name} {address} {description}".lower()

        # Check city keyword presence if known city
        if city_id in CITY_KEYWORDS:
            keywords = CITY_KEYWORDS[city_id]
            if not any(kw in combined for kw in keywords):
                return False, f"Place lacks geographical linkage to {city_id}"

        # Coordinate bounding box check if city_config provides boundaries
        if city_config and "boundaries" in city_config:
            b = city_config["boundaries"]
            lat = place.get("latitude")
            lon = place.get("longitude")
            if lat is not None and lon is not None:
                if not (b["min_lat"] <= lat <= b["max_lat"] and b["min_lon"] <= lon <= b["max_lon"]):
                    logger.warning(f"Coordinates ({lat}, {lon}) outside bounds for {name}")
                    # Mark for review rather than hard reject if address is local
                    place["verification_status"] = "pending_review"

        # Check for event confusion (places should not be time-specific movies or single-day gigs)
        if any(w in name.lower() for w in ["standup special", "live concert", "dj night on", "tour 2026", "vs match"]):
            return False, "Record appears to be an upcoming event, not a permanent place"

        return True, "Valid place"

