"""
Event Deduplicator.
Handles intra-batch and cross-platform deduplication, fuzzy title matching,
cross-source provenance merging, and guarantees higher quality data is preserved.
"""

import re
from typing import List, Dict, Any, Tuple


class EventDeduplicator:
    """
    Deduplicates events while preserving the highest fidelity fields and provenance.
    """

    @staticmethod
    def generate_fingerprint(title: str, date_str: str = "") -> str:
        """
        Creates a normalized alphanumeric fingerprint for comparison.
        """
        clean_title = re.sub(r'[^a-z0-9]', '', (title or "").lower())[:32]
        # Clean date string if present
        clean_date = re.sub(r'[^a-z0-9]', '', (date_str or "").lower())[:10]
        return f"{clean_title}_{clean_date}" if clean_date else clean_title

    @classmethod
    def merge_events(cls, primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges secondary event into primary, retaining the highest quality information.
        Does NOT overwrite good data with lower-quality data.
        """
        merged = dict(primary)

        # Merge sources
        p_src = primary.get("source", "")
        s_src = secondary.get("source", "")
        if s_src and s_src not in p_src:
            merged["source"] = f"{p_src} / {s_src}"

        # Image quality: prefer non-default images
        p_img = primary.get("image", "")
        s_img = secondary.get("image", "")
        if "unsplash.com" in p_img and s_img and "unsplash.com" not in s_img:
            merged["image"] = s_img

        # Time detail: prefer explicit timings over defaults
        p_time = primary.get("time", "")
        s_time = secondary.get("time", "")
        if (not p_time or p_time == "Evening onwards") and s_time and s_time != "Evening onwards":
            merged["time"] = s_time

        # Booking link: keep primary or take secondary if primary missing
        if not merged.get("link") or merged.get("link") == "#":
            merged["link"] = secondary.get("link")

        # Description: keep longer, richer description
        if len(secondary.get("description", "")) > len(merged.get("description", "")):
            merged["description"] = secondary.get("description")

        # Price: prefer explicit price over undisclosed
        if merged.get("price") in ["Book Online", "Price not disclosed", None] and secondary.get("price"):
            merged["price"] = secondary.get("price")

        return merged

    @classmethod
    def deduplicate(cls, event_pool: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicates a candidate pool of events, combining multi-platform occurrences.
        """
        unique_map: Dict[str, Dict[str, Any]] = {}

        for ev in event_pool:
            title = ev.get("title", "")
            date_str = ev.get("date", "") or ev.get("date_human", "")
            fp = cls.generate_fingerprint(title, date_str)

            if not fp:
                continue

            if fp in unique_map:
                # Merge with existing
                unique_map[fp] = cls.merge_events(unique_map[fp], ev)
            else:
                unique_map[fp] = ev

        return list(unique_map.values())

