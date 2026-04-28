CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS patients (
    id BIGSERIAL PRIMARY KEY,
    patient_id TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    gender TEXT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medical_glossary (
    id BIGSERIAL PRIMARY KEY,
    darija_term TEXT NOT NULL UNIQUE,
    french_term TEXT,
    english_term TEXT,
    category TEXT NOT NULL,
    severity INTEGER DEFAULT 1,
    description TEXT,
    related_terms TEXT[],
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patient_assessments (
    id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patients(id),
    age INTEGER NOT NULL,
    systolic_bp INTEGER NOT NULL,
    diastolic_bp INTEGER NOT NULL,
    fasting_glucose INTEGER NOT NULL,
    bmi FLOAT NOT NULL,
    smoking BOOLEAN NOT NULL,
    family_history BOOLEAN NOT NULL,
    comorbidities INTEGER NOT NULL,
    risk_score FLOAT,
    risk_level TEXT,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patients_patient_id ON patients(patient_id);
CREATE INDEX idx_glossary_darija ON medical_glossary(darija_term);
CREATE INDEX idx_glossary_category ON medical_glossary(category);
CREATE INDEX idx_glossary_embedding ON medical_glossary USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_assessments_patient_id ON patient_assessments(patient_id);
CREATE INDEX idx_assessments_risk_level ON patient_assessments(risk_level);
CREATE INDEX idx_assessments_date ON patient_assessments(assessment_date);
CREATE INDEX idx_model_metrics_name ON model_metrics(metric_name);

ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_glossary ENABLE ROW LEVEL SECURITY;
ALTER TABLE patient_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metrics ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION search_glossary_embedding(
    query_embedding vector(768),
    match_count INT DEFAULT 10,
    similarity_threshold FLOAT DEFAULT 0.3
)
RETURNS TABLE(
    id BIGINT,
    darija_term TEXT,
    french_term TEXT,
    english_term TEXT,
    category TEXT,
    severity INT,
    description TEXT,
    similarity FLOAT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        medical_glossary.id,
        medical_glossary.darija_term,
        medical_glossary.french_term,
        medical_glossary.english_term,
        medical_glossary.category,
        medical_glossary.severity,
        medical_glossary.description,
        (1 - (medical_glossary.embedding <=> query_embedding))::FLOAT as similarity
    FROM medical_glossary
    WHERE medical_glossary.embedding IS NOT NULL
    ORDER BY medical_glossary.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_patient_assessments(p_patient_id BIGINT, limit_results INT DEFAULT 50)
RETURNS TABLE(id BIGINT, patient_id BIGINT, age INT, systolic_bp INT, diastolic_bp INT, fasting_glucose INT, bmi FLOAT, smoking BOOLEAN, family_history BOOLEAN, comorbidities INT, risk_score FLOAT, risk_level TEXT, assessment_date TIMESTAMP)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        patient_assessments.id,
        patient_assessments.patient_id,
        patient_assessments.age,
        patient_assessments.systolic_bp,
        patient_assessments.diastolic_bp,
        patient_assessments.fasting_glucose,
        patient_assessments.bmi,
        patient_assessments.smoking,
        patient_assessments.family_history,
        patient_assessments.comorbidities,
        patient_assessments.risk_score,
        patient_assessments.risk_level,
        patient_assessments.assessment_date
    FROM patient_assessments
    WHERE patient_assessments.patient_id = p_patient_id
    ORDER BY patient_assessments.assessment_date DESC
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION insert_glossary_term(
    p_darija_term TEXT,
    p_french_term TEXT,
    p_english_term TEXT,
    p_category TEXT,
    p_severity INT,
    p_description TEXT,
    p_embedding vector(768)
)
RETURNS BIGINT AS $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO medical_glossary(darija_term, french_term, english_term, category, severity, description, embedding)
    VALUES (p_darija_term, p_french_term, p_english_term, p_category, p_severity, p_description, p_embedding)
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION insert_patient_assessment(
    p_patient_id BIGINT,
    p_age INT,
    p_systolic_bp INT,
    p_diastolic_bp INT,
    p_fasting_glucose INT,
    p_bmi FLOAT,
    p_smoking BOOLEAN,
    p_family_history BOOLEAN,
    p_comorbidities INT,
    p_risk_score FLOAT,
    p_risk_level TEXT
)
RETURNS BIGINT AS $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO patient_assessments(patient_id, age, systolic_bp, diastolic_bp, fasting_glucose, bmi, smoking, family_history, comorbidities, risk_score, risk_level)
    VALUES (p_patient_id, p_age, p_systolic_bp, p_diastolic_bp, p_fasting_glucose, p_bmi, p_smoking, p_family_history, p_comorbidities, p_risk_score, p_risk_level)
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;
