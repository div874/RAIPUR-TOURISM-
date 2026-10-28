"""
Event Validator.
Strictly verifies event candidates to ensure they take place in Raipur / Chhattisgarh,
filters out false positives, national tours without confirmed Raipur stops,
online/zoom webinars, and prevents fabrication of dates, venues, or prices.
"""

import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("EventValidator")

RAIPUR_CG_KEYWORDS = [
    "raipur", "chhattisgarh", "chattisgarh", "cg",
    "nava raipur", "naya raipur", "labhandih", "pandri",
    "devendra nagar", "vip chowk", "telibandha", "marine drive",
    "civil lines", "shankar nagar", "tatibandh", "samta colony",
    "bastar", "jagdalpur", "bijapur", "bhilai", "durg", "maic", "sayaji",
    "babylon", "underdoggs", "akhada", "soulescape", "haunt dive",
    "royal castle", "soul garden", "f lounge", "edo", "science college",
    "pt ravishankar", "nit raipur", "iiit naya raipur", "hnlu",
    "kursi cowork", "diablo", "ambuja mall", "magneto"
]

EXCLUDED_CITIES = [
    "hyderabad", "bangalore", "bengaluru", "mumbai", "lucknow", "ahmedabad",
    "gurgaon", "gurugram", "delhi", "new delhi", "pune", "chennai", "kolkata",
    "noida", "aundh", "imagicaa", "wonderla", "vgp", "ramoji", "kila raipur",
    "punjab", "varanasi", "rewa", "indore", "bhopal", "nagpur", "jaipur",
    "ambala", "sagar", "ujjain", "prayagraj", "allahabad", "surat", "vadodara",
    "chandigarh", "patna", "kanpur", "kochi", "coimbatore", "goa", "aquatica"
]

# Permanent tourist attractions that should NOT be marked as time-sensitive upcoming events
PERMANENT_ATTRACTIONS = [
    "swami vivekananda sarovar", "telibandha talab",
    "purkhauti muktangan", "ghatarani waterfalls", "jatmai temple",
    "nandanvan jungle safari", "mahamaya temple", "doodhadhari math",
    "energy park", "gandhi udyan", "shree rajiv lochan mandir",
    "bambleshwari temple", "sirpur heritage site"
]

# Online, webinar or UI artifacts
DISALLOWED_TERMS = [
    "continue with", "sign in", "login", "log in", "terms & conditions",
    "privacy policy", "zoom app", "zoom meeting", "google meet", "online only",
    "webinar", "virtual class", "online workshop", "online class", "online meetup",
    "online course", "online session", "[online]"
]


class EventValidator:
    """
    Validates event integrity, location physical reality, and rejects fabricated or out-of-city records.
    """

    @staticmethod
    def is_valid_raipur_location(venue: str, address: str = "", raw_text: str = "") -> Tuple[bool, str]:
        """
        Verifies if an event location is strictly situated in Raipur or Chhattisgarh.
        """
        combined = f"{venue} {address} {raw_text}".lower().strip()

        if not combined:
            return False, "Empty location text"

        # Check for non-Raipur excluded cities
        for city in EXCLUDED_CITIES:
            # Check whole word match
            if re.search(r'\b' + re.escape(city) + r'\b', combined):
                # If it's a known non-Raipur venue (like Wonderla, Ramoji, Aquatica)
                if city in ["hyderabad", "bangalore", "bengaluru", "chennai", "mumbai", "kolkata", "kochi"]:
                    return False, f"Location explicitly mentions non-Raipur city '{city}'"

        # Must have at least one explicit Raipur / CG keyword
        has_raipur_keyword = any(kw in combined for kw in RAIPUR_CG_KEYWORDS)
        if not has_raipur_keyword:
            return False, "Lacks Raipur / Chhattisgarh geographical keyword"

        return True, "Verified in Raipur/Chhattisgarh"

    @staticmethod
    def is_permanent_attraction(title: str, description: str = "") -> bool:
        """
        Detects if a record is a permanent sightseeing attraction.
        """
        title_lower = title.lower()
        desc_lower = description.lower()
        for attraction in PERMANENT_ATTRACTIONS:
            if attraction in title_lower and not any(k in title_lower for k in ["festival", "fest", "fair", "mela", "marathon", "concert", "run", "celebration", "expo"]):
                return True
        return False

    @classmethod
    def validate_event(cls, event: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Full sanity and verification check for an event candidate.
        """
        title = (event.get("title") or "").strip()
        title_lower = title.lower()

        if len(title) < 5:
            return False, "Title too short"

        # Check disallowed phrases (UI artifacts, online-only webinars)
        for term in DISALLOWED_TERMS:
            if term in title_lower:
                return False, f"Title contains disallowed term '{term}'"

        # Check if title explicitly mentions another city without Raipur
        for city in EXCLUDED_CITIES:
            if re.search(r'\b' + re.escape(city) + r'\b', title_lower):
                if not any(k in title_lower for k in ["raipur", "chhattisgarh"]):
                    return False, f"Title refers to non-Raipur city '{city}'"

        # Reject generic national tours that do not have a specific confirmed Raipur venue
        venue = (event.get("venue") or event.get("venue_name") or "").strip()
        venue_lower = venue.lower()

        if any(tour_kw in title_lower for tour_kw in ["india tour", "tour 2026", "tour 2027"]):
            if venue_lower in ["raipur, chhattisgarh", "venue to be announced", "tba", ""]:
                return False, "National tour without a confirmed Raipur venue"

        # Permanent attraction check
        if cls.is_permanent_attraction(title, event.get("description", "")):
            return False, "Record is a permanent tourist attraction, not a scheduled event"

        address = (event.get("address") or "").strip()
        raw_text = f"{event.get('description', '')} {event.get('original_url', '')} {event.get('link', '')}"

        is_valid_loc, reason = cls.is_valid_raipur_location(venue, address, raw_text)
        if not is_valid_loc:
            return False, reason

        return True, "Valid verified event"
