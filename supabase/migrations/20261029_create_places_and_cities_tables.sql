-- =========================================================================
-- Hamara Sheher - City Discovery & Unified Places Database Schema
-- Migration: 20261029_create_places_and_cities_tables.sql
-- =========================================================================

-- 1. Cities Registry Table
CREATE TABLE IF NOT EXISTS public.cities (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    country_code VARCHAR(10) DEFAULT 'IN',
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    currency VARCHAR(10) DEFAULT 'INR',
    brand_name VARCHAR(100),
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed default pilot cities
INSERT INTO public.cities (id, name, state, brand_name, enabled)
VALUES 
    ('raipur', 'Raipur', 'Chhattisgarh', 'Hamara Raipur', true),
    ('pune', 'Pune', 'Maharashtra', 'Hamara Pune', false)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    state = EXCLUDED.state,
    brand_name = EXCLUDED.brand_name;

-- 2. Permanent Places Database Table
CREATE TABLE IF NOT EXISTS public.places (
    id VARCHAR(100) PRIMARY KEY,
    city_id VARCHAR(50) NOT NULL REFERENCES public.cities(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug VARCHAR(150),
    place_type VARCHAR(50) NOT NULL,            -- 'destination', 'eatery', 'experience'
    primary_category VARCHAR(100) NOT NULL,      -- 'heritage', 'nature', 'museum', 'street_food', 'cafe', 'fine_dining', 'workshop', etc.
    secondary_categories TEXT[] DEFAULT '{}',
    description TEXT,
    short_description TEXT,
    address TEXT,
    neighbourhood VARCHAR(100),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    price_level VARCHAR(20) DEFAULT 'Unknown',   -- 'Free', '₹', '₹₹', '₹₹₹', 'Unknown'
    estimated_cost_min NUMERIC(10, 2),
    estimated_cost_max NUMERIC(10, 2),
    currency VARCHAR(10) DEFAULT 'INR',
    opening_hours TEXT,
    contact_url TEXT,
    official_website TEXT,
    booking_url TEXT,
    image_url TEXT,
    source_urls TEXT[] DEFAULT '{}',
    source_provenance VARCHAR(100) NOT NULL,
    verification_status VARCHAR(50) DEFAULT 'verified', -- 'unverified', 'pending_review', 'verified', 'needs_reverification', 'rejected'
    operating_status VARCHAR(50) DEFAULT 'open',        -- 'open', 'temporarily_closed', 'permanently_closed', 'unknown'
    last_verified_at TIMESTAMPTZ DEFAULT NOW(),
    last_checked_at TIMESTAMPTZ DEFAULT NOW(),
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for lightning fast spatial, city, and category discovery
CREATE INDEX IF NOT EXISTS idx_places_city_type ON public.places (city_id, place_type);
CREATE INDEX IF NOT EXISTS idx_places_city_category ON public.places (city_id, primary_category);
CREATE INDEX IF NOT EXISTS idx_places_verification ON public.places (verification_status);
CREATE INDEX IF NOT EXISTS idx_places_operating ON public.places (operating_status);
CREATE INDEX IF NOT EXISTS idx_places_slug ON public.places (slug);

-- Enable Row Level Security (RLS)
ALTER TABLE public.cities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.places ENABLE ROW LEVEL SECURITY;

-- Policies for Cities
DROP POLICY IF EXISTS "Public read access for cities" ON public.cities;
CREATE POLICY "Public read access for cities" ON public.cities FOR SELECT USING (true);

DROP POLICY IF EXISTS "Write access for cities pipeline" ON public.cities;
CREATE POLICY "Write access for cities pipeline" ON public.cities FOR ALL TO anon, authenticated, service_role USING (true) WITH CHECK (true);

-- Policies for Places
DROP POLICY IF EXISTS "Public read access for verified places" ON public.places;
CREATE POLICY "Public read access for verified places" ON public.places FOR SELECT USING (true);

DROP POLICY IF EXISTS "Write access for places ingestion pipeline" ON public.places;
CREATE POLICY "Write access for places ingestion pipeline" ON public.places FOR ALL TO anon, authenticated, service_role USING (true) WITH CHECK (true);

-- Updated_at triggers
DROP TRIGGER IF EXISTS trg_places_updated_at ON public.places;
CREATE TRIGGER trg_places_updated_at
BEFORE UPDATE ON public.places
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

