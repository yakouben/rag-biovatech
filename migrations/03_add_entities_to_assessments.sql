-- Migration: Add clinical_entities column to patient_assessments
-- This supports structured data extraction from Nour conversations

ALTER TABLE patient_assessments 
ADD COLUMN IF NOT EXISTS clinical_entities JSONB DEFAULT '{}'::jsonb;

-- Update indexes for performance
CREATE INDEX IF NOT EXISTS idx_assessments_entities ON patient_assessments USING GIN (clinical_entities);
