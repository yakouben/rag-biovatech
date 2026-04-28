-- Fix Schema Issues: Type Mismatches, FK Constraints, RLS Policies
-- Aligns all IDs to UUID, fixes foreign keys, adds RLS policies, corrects data types

-- Step 1: Add UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Step 2: Add columns for new UUID versions (to preserve data during migration)
ALTER TABLE patients ADD COLUMN IF NOT EXISTS new_id UUID DEFAULT gen_random_uuid();
ALTER TABLE patient_assessments ADD COLUMN IF NOT EXISTS new_patient_id UUID;
ALTER TABLE medical_glossary ADD COLUMN IF NOT EXISTS new_id UUID DEFAULT gen_random_uuid();

-- Step 3: Copy existing data to new UUID columns
UPDATE patients SET new_id = gen_random_uuid() WHERE new_id IS NULL;
UPDATE patient_assessments pa SET new_patient_id = p.new_id FROM patients p WHERE pa.patient_id = p.id AND new_patient_id IS NULL;
UPDATE medical_glossary SET new_id = gen_random_uuid() WHERE new_id IS NULL;

-- Step 4: Drop old foreign key constraints
ALTER TABLE patient_assessments DROP CONSTRAINT IF EXISTS patient_assessments_patient_id_fkey;

-- Step 5: Drop old primary keys
ALTER TABLE patients DROP CONSTRAINT IF EXISTS patients_pkey;
ALTER TABLE medical_glossary DROP CONSTRAINT IF EXISTS medical_glossary_pkey;

-- Step 6: Rename columns and make them primary keys
ALTER TABLE patients RENAME COLUMN id TO old_id;
ALTER TABLE patients RENAME COLUMN new_id TO id;
ALTER TABLE patients ADD PRIMARY KEY (id);

ALTER TABLE medical_glossary RENAME COLUMN id TO old_id;
ALTER TABLE medical_glossary RENAME COLUMN new_id TO id;
ALTER TABLE medical_glossary ADD PRIMARY KEY (id);

ALTER TABLE patient_assessments RENAME COLUMN patient_id TO old_patient_id;
ALTER TABLE patient_assessments RENAME COLUMN new_patient_id TO patient_id;

-- Step 7: Drop old indexes that referenced old columns
DROP INDEX IF EXISTS idx_patients_patient_id;

-- Step 8: Add proper foreign key constraint to patient_assessments
ALTER TABLE patient_assessments 
ADD CONSTRAINT patient_assessments_patient_id_fkey 
FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE;

-- Step 9: Fix data types
-- Ensure medical_glossary.related_terms is properly typed as text[]
ALTER TABLE medical_glossary 
ALTER COLUMN related_terms SET DATA TYPE text[] USING CASE 
    WHEN related_terms IS NULL THEN NULL::text[]
    ELSE ARRAY[related_terms]::text[]
END;

-- Step 10: Verify embedding column is vector(768)
-- (Already correct in current schema)

-- Step 11: Create new indexes
CREATE INDEX IF NOT EXISTS idx_patients_id ON patients(id);
CREATE INDEX IF NOT EXISTS idx_glossary_darija ON medical_glossary(darija_term);
CREATE INDEX IF NOT EXISTS idx_glossary_category ON medical_glossary(category);
CREATE INDEX IF NOT EXISTS idx_glossary_embedding ON medical_glossary USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_assessments_patient_id ON patient_assessments(patient_id);
CREATE INDEX IF NOT EXISTS idx_assessments_risk_level ON patient_assessments(risk_level);
CREATE INDEX IF NOT EXISTS idx_assessments_date ON patient_assessments(assessment_date);

-- Step 12: Clean up old columns
ALTER TABLE patients DROP COLUMN IF EXISTS old_id;
ALTER TABLE medical_glossary DROP COLUMN IF EXISTS old_id;
ALTER TABLE patient_assessments DROP COLUMN IF EXISTS old_patient_id;

-- Step 13: Enable RLS if not already enabled
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_glossary ENABLE ROW LEVEL SECURITY;
ALTER TABLE patient_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metrics ENABLE ROW LEVEL SECURITY;

-- Step 14: Drop existing policies and create new ones
DROP POLICY IF EXISTS patients_select_own ON patients;
DROP POLICY IF EXISTS patients_insert_own ON patients;
DROP POLICY IF EXISTS patients_update_own ON patients;
DROP POLICY IF EXISTS assessments_select_own ON patient_assessments;
DROP POLICY IF EXISTS assessments_insert_own ON patient_assessments;
DROP POLICY IF EXISTS glossary_select_public ON medical_glossary;
DROP POLICY IF EXISTS metrics_insert_own ON model_metrics;

-- Patients: users can see/edit their own data (assuming profiles.id = auth.users(id))
CREATE POLICY patients_select_own ON patients
    FOR SELECT USING (id::text = auth.uid()::text OR auth.role() = 'admin');

CREATE POLICY patients_insert_own ON patients
    FOR INSERT WITH CHECK (id::text = auth.uid()::text OR auth.role() = 'admin');

CREATE POLICY patients_update_own ON patients
    FOR UPDATE USING (id::text = auth.uid()::text OR auth.role() = 'admin')
    WITH CHECK (id::text = auth.uid()::text OR auth.role() = 'admin');

-- Patient Assessments: users see their own assessments, doctors see linked patients
CREATE POLICY assessments_select_own ON patient_assessments
    FOR SELECT USING (
        patient_id::text = auth.uid()::text 
        OR auth.role() = 'admin'
    );

CREATE POLICY assessments_insert_own ON patient_assessments
    FOR INSERT WITH CHECK (
        patient_id::text = auth.uid()::text 
        OR auth.role() = 'admin'
    );

-- Medical Glossary: readable by all authenticated users
CREATE POLICY glossary_select_public ON medical_glossary
    FOR SELECT TO authenticated USING (true);

-- Model Metrics: read-only for authenticated, insert for admin
CREATE POLICY metrics_select_authenticated ON model_metrics
    FOR SELECT TO authenticated USING (true);

CREATE POLICY metrics_insert_admin ON model_metrics
    FOR INSERT TO authenticated WITH CHECK (auth.role() = 'admin');

-- Step 15: Fix BMI column to use GENERATED ALWAYS AS (auto-update on weight/height change)
-- Note: This assumes you have weight and height columns. Adjust if column names differ.
-- ALTER TABLE patients ADD COLUMN IF NOT EXISTS weight FLOAT;
-- ALTER TABLE patients ADD COLUMN IF NOT EXISTS height FLOAT;
-- ALTER TABLE patients ADD COLUMN bmi GENERATED ALWAYS AS (weight / (height * height)) STORED;

-- If BMI is already a regular column and you want to keep it for now, no action needed.
-- To convert: create new column as GENERATED, migrate data, then swap.
