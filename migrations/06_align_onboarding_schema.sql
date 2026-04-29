-- Align Patient Schema with Dashboard Onboarding Mapping
ALTER TABLE patients ADD COLUMN IF NOT EXISTS first_name TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS last_name TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS birth_date DATE;

-- Create an index for faster searching by name
CREATE INDEX IF NOT EXISTS idx_patients_last_name ON patients(last_name);
CREATE INDEX IF NOT EXISTS idx_patients_first_name ON patients(first_name);

-- Comment for documentation
COMMENT ON COLUMN patients.first_name IS 'Patient given name';
COMMENT ON COLUMN patients.last_name IS 'Patient family name';
COMMENT ON COLUMN patients.birth_date IS 'Calculated or provided date of birth';
