-- Add ML columns to reviews table
ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS auto_labels JSONB,
ADD COLUMN IF NOT EXISTS detected_language VARCHAR(5);