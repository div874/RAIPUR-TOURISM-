"""
Comprehensive Unit & Integration Test Suite for Hamara Sheher Places Pipeline.
Tests normalization, deduplication, validation, unknown handling, city isolation,
and event pipeline compatibility.
"""

import unittest
from places.place_normalizer import PlaceNormalizer
from places.place_validator import PlaceValidator
from places.place_deduplicator import PlaceDeduplicator
from places.refresh_scheduler import PlacePipelineScheduler
from scrapers.event_validator import EventValidator


class TestPlaceNormalization(unittest.TestCase):

    def test_slugify(self):
        self.assertEqual(PlaceNormalizer.slugify("Dudhadhari Math & Temple"), "dudhadhari-math-temple")
        self.assertEqual(PlaceNormalizer.slugify("Gole Bazaar! 18th-Century"), "gole-bazaar-18th-century")

    def test_id_generation(self):
        place_id = PlaceNormalizer.generate_place_id("raipur", "Telibandha Marine Drive")
        self.assertEqual(place_id, "plc_raipur_telibandha-marine-drive")

    def test_unknown_price_preservation(self):
        level, min_c, max_c = PlaceNormalizer.normalize_price_level("Unknown", None)
        self.assertEqual(level, "Unknown")
        self.assertIsNone(min_c)
        self.assertIsNone(max_c)

    def test_free_price_level(self):
        level, min_c, max_c = PlaceNormalizer.normalize_price_level("Free", 0.0)
        self.assertEqual(level, "Free")
        self.assertEqual(min_c, 0.0)
        self.assertEqual(max_c, 0.0)

    def test_unknown_hours_preserved_as_none(self):
        raw = {
            "name": "Local Secret Viewpoint",
            "address": "Raipur, Chhattisgarh"
            # opening_hours omitted
        }
        normalized = PlaceNormalizer.normalize(raw, "raipur")
        self.assertIsNone(normalized.get("opening_hours"))


class TestPlaceValidation(unittest.TestCase):

    def test_short_name_rejected(self):
        place = {"name": "AB", "city_id": "raipur", "address": "Raipur, Chhattisgarh"}
        is_valid, reason = PlaceValidator.validate(place)
        self.assertFalse(is_valid)
        self.assertIn("too short", reason)

    def test_out_of_city_place_rejected(self):
        place = {
            "name": "Marine Drive Promenade",
            "city_id": "raipur",
            "address": "Bandra West, Mumbai, Maharashtra"
        }
        is_valid, reason = PlaceValidator.validate(place)
        self.assertFalse(is_valid)
        self.assertIn("lacks geographical linkage", reason)

    def test_valid_raipur_place(self):
        place = {
            "name": "Dudhadhari Math",
            "city_id": "raipur",
            "address": "Maharajbandh Lake, Raipur, Chhattisgarh"
        }
        is_valid, _ = PlaceValidator.validate(place)
        self.assertTrue(is_valid)

    def test_event_not_treated_as_permanent_place(self):
        place = {
            "name": "Arijit Singh Live Concert 2026",
            "city_id": "raipur",
            "address": "Science College Ground, Raipur"
        }
        is_valid, reason = PlaceValidator.validate(place)
        self.assertFalse(is_valid)
        self.assertIn("upcoming event", reason)


class TestPlaceDeduplication(unittest.TestCase):

    def test_exact_id_merging(self):
        p1 = {
            "id": "plc_raipur_dudhadhari-math",
            "name": "Dudhadhari Math",
            "city_id": "raipur",
            "description": "Short desc",
            "source_urls": ["url1"]
        }
        p2 = {
            "id": "plc_raipur_dudhadhari-math",
            "name": "Dudhadhari Math Complex",
            "city_id": "raipur",
            "description": "Much longer and richer description of 17th century monastery",
            "source_urls": ["url2"]
        }
        deduped, logs = PlaceDeduplicator.deduplicate([p1, p2])
        self.assertEqual(len(deduped), 1)
        self.assertEqual(len(logs), 1)
        self.assertEqual(deduped[0]["description"], p2["description"])
        self.assertEqual(len(deduped[0]["source_urls"]), 2)

    def test_fuzzy_name_matching(self):
        p1 = {
            "id": "plc_raipur_gandhi-udyan",
            "name": "Gandhi Udyan Park",
            "city_id": "raipur"
        }
        p2 = {
            "id": "plc_raipur_gandhi-udyan-garden",
            "name": "Gandhi Udyan Garden",
            "city_id": "raipur"
        }
        is_dup, ratio = PlaceDeduplicator.are_potential_duplicates(p1, p2)
        self.assertTrue(is_dup)
        self.assertGreater(ratio, 0.82)


class TestCrossCityIsolation(unittest.TestCase):

    def test_city_filter_isolation(self):
        scheduler_raipur = PlacePipelineScheduler(city_id="raipur")
        res_raipur = scheduler_raipur.run(dry_run=True)
        places_raipur = res_raipur["places"]

        # Ensure all records belong exclusively to raipur
        for p in places_raipur:
            self.assertEqual(p["city_id"], "raipur")

        scheduler_pune = PlacePipelineScheduler(city_id="pune")
        res_pune = scheduler_pune.run(dry_run=True)
        places_pune = res_pune["places"]

        for p in places_pune:
            self.assertEqual(p["city_id"], "pune")


class TestEventPipelineCompatibility(unittest.TestCase):

    def test_event_validator_permanent_attraction_detection(self):
        # Ensure event pipeline continues to reject permanent tourist spots from event feed
        self.assertTrue(EventValidator.is_permanent_attraction("Visit Purkhauti Muktangan"))
        self.assertTrue(EventValidator.is_permanent_attraction("Nandanvan Jungle Safari Sightseeing"))
        # But allows legitimate festivals
        self.assertFalse(EventValidator.is_permanent_attraction("Purkhauti Muktangan Tribal Folk Fest 2026"))


if __name__ == "__main__":
    unittest.main()

