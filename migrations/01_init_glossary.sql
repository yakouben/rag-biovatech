-- ChronicCare Medical Glossary Schema Initialization
-- Creates tables for storing Darija medical glossary with pgvector support

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Medical Glossary Table
CREATE TABLE IF NOT EXISTS medical_glossary (
    id BIGINT PRIMARY KEY DEFAULT gen_random_bigint(),
    darija TEXT NOT NULL,
    french TEXT NOT NULL,
    english TEXT NOT NULL,
    category TEXT NOT NULL,
    embedding vector(768),  -- Gemini embedding dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT medical_glossary_unique UNIQUE(darija, english)
);

-- Create index on category for faster filtering
CREATE INDEX IF NOT EXISTS idx_glossary_category ON medical_glossary(category);

-- Create index on embedding for vector similarity search
CREATE INDEX IF NOT EXISTS idx_glossary_embedding ON medical_glossary USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create index on full text search columns
CREATE INDEX IF NOT EXISTS idx_glossary_darija ON medical_glossary USING GIN(to_tsvector('arabic', darija));
CREATE INDEX IF NOT EXISTS idx_glossary_french ON medical_glossary USING GIN(to_tsvector('french', french));
CREATE INDEX IF NOT EXISTS idx_glossary_english ON medical_glossary USING GIN(to_tsvector('english', english));

-- RPC function for similarity search
CREATE OR REPLACE FUNCTION search_glossary_embedding(
    query_embedding vector,
    match_count INT DEFAULT 10,
    similarity_threshold FLOAT DEFAULT 0.3
)
RETURNS TABLE (
    id BIGINT,
    darija TEXT,
    french TEXT,
    english TEXT,
    category TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        g.id,
        g.darija,
        g.french,
        g.english,
        g.category,
        (1 - (g.embedding <=> query_embedding))::FLOAT as similarity
    FROM medical_glossary g
    WHERE g.embedding IS NOT NULL
        AND (1 - (g.embedding <=> query_embedding)) > similarity_threshold
    ORDER BY g.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Patient Assessment Records (for tracking predictions and drift)
CREATE TABLE IF NOT EXISTS patient_assessments (
    id BIGINT PRIMARY KEY DEFAULT gen_random_bigint(),
    patient_id TEXT NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    symptoms TEXT,
    predicted_risk_level INT,
    actual_risk_level INT,
    risk_score FLOAT,
    confidence FLOAT,
    is_correct BOOLEAN,
    glossary_terms_used TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT assessments_patient_fk FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- Create index for patient queries
CREATE INDEX IF NOT EXISTS idx_assessments_patient ON patient_assessments(patient_id);
CREATE INDEX IF NOT EXISTS idx_assessments_date ON patient_assessments(assessment_date DESC);
CREATE INDEX IF NOT EXISTS idx_assessments_risk ON patient_assessments(predicted_risk_level);

-- Patient Records Table
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INT,
    gender TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model Performance Metrics (for drift detection)
CREATE TABLE IF NOT EXISTS model_metrics (
    id BIGINT PRIMARY KEY DEFAULT gen_random_bigint(),
    metric_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    total_predictions INT,
    by_risk_category JSONB,  -- Metrics broken down by risk category
    drift_detected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_date ON model_metrics(metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_drift ON model_metrics(drift_detected);

-- Add updated_at trigger for glossary
CREATE OR REPLACE FUNCTION update_glossary_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER glossary_timestamp
BEFORE UPDATE ON medical_glossary
FOR EACH ROW
EXECUTE FUNCTION update_glossary_timestamp();

-- Add updated_at trigger for patients
CREATE OR REPLACE FUNCTION update_patients_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER patients_timestamp
BEFORE UPDATE ON patients
FOR EACH ROW
EXECUTE FUNCTION update_patients_timestamp();

-- Grant permissions
GRANT SELECT ON medical_glossary TO authenticated;
GRANT SELECT, INSERT ON patient_assessments TO authenticated;
GRANT SELECT, INSERT, UPDATE ON patients TO authenticated;
GRANT SELECT, INSERT ON model_metrics TO authenticated;
GRANT EXECUTE ON FUNCTION search_glossary_embedding TO authenticated;
