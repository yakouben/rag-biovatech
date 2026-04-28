# 🛠 ChronicCare Master API Reference
**Base URL:** `https://web-production-fadce.up.railway.app`
**Security:** All requests require `X-Internal-Key` in the Header.

## 1. Patient Interaction (The "Nour" Brain)

### `POST /api/v1/chat`
Main endpoint for the mobile app. Converts Darija input into clinical reasoning and risk scores.
- **Request Body:**
  - `patient_id` (string)
  - `patient_symptoms` (string - transcribed Darija/French)
  - `patient_data` (object - vitals)

### `GET /patient/{id}/check-drift`
Proactive reasoning engine. Checks for adherence drops and returns a Darija nurture message.

### `GET /api/v1/patient/{id}/history`
Fetches structured historical data (vitals, risk, summaries) over a specified period (default 30 days) for trend visualization.

## 2. Doctor Intelligence

### `POST /doctor/chat`
RAG (Retrieval Augmented Generation) over a specific patient's history.
- **Request Body:**
  - `patient_id` (string)
  - `question` (string - e.g., "Is she taking her Metformin?")

### `POST /api/v1/reports/generate`
Generates a comprehensive clinical PDF for the doctor.
- **Query Params:** `patient_id`, `patient_name`, `adherence_days` (7, 14, 21, 30).

## 3. Data Extraction (Background)

### `POST /api/v1/entities/extract`
Utility to turn unstructured Darija text into JSON clinical entities (Symptoms, Meds, Vitals).

## 4. System Health

### `GET /api/v1/health`
Check if the Brain is alive and connected to Supabase/Gemini.
