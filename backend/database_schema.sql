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

-- Indexes for performance
CREATE INDEX idx_classified_data_tweet_id ON classified_data(tweet_id);
CREATE INDEX idx_classified_data_image_id ON classified_data(image_id);
CREATE INDEX idx_classified_data_text_info ON classified_data(text_info);
CREATE INDEX idx_classified_data_image_info ON classified_data(image_info);
CREATE INDEX idx_classified_data_text_human ON classified_data(text_human);
CREATE INDEX idx_classified_data_image_human ON classified_data(image_human);
CREATE INDEX idx_classified_data_image_damage ON classified_data(image_damage);
CREATE INDEX idx_classified_data_created_at ON classified_data(created_at);

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

-- Row Level Security (RLS) policies
ALTER TABLE classified_data ENABLE ROW LEVEL SECURITY;

-- Policy to allow all operations for authenticated users
CREATE POLICY "Allow all operations for authenticated users" ON classified_data
    FOR ALL USING (auth.role() = 'authenticated');

-- Policy to allow all operations for service role
CREATE POLICY "Allow all operations for service role" ON classified_data
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
COMMENT ON VIEW informative_data IS 'Quick access to informative tweets (text or image)';
COMMENT ON VIEW humanitarian_data IS 'Quick access to tweets with humanitarian classifications';
COMMENT ON VIEW damage_assessment_data IS 'Quick access to tweets with damage assessments'; 