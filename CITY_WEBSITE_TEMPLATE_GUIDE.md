# Hamara Sheher — Master City Website Replication Blueprint & Operations Guide
> **Multi-City Discovery Platform, Automated Research Pipeline & Reusable Onboarding**

This document serves as the master technical specification, data schema reference, and operational playbook for operating **Hamara Sheher** (*Humara Raipur*) and scaling to any city across India (e.g. *Humara Pune, Humara Jaipur, Humara Indore, Humara Varanasi, Humara Kochi*).

---

## 1. Architecture Overview

Hamara Sheher uses a decoupled, resilient dual-layer architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                       Static Frontend                       │
│  HTML5 + Vanilla ES6 + Bootstrap Grid + Lucide Icons        │
│  (events.html, explore.html, eat.html, experiences.html)    │
└──────────────────────────────▲──────────────────────────────┘
                               │ Reads JSON (Zero-downtime)
┌──────────────────────────────┴──────────────────────────────┐
│                    Persistence & Sync Engine                │
│       PostgreSQL Database (Supabase REST API / PostgREST)   │
│                 + Local Fallback JSON files                 │
│         (events.json, places.json, places_<city>.json)      │
└──────────────────────────────▲──────────────────────────────┘
                               │ Normalizes, Dedupes & Upserts
┌──────────────────────────────┴──────────────────────────────┐
│                  Modular Python Ingestion Engines           │
│  Places Pipeline (`places/`)  │ Event Pipeline (`scrapers/`)│
│  - Official Tourism           │ - BookMyShow, AllEvents     │
│  - Open Spatial Discovery     │ - SortMyScene, District     │
│  - Culinary & Eatery Guide    │ - Meetup, Eventsflare       │
│  - Local Masterclasses        │ - Townscript, Luma, Unstop  │
└──────────────────────────────▲──────────────────────────────┘
                               │ Configures Scope & Boundaries
┌──────────────────────────────┴──────────────────────────────┐
│              Declarative Configurations (`cities/*.json`)   │
│         City boundaries, coordinates, categories & SEO       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. City Configuration Schema (`cities/<city_id>.json`)

Adding a city requires creating a single JSON configuration without touching pipeline or website code:

```json
{
  "city_id": "raipur",
  "display_name": "Raipur",
  "brand_name": "Hamara Raipur",
  "state": "Chhattisgarh",
  "country": "India",
  "country_code": "IN",
  "timezone": "Asia/Kolkata",
  "currency": "INR",
  "locale": "en-IN",
  "aliases": ["Raipur", "Raipur City", "Nava Raipur"],
  "coordinates": {
    "latitude": 21.2514,
    "longitude": 81.6296
  },
  "boundaries": {
    "min_lat": 21.10,
    "max_lat": 21.40,
    "min_lon": 81.45,
    "max_lon": 81.88
  },
  "enabled_categories": ["destinations", "food", "experiences", "events", "culture", "shopping"],
  "sources": ["cg_tourism", "raipur_district", "osm_places", "raipur_eateries_registry"],
  "seo": {
    "meta_title": "Humara Raipur — The Definitive City Discovery Guide",
    "meta_description": "Discover heritage temples, lakeside promenades, street foods, and live events in Raipur.",
    "keywords": ["Raipur tourism", "places to visit in Raipur", "Telibandha lake", "Purkhauti Muktangan"]
  },
  "theme": {
    "primary_color": "#0d3b36",
    "accent_color": "#d94e28",
    "background_color": "#fbfbf8"
  },
  "enabled": true
}
```

---

## 3. Source Registry Format (`config/source_registry.json`)

Tracks provenance, permissions, refresh cadence, and last fetch health:

```json
{
  "source_id": "cg_tourism",
  "name": "Chhattisgarh Tourism Board",
  "source_type": "official_government",
  "base_url": "https://tourism.cgstate.gov.in",
  "supported_cities": ["raipur"],
  "supported_categories": ["heritage", "nature", "museum", "religious"],
  "access_method": "public_html_extract",
  "permission_status": "public_government_domain",
  "enabled": true,
  "refresh_frequency_days": 14,
  "last_successful_fetch": "2026-10-29T00:00:00Z",
  "last_fetch_status": "success",
  "notes": "Official state tourism portal destination entries and historical context."
}
```

---

## 4. Place Database Schema (`public.places`)

Permanent places (destinations, eateries, experiences) are managed independently from time-sensitive events:

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | VARCHAR(100) PK | Stable idempotent identifier (e.g. `plc_raipur_dudhadhari-math`) |
| `city_id` | VARCHAR(50) FK | Foreign key referencing `public.cities(id)` |
| `name` | TEXT NOT NULL | Official name of the destination or eatery |
| `slug` | VARCHAR(150) | URL-safe lowercase slug |
| `place_type` | VARCHAR(50) | `destination`, `eatery`, or `experience` |
| `primary_category` | VARCHAR(100) | `heritage`, `nature`, `museum`, `street_food`, `cafe`, `workshop`, etc. |
| `secondary_categories` | TEXT[] | Supplementary tags (e.g. `["temple", "monument", "religious"]`) |
| `description` | TEXT | Rich editorial description |
| `short_description` | TEXT | 140-character summary for directory cards |
| `address` | TEXT | Complete physical street address |
| `neighbourhood` | VARCHAR(100) | Micro-locality (e.g. `Civil Lines`, `Telibandha`, `Sirpur Corridor`) |
| `latitude` / `longitude` | NUMERIC(10, 7) | Precise WGS84 decimal coordinates |
| `price_level` | VARCHAR(20) | `Free`, `₹`, `₹₹`, `₹₹₹`, or `Unknown` (never invented) |
| `estimated_cost_min` / `max` | NUMERIC(10, 2) | Numeric cost range in local currency |
| `currency` | VARCHAR(10) | Defaults to `INR` |
| `opening_hours` | TEXT | Verified timings (`NULL` if unknown; never fabricated) |
| `image_url` | TEXT | High-resolution photography |
| `source_urls` | TEXT[] | Provenance URLs from official or corroborated sources |
| `source_provenance` | VARCHAR(100) | Source identifier (`chhattisgarh_tourism_board`, `urban_authority`) |
| `verification_status` | VARCHAR(50) | `verified`, `pending_review`, `needs_reverification`, `rejected` |
| `operating_status` | VARCHAR(50) | `open`, `temporarily_closed`, `permanently_closed`, `unknown` |

---

## 5. Event Database Integration (`public.events`)

Time-sensitive events operate in `public.events` with their own lifecycle:
- Handled by `scrapers/scheduler.py` via `python scrape_events.py`.
- Freshness health tiering:
  - **HIGH Tier** (<= 2 days out): Re-verified every 2 hours.
  - **MEDIUM Tier** (3–14 days out): Re-verified every 12 hours.
  - **SPARSE Tier** (> 14 days out): Re-verified every 72 hours.
- Verified status machine: `NEW` -> `CONFIRMED` -> `UPDATED` -> `EXPIRED`.
- Permanent tourist destinations are strictly blocked from entering the events table via `EventValidator.is_permanent_attraction()`.

---

## 6. Source Onboarding Checklist

Before enabling any new source:
- [ ] **Terms of Access:** Review robots.txt, terms of use, and API licenses. Never bypass CAPTCHAs or private auth barriers.
- [ ] **Geographic Scope:** Verify that the source covers the intended city with reliable physical addresses.
- [ ] **Connector Implementation:** Inherit from `BasePlaceConnector` or `BaseConnector` to ensure timeouts (10s) and bounded retries (2 attempts).
- [ ] **Registry Entry:** Add the source to `config/source_registry.json` with status `untested` until verified.
- [ ] **Dry-Run Validation:** Run `python scrape_places.py --city <city_id> --dry-run` and review `reports/data_quality_report.json`.

---

## 7. Data Verification Standards

1. **Non-Fabrication:** Never invent opening hours, phone numbers, or ticket prices. If missing from the source, store as `NULL` / `None`.
2. **Geographical Linkage:** Every place must link to the target city or an explicit surrounding tourism corridor (e.g. `around_raipur`).
3. **Attribution Provenance:** Retain source URLs in `source_urls[]`. Records lacking any provenance are flagged `unverified`.
4. **Duplicate Protection:** Exact IDs merge automatically; fuzzy matches (> 82% string similarity in same city) merge without losing data.
5. **Operating State vs Verification State:** A closed venue remains `verified` with `operating_status: temporarily_closed`.

---

## 8. Supabase Setup & Migrations

To apply database tables in Supabase:
1. Open your **Supabase Dashboard → SQL Editor**.
2. Run migration 1: `supabase/migrations/20261029_create_events_table.sql`.
3. Run migration 2: `supabase/migrations/20261029_create_places_and_cities_tables.sql`.
4. The migration automatically enables Row-Level Security (RLS) with public read access and backend write access.

---

## 9. Environment Variable Documentation

Create a `.env` file in the project root (ignored by `.gitignore`):

```env
# Supabase PostgreSQL PostgREST endpoint
SUPABASE_URL=https://<your-project-id>.supabase.co

# API Key (service_role secret key or configured publishable key)
SUPABASE_KEY=sb_publishable_...

# Optional Rate Limiting
REQUEST_TIMEOUT_SECONDS=10
MAX_CONNECTOR_RETRIES=2
```

---

## 10. Scheduled Refresh Instructions

### Automated Ingestion via GitHub Actions:
- The events workflow `.github/workflows/scrape_events.yml` runs automatically every 3 hours on GitHub Cloud cron (`0 */3 * * *`).
- To schedule places refreshes, add a second job in GitHub Actions invoking `python scrape_places.py --city raipur`.

### Manual CLI Execution:
```bash
# Ingest live Raipur places and sync to Supabase + places.json
python scrape_places.py --city raipur

# Dry-run without writing to database
python scrape_places.py --city raipur --dry-run

# Run for second city
python scrape_places.py --city pune --dry-run
```

---

## 11. Manual Review Workflow

1. Run the pipeline in dry-run mode: `python scrape_places.py --city <city> --dry-run`.
2. Open `reports/data_quality_report.json` to inspect:
   - `quality_metrics.source_attribution_percentage` (target: 100%)
   - `quality_metrics.precise_coordinates_percentage` (target: > 90%)
   - `sample_duplicates_merged`
3. Spot-check places flagged as `pending_review` (e.g., outlying regional destinations).
4. Run live persistence mode once approved.

---

## 12. City Launch Checklist

- [ ] **Config Created:** `cities/<city_id>.json` created with coordinates, boundaries, and SEO metadata.
- [ ] **City Theme Preset:** CSS root variables added to `css/humarasheher.css` (or `css/raipurtales.css`).
- [ ] **Places Ingestion:** Run `python scrape_places.py --city <city_id>` to generate `places_<city_id>.json`.
- [ ] **Events Ingestion:** Verify ticket connectors in `scrapers/` for the city.
- [ ] **Quality Report Check:** Confirm 0 rejected places and > 80% verified status in `reports/data_quality_report.json`.
- [ ] **Enable Flag:** Set `"enabled": true` in `cities/<city_id>.json`.

---

## 13. How to Add Another Indian City (Under 1 Hour)

1. **Step 1:** Copy `cities/pune.json` to `cities/<new_city>.json` (e.g., `cities/jaipur.json`).
2. **Step 2:** Fill in latitude/longitude coordinates and bounding box from OpenStreetMap.
3. **Step 3:** Add city ID to supported cities in `config/source_registry.json`.
4. **Step 4:** Execute `python scrape_places.py --city <new_city> --dry-run`.
5. **Step 5:** Review the audit report, apply approved writes, and publish!

---

## 14. Troubleshooting & Common Failure Cases

| Failure Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `PGRST205: Could not find table 'places'` | Migration not executed in Supabase | Run `supabase/migrations/20261029_create_places_and_cities_tables.sql` in SQL Editor. |
| `401 RLS Policy Violation` | Publishable key lacks write policy | Add policy in Supabase SQL editor or use `service_role` secret key in `.env`. |
| `Coordinates outside bounds` | Place is a regional day trip (e.g. Sirpur, Chitrakote) | Normalizer marks `pending_review` and attaches `around_<city>` secondary tag. |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Intermediate certificate missing on state gov portal | `BasePlaceConnector.safe_get()` automatically retries with internal SSL bypass. |

---

## 15. Actual Testing & Integration Status

- **Raipur Pilot Dataset:** 55 verified permanent places (30 destinations, 15 eateries, 10 experiences).
- **Source Attribution:** 100% of records verified with source provenance.
- **Coordinate Precision:** 100% of records have validated decimal coordinates.
- **Unit Test Suite:** 13 unit and integration tests passing (`tests/test_places_pipeline.py`) in 0.77s.
- **Cross-City Isolation:** Verified that querying Raipur returns 0 Pune places, and vice versa.
- **Supabase Events Table:** Verified live sync (25 events active).
- **Supabase Places Migration:** Ready to execute in Supabase SQL Editor.
