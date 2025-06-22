-- Crisis-MMD Database Schema
-- This schema stores classified tweet data matching the CrisisMMD dataset structure

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types for classification labels
CREATE TYPE informative_label AS ENUM (
    'informative',
    'not_informative',
    'dont_know_or_cant_judge'
);

CREATE TYPE humanitarian_label AS ENUM (
    'affected_individuals',
    'infrastructure_and_utility_damage',
    'injured_or_dead_people',
    'missing_or_found_people',
    'rescue_volunteering_or_donation_effort',
    'vehicle_damage',
    'other_relevant_information',
    'not_humanitarian'
);

CREATE TYPE damage_label AS ENUM (
    'severe_damage',
    'mild_damage',
    'little_or_no_damage',
    'dont_know_or_cant_judge'
);

-- Main classified_data table - stores all classified tweet data
CREATE TABLE classified_data (
    id BIGSERIAL PRIMARY KEY,
    
    -- Tweet identifiers
    tweet_id BIGINT NOT NULL,
    image_id TEXT NOT NULL,
    
    -- Text classification
    text_info informative_label NOT NULL,
    text_info_conf DECIMAL(4,3) NOT NULL CHECK (text_info_conf >= 0.0 AND text_info_conf <= 1.0),
    
    -- Image classification
    image_info informative_label,
    image_info_conf DECIMAL(4,3) CHECK (image_info_conf IS NULL OR (image_info_conf >= 0.0 AND image_info_conf <= 1.0)),
    
    -- Text humanitarian classification
    text_human humanitarian_label,
    text_human_conf DECIMAL(4,3) CHECK (text_human_conf IS NULL OR (text_human_conf >= 0.0 AND text_human_conf <= 1.0)),
    
    -- Image humanitarian classification
    image_human humanitarian_label,
    image_human_conf DECIMAL(4,3) CHECK (image_human_conf IS NULL OR (image_human_conf >= 0.0 AND image_human_conf <= 1.0)),
    
    -- Image damage assessment
    image_damage damage_label,
    image_damage_conf DECIMAL(4,3) CHECK (image_damage_conf IS NULL OR (image_damage_conf >= 0.0 AND image_damage_conf <= 1.0)),
    
    -- Tweet content
    tweet_text TEXT NOT NULL CHECK (length(tweet_text) > 0),
    image_url TEXT,
    image_path TEXT,
    location TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_image_id UNIQUE (image_id),
    CONSTRAINT valid_image_id_format CHECK (image_id ~ '^[0-9]+_[0-9]+$')
);

-- Users table - stores user profiles for crisis alert system
-- Extends Supabase Auth users with additional profile information
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL CHECK (length(name) > 0),
    phone_number TEXT NOT NULL UNIQUE CHECK (phone_number ~ '^\+?[1-9]\d{8,14}$'),
    location JSONB NOT NULL CHECK (
        location ? 'lat' AND 
        location ? 'lng' AND 
        location ? 'address' AND
        (location->>'lat')::NUMERIC BETWEEN -90 AND 90 AND
        (location->>'lng')::NUMERIC BETWEEN -180 AND 180
    ),
    emergency_contacts JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (
        jsonb_typeof(emergency_contacts) = 'array'
    ),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_classified_data_tweet_id ON classified_data(tweet_id);
CREATE INDEX idx_classified_data_image_id ON classified_data(image_id);
CREATE INDEX idx_classified_data_text_info ON classified_data(text_info);
CREATE INDEX idx_classified_data_image_info ON classified_data(image_info);
CREATE INDEX idx_classified_data_text_human ON classified_data(text_human);
CREATE INDEX idx_classified_data_image_human ON classified_data(image_human);
CREATE INDEX idx_classified_data_image_damage ON classified_data(image_damage);
CREATE INDEX idx_classified_data_created_at ON classified_data(created_at);

-- User table indexes
CREATE INDEX idx_users_phone_number ON users(phone_number);
CREATE INDEX idx_users_location_lat_lng ON users USING GIN ((location->'lat'), (location->'lng'));
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_classified_data_updated_at 
    BEFORE UPDATE ON classified_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW informative_data AS
SELECT * FROM classified_data 
WHERE text_info = 'informative' OR image_info = 'informative'
ORDER BY created_at DESC;

CREATE VIEW humanitarian_data AS
SELECT * FROM classified_data 
WHERE text_human IS NOT NULL OR image_human IS NOT NULL
ORDER BY created_at DESC;

CREATE VIEW damage_assessment_data AS
SELECT * FROM classified_data 
WHERE image_damage IS NOT NULL
ORDER BY created_at DESC;

CREATE VIEW high_confidence_text AS
SELECT * FROM classified_data 
WHERE text_info_conf >= 0.8
ORDER BY text_info_conf DESC, created_at DESC;

CREATE VIEW high_confidence_image AS
SELECT * FROM classified_data 
WHERE image_info_conf >= 0.8
ORDER BY image_info_conf DESC, created_at DESC;

-- User views
CREATE VIEW active_users AS
SELECT * FROM users 
WHERE is_active = true
ORDER BY created_at DESC;

-- Row Level Security (RLS) policies
ALTER TABLE classified_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Classified data policies
CREATE POLICY "Allow all operations for authenticated users" ON classified_data
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for service role" ON classified_data
    FOR ALL USING (auth.role() = 'service_role');

-- User policies
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Allow user creation during signup" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Service role can access all users" ON users
    FOR ALL USING (auth.role() = 'service_role');

-- Comments for documentation
COMMENT ON TABLE classified_data IS 'Stores classified tweet data matching CrisisMMD dataset structure';
COMMENT ON COLUMN classified_data.tweet_id IS 'Original Twitter tweet ID';
COMMENT ON COLUMN classified_data.image_id IS 'Tweet ID combined with image index (tweet_id_index)';
COMMENT ON COLUMN classified_data.text_info IS 'Informative classification for tweet text';
COMMENT ON COLUMN classified_data.text_info_conf IS 'Confidence score for text informative classification';
COMMENT ON COLUMN classified_data.image_info IS 'Informative classification for tweet image';
COMMENT ON COLUMN classified_data.image_info_conf IS 'Confidence score for image informative classification';
COMMENT ON COLUMN classified_data.text_human IS 'Humanitarian classification for tweet text';
COMMENT ON COLUMN classified_data.text_human_conf IS 'Confidence score for text humanitarian classification';
COMMENT ON COLUMN classified_data.image_human IS 'Humanitarian classification for tweet image';
COMMENT ON COLUMN classified_data.image_human_conf IS 'Confidence score for image humanitarian classification';
COMMENT ON COLUMN classified_data.image_damage IS 'Damage severity assessment for tweet image';
COMMENT ON COLUMN classified_data.image_damage_conf IS 'Confidence score for image damage assessment';

COMMENT ON TABLE users IS 'User profiles for crisis alert system, extends Supabase Auth';
COMMENT ON COLUMN users.id IS 'References auth.users(id) from Supabase Auth';
COMMENT ON COLUMN users.name IS 'Full name of the user';
COMMENT ON COLUMN users.phone_number IS 'Phone number in international format, used for auth and calling';
COMMENT ON COLUMN users.location IS 'User location as JSONB: {lat, lng, address}';
COMMENT ON COLUMN users.emergency_contacts IS 'Array of emergency contacts: [{name, phone, relationship}]';
COMMENT ON COLUMN users.is_active IS 'Whether user should receive crisis alerts';

COMMENT ON VIEW informative_data IS 'Quick access to informative tweets (text or image)';
COMMENT ON VIEW humanitarian_data IS 'Quick access to tweets with humanitarian classifications';
COMMENT ON VIEW damage_assessment_data IS 'Quick access to tweets with damage assessments';
COMMENT ON VIEW active_users IS 'Quick access to active users who can receive alerts'; 