-- =========================================================================
-- Hamara Sheher / Raipur Multi-Source Event Aggregation Schema
-- Migration: 20261029_create_events_table.sql
-- =========================================================================

CREATE TABLE IF NOT EXISTS public.events (
    id VARCHAR(100) PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_event_id VARCHAR(150),
    original_url TEXT,
    booking_url TEXT,
    title TEXT NOT NULL,
    description TEXT,
    city VARCHAR(100) DEFAULT 'Raipur',
    state VARCHAR(100) DEFAULT 'Chhattisgarh',
    venue_name TEXT,
    address TEXT,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    start_datetime TIMESTAMPTZ,
    end_datetime TIMESTAMPTZ,
    date_human VARCHAR(100),
    time_human VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    price_min NUMERIC(10, 2),
    price_max NUMERIC(10, 2),
    price_type VARCHAR(50) DEFAULT 'undisclosed', -- 'free', 'paid', 'undisclosed', 'registration_required', 'unknown'
    currency VARCHAR(10) DEFAULT 'INR',
    category VARCHAR(100) DEFAULT 'Shows',        -- 'Sports', 'Culture', 'Clubs', 'Shows'
    tags TEXT[] DEFAULT '{}',
    image_url TEXT,
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_verified_at TIMESTAMPTZ DEFAULT NOW(),
    verification_status VARCHAR(50) DEFAULT 'CONFIRMED', -- 'NEW', 'CONFIRMED', 'UPDATED', 'EXPIRED'
    lifecycle_status VARCHAR(50) DEFAULT 'UPCOMING',    -- 'UPCOMING', 'LIVE', 'COMPLETED', 'CANCELLED'
    freshness_tier VARCHAR(20) DEFAULT 'MEDIUM',        -- 'HIGH', 'MEDIUM', 'SPARSE'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performant filtering and deduplication
CREATE INDEX IF NOT EXISTS idx_events_city_start ON public.events (city, start_datetime);
CREATE INDEX IF NOT EXISTS idx_events_verification_status ON public.events (verification_status);
CREATE INDEX IF NOT EXISTS idx_events_category ON public.events (category);
CREATE INDEX IF NOT EXISTS idx_events_source ON public.events (source_name, source_event_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;

-- Policy 1: Allow public read-only access for all clients (website visitors, anon key)
DROP POLICY IF EXISTS "Public read access for verified events" ON public.events;
CREATE POLICY "Public read access for verified events"
ON public.events
FOR SELECT
USING (true);

-- Policy 2: Allow service role full access for scraper ingest and updates
DROP POLICY IF EXISTS "Service role write access for ingestion pipeline" ON public.events;
CREATE POLICY "Service role write access for ingestion pipeline"
ON public.events
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Policy 3: Allow publishable/anon key write access (for automated script updates with publishable key)
DROP POLICY IF EXISTS "Anon write access for ingestion pipeline" ON public.events;
CREATE POLICY "Anon write access for ingestion pipeline"
ON public.events
FOR ALL
TO anon, authenticated
USING (true)
WITH CHECK (true);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_events_updated_at ON public.events;
CREATE TRIGGER trg_events_updated_at
BEFORE UPDATE ON public.events
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
