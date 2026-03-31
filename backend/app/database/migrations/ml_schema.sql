-- ML Schema for Hotel Reviews Integration
-- Creates tables for training data storage and model management

-- 1. ml_training_reviews: Stores labeled review data
CREATE TABLE IF NOT EXISTS ml_training_reviews (
    id SERIAL PRIMARY KEY,
    business_type_id INTEGER NOT NULL CHECK (business_type_id IN (1, 2)),
    review_text TEXT NOT NULL,
    main_label VARCHAR(50),
    second_label VARCHAR(50),
    third_label VARCHAR(50),
    detected_language VARCHAR(5),
    is_hand_labelled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster queries by business type
CREATE INDEX IF NOT EXISTS idx_ml_training_reviews_business_type 
    ON ml_training_reviews(business_type_id);

-- Index for language-based queries
CREATE INDEX IF NOT EXISTS idx_ml_training_reviews_language 
    ON ml_training_reviews(detected_language);

-- 2. ml_categories: Defines categories for each business type
CREATE TABLE IF NOT EXISTS ml_categories (
    id SERIAL PRIMARY KEY,
    business_type_id INTEGER NOT NULL CHECK (business_type_id IN (1, 2)),
    category_name VARCHAR(50) NOT NULL,
    label_rank INTEGER NOT NULL CHECK (label_rank BETWEEN 1 AND 3),
    UNIQUE (business_type_id, category_name, label_rank)
);

-- Insert default hotel categories (business_type_id = 1)
INSERT INTO ml_categories (business_type_id, category_name, label_rank) VALUES
(1, 'room', 1), (1, 'room', 2), (1, 'room', 3),
(1, 'service', 1), (1, 'service', 2), (1, 'service', 3),
(1, 'food', 1), (1, 'food', 2), (1, 'food', 3),
(1, 'clean', 1), (1, 'clean', 2), (1, 'clean', 3),
(1, 'location', 1), (1, 'location', 2), (1, 'location', 3),
(1, 'amenities', 1), (1, 'amenities', 2), (1, 'amenities', 3),
(1, 'value', 1), (1, 'value', 2), (1, 'value', 3),
(1, 'other', 1), (1, 'other', 2), (1, 'other', 3)
ON CONFLICT DO NOTHING;

-- Insert default restaurant categories (business_type_id = 2)
INSERT INTO ml_categories (business_type_id, category_name, label_rank) VALUES
(2, 'food_quality', 1), (2, 'food_quality', 2), (2, 'food_quality', 3),
(2, 'service_quality', 1), (2, 'service_quality', 2), (2, 'service_quality', 3),
(2, 'ambience', 1), (2, 'ambience', 2), (2, 'ambience', 3),
(2, 'cleanliness', 1), (2, 'cleanliness', 2), (2, 'cleanliness', 3),
(2, 'value_for_money', 1), (2, 'value_for_money', 2), (2, 'value_for_money', 3),
(2, 'location_convenience', 1), (2, 'location_convenience', 2), (2, 'location_convenience', 3),
(2, 'wait_time', 1), (2, 'wait_time', 2), (2, 'wait_time', 3),
(2, 'hygiene_safety', 1), (2, 'hygiene_safety', 2), (2, 'hygiene_safety', 3),
(2, 'dietary_options', 1), (2, 'dietary_options', 2), (2, 'dietary_options', 3)
ON CONFLICT DO NOTHING;

-- 3. ml_models: Model metadata and versions
CREATE TABLE IF NOT EXISTS ml_models (
    id SERIAL PRIMARY KEY,
    business_type_id INTEGER NOT NULL CHECK (business_type_id IN (1, 2)),
    model_version VARCHAR(20) NOT NULL,
    trained_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accuracy FLOAT,
    UNIQUE (business_type_id, model_version)
);

-- Index for model lookup
CREATE INDEX IF NOT EXISTS idx_ml_models_business_type 
    ON ml_models(business_type_id);