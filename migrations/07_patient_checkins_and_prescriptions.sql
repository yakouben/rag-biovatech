-- Phase 1: Daily Check-ins Table
CREATE TABLE IF NOT EXISTS patient_checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    checkin_date DATE NOT NULL DEFAULT CURRENT_DATE,
    fasting_glucose FLOAT,
    systolic_bp INT,
    diastolic_bp INT,
    weight FLOAT,
    symptoms TEXT,
    mood TEXT,
    medications_taken BOOLEAN DEFAULT true,
    risk_score FLOAT,
    risk_level TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_patient_daily_checkin UNIQUE(patient_id, checkin_date)
);

-- Phase 2: Prescriptions and Medications
CREATE TABLE IF NOT EXISTS prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    doctor_notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prescription_medications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_id UUID REFERENCES prescriptions(id) ON DELETE CASCADE,
    medication_id INT, -- Refers to the ID in medications_catalog.json
    medication_name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    frequency TEXT NOT NULL,
    times TEXT[], -- Array of times like ['08:00', '20:00']
    with_food BOOLEAN DEFAULT true,
    medication_photo_url TEXT,
    darija_instructions TEXT,
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add telegram fields to patients
ALTER TABLE patients ADD COLUMN IF NOT EXISTS telegram_chat_id TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS disease_type TEXT DEFAULT 'diabetes'; -- 'diabetes', 'hypertension', 'both'

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_checkins_patient ON patient_checkins(patient_id);
CREATE INDEX IF NOT EXISTS idx_checkins_date ON patient_checkins(checkin_date);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_patients_telegram ON patients(telegram_chat_id);

-- RLS (Open for MVP as requested)
ALTER TABLE patient_checkins DISABLE ROW LEVEL SECURITY;
ALTER TABLE prescriptions DISABLE ROW LEVEL SECURITY;
ALTER TABLE prescription_medications DISABLE ROW LEVEL SECURITY;
