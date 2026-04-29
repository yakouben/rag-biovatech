-- Expand Patient Profiles with Family Contact and Migration Support
-- Adds fields for richer patient onboarding and history tracking

ALTER TABLE patients ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS family_contact_name TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS family_contact_phone TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS family_access_granted BOOLEAN DEFAULT FALSE;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS previous_clinic_id TEXT; -- For identifying data origin during migration
ALTER TABLE patients ADD COLUMN IF NOT EXISTS medical_history_summary TEXT; -- Brief summary of imported history

-- Create index for faster lookups by phone (useful for searching existing clients)
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_prev_clinic ON patients(previous_clinic_id);

-- Add comments for documentation
COMMENT ON COLUMN patients.family_contact_name IS 'Name of the family member to contact (e.g., son, daughter)';
COMMENT ON COLUMN patients.family_access_granted IS 'Whether the family member has access to receive alerts and reports';
COMMENT ON COLUMN patients.previous_clinic_id IS 'ID of the clinic where the patient was previously treated';
