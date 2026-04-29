# 🛠 ChronicCare Master API Reference
**Base URL:** `https://web-production-fadce.up.railway.app`
**Security:** Authentication is currently disabled for MVP prototype accessibility.

## 1. Patient Interaction (The "Nour" Brain)

### `POST /api/v1/chat`
Main endpoint for the mobile app. Converts Darija input into clinical reasoning and risk scores.
- **Request Body:**
  - `patient_id` (string)
  - `patient_symptoms` (string - transcribed Darija/French)
  - `patient_data` (object - vitals)
- **Response:**
  - `hela_response` (string)
  - `thinking_steps` (array - Proof of RAG and internal work)
  - `risk_score` (HIGH/MODERATE/LOW)
  - `glossary_context` (array - matched medical terms)

### `GET /api/v1/patient/{id}/check-drift`
Proactive reasoning engine. Checks for adherence drops and returns a Darija nurture message.

### `GET /api/v1/patient/{id}/history`
Fetches structured historical data (vitals, risk, summaries) over a specified period (default 30 days) for trend visualization.

## 2. Doctor Intelligence

### `POST /api/v1/doctor/chat`
RAG (Retrieval Augmented Generation) over a specific patient's history.
- **Request Body:**
  - `patient_id` (string)
  - `question` (string - e.g., "Is she taking her Metformin?")

### `GET /api/v1/patients/risk-queue`
Returns latest assessments for all patients, prioritized by risk score.

### `POST /api/v1/reports/generate`
Generates a comprehensive clinical PDF for the doctor.
- **Query Params:** `patient_id`, `patient_name`, `adherence_days` (7, 14, 21, 30).

## 3. Data Extraction (Background)

### `POST /api/v1/entities/extract`
Utility to turn unstructured Darija text into JSON clinical entities (Symptoms, Meds, Vitals).

## 4. System Health

### `GET /api/v1/health`
Check if the Brain is alive and connected to Supabase/Gemini.
