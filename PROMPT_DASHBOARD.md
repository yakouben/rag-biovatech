# 🖥️ DASHBOARD TEAM — Complete Spec
> **Base URL:** `https://web-production-fadce.up.railway.app/api/v1`
> **Auth:** Every request needs header `X-Internal-Key: [from .env file]`
> **Tech:** Next.js or React + Recharts + Axios

---

## What You're Building (Read This First)

You are building a **doctor-facing web dashboard** for chronic disease management
(Diabetes & Hypertension) in Algeria. The doctor uses this to manage all their
patients from one screen. They can see who is at risk, who missed their meds,
and ask the AI questions about any patient's history.

The doctor is the one who **creates patients**. They fill a form with the
patient's info (name, age, vitals, family contact), and the backend stores it
in the `patients` table on Supabase. The backend also runs an AI analysis
on the imported data and returns a clinical summary and a welcome message.

Once a patient is registered, the patient uses a **mobile app** (that's the
other team) to chat with Hela AI daily. Every chat creates an assessment
record in the `patient_assessments` table on Supabase. Your dashboard reads
those assessments to show the doctor real-time risk scores, adherence trends,
and AI-generated clinical insights — without the doctor needing to call anyone.

The whole point is: **the doctor sees everything the patient does, automatically.**
No phone calls, no paper files. The AI tracks the patient 24/7 between visits.

---

## What The Mobile App Team Does (So You Understand)

The app dev builds a Flutter app for patients. Patients chat with Hela AI using
`POST /chat`, which saves assessments to Supabase. They view their own health
history and get medication nudges. They download PDF reports. They do NOT manage
other patients or see the risk queue — that's your job. Everything the patient
writes via chat becomes data you read on the dashboard.

---

## YOUR ENDPOINTS

### `GET /api/v1/health`
**When to call:** On dashboard load, show status in header.
**What it does:** Pings Supabase, Gemini AI, and the Risk Model.
**What comes back:** `status` ("healthy" or "degraded"), `version`, `timestamp`, and a `services` object with `database`, `gemini`, `model`, `environment`.
**What you show:** A small dot in the top-right corner. Green = healthy. Red = degraded. Tooltip shows the service details on hover.

---

### `POST /api/v1/patients/onboard`
**When to call:** Doctor fills the "Add Patient" form and clicks Submit.
**What it does:** Creates a new row in the `patients` table in Supabase. If `initial_vitals` are provided, it also runs a risk assessment and saves the first record to `patient_assessments`. Then it calls Gemini AI to generate a clinical summary and a Darija welcome message.
**Request body fields:**
- `profile` (object) — `name`, `age`, `gender`, `phone`, `address`, `date_of_birth`, `family_contact_name`, `family_contact_phone`, `family_access_granted` (boolean), `previous_clinic_id` (optional), `medical_history_summary` (optional)
- `initial_vitals` (object, optional) — `age`, `systolic_bp`, `diastolic_bp`, `fasting_glucose`, `bmi`, `smoking`, `family_history`, `comorbidities`
- `is_import` (boolean) — `true` if the patient is being imported from another clinic

**What comes back:**
- `patient_id` — the UUID Supabase generated. **Save this.** You need it for every other call.
- `status` — `"success"`
- `message` — confirmation string
- `initial_risk` — full risk assessment object with `category` (HIGH/MODERATE/LOW), `risk_score`, `recommendations[]`, `monitoring_frequency`. Will be `null` if no vitals were provided.
- `ai_analysis` — object with `clinical_summary`, `welcome_message_darija`, `suggested_focus`

**What you show:**
- A **multi-step form**: Step 1 = identity (name, age, gender, phone) → Step 2 = vitals (BP, glucose, BMI) → Step 3 = family contact → Step 4 = review & submit
- On success → show a result card with the `initial_risk.category` as a colored badge + `ai_analysis.clinical_summary` + `ai_analysis.suggested_focus` highlighted
- If `is_import` is true, show the `message` which includes the origin clinic

---

### `GET /api/v1/patient/{patient_id}/profile`
**When to call:** When doctor clicks a patient row in the list.
**What it does:** Reads from the `patients` table in Supabase.
**What comes back:** `id`, `name`, `age`, `gender`, `phone`, `address`, `date_of_birth`, `family_contact_name`, `family_contact_phone`, `family_access_granted`, `previous_clinic_id`, `medical_history_summary`.
**What you show:** A profile card. Show family contact with a phone icon. Show `family_access_granted` as a colored badge (green = yes, grey = no).

---

### `GET /api/v1/patients/risk-queue`
**When to call:** Dashboard home page on load. This is your **main screen**.
**What it does:** Queries `patient_assessments` table from Supabase, gets the latest assessment per patient, orders by `assessment_date` descending, returns up to 100 records.
**What comes back:** Array of objects, each with:
- `patient_id` — UUID
- `assessment_date` — ISO timestamp
- `risk_score` — float (0-10)
- `predicted_risk_level` — int: `0` = LOW, `1` = MODERATE, `2` = HIGH
- `symptoms` — string (latest clinical note)

**Important:** This does NOT return the patient's name. You must call `GET /patient/{id}/profile` separately to get the name. **Cache profiles** after first fetch so you don't re-call for every row.

**What you show:**
- A **sortable table** with columns: Patient Name | Risk Level | Last Note | Last Check-in | Actions
- Risk badge: `predicted_risk_level` 2 = 🔴 HIGH, 1 = 🟡 MODERATE, 0 = 🟢 LOW
- Sort by risk level descending by default (HIGH on top)
- "Actions" column: buttons for "View" (→ patient detail) and "Report" (→ PDF)
- If a patient hasn't checked in for **7+ days**, show a ⏰ "Inactive" warning icon

---

### `GET /api/v1/patient/{patient_id}/history?days=30`
**When to call:** Patient detail page loads.
**Query param:** `days` — integer (7, 14, 30, or 90).
**What it does:** Reads from `patient_assessments` in Supabase, extracts vitals from the `clinical_entities` JSONB column, returns a chronological array.
**What comes back:**
- `patient_id` — string
- `count` — how many entries
- `history` — array of `{ date, risk, systolic, diastolic, glucose, summary }`

**What you show:**
- **BP Chart** (Recharts LineChart): two lines — systolic (red) + diastolic (blue). Reference lines at 120/80 mmHg.
- **Glucose Chart:** single amber line. Reference at 100 mg/dL.
- **Date range selector:** 7d | 14d | 30d | 90d — re-fetches on click
- **Timeline list:** each `summary` as a card below the charts, with the `date` and `risk` badge

---

### `GET /api/v1/patient/{patient_id}/check-drift`
**When to call:** Alongside the history call on patient detail page.
**What it does:** Compares 3-day vs 30-day medication adherence using `adherence_service`, which reads `clinical_entities.missed_medications` from `patient_assessments` in Supabase. If there's a >30% drop, generates a Darija nurture message via Gemini.
**What comes back:**
- `long_term_adherence` — float 0-1 (30-day)
- `short_term_adherence` — float 0-1 (3-day)
- `adherence_drop` — float
- `trigger_notification` — boolean
- `nurture_message_darija` — string (only if triggered)

**What you show:**
- **Adherence bar** on the patient detail page: green if > 80%, yellow if 50-80%, red if < 50%
- Show the percentage: e.g. "Adherence: 85%"
- If `trigger_notification` is `true` → show a 🔴 **"Adherence Alert"** badge. Show `adherence_drop` as "-35%"
- Also mark this patient with a red dot in the risk-queue table

---

### `POST /api/v1/doctor/chat`
**When to call:** Doctor types a question in the "Ask AI" panel on a patient detail page.
**What it does:** Pulls the last 50 records from `patient_assessments` for this patient from Supabase, builds a history context, and asks Gemini AI to answer the doctor's question based only on that history.
**Request body fields:**
- `patient_id` (string) — the patient UUID
- `question` (string) — natural language clinical question
- `include_raw_history` (boolean) — set `true` if you want the raw assessment rows back

**What comes back:**
- `answer` — string, the AI's clinical answer
- `patient_id` — string
- `history_analyzed` — int (how many records the AI reviewed)
- `raw_history` — array of assessment objects (only if `include_raw_history` was `true`, otherwise `null`)

**What you show:**
- Chat-style input at the bottom of the patient detail page
- AI answer in a styled card with a 🤖 icon
- Subtitle: "Based on {history_analyzed} records"
- If raw history is requested, show a collapsible list of the assessment entries

---

### `POST /api/v1/reports/generate`
**When to call:** Doctor clicks "Generate Report" on a patient's page.
**Query params:** `patient_id` (string), `patient_name` (string), `adherence_days` (int, default 30).
**What it does:** Re-runs risk assessment + adherence + glossary + AI reasoning on the backend, then generates a PDF with ReportLab containing patient info, vital signs table, risk assessment, clinical notes, adherence score, and recommendations. Streams back as `application/pdf`.
**What you show:**
- Loading spinner ("Generating clinical report…")
- On completion: open PDF in a new browser tab or trigger a download
- Offer a Print button

---

## YOUR SCREENS

| # | Screen | API Calls | What It Shows |
|---|--------|-----------|---------------|
| 1 | Dashboard Home | `GET /patients/risk-queue` + `GET /health` | Risk-sorted patient table + system status |
| 2 | Add Patient | `POST /patients/onboard` | Multi-step form → AI analysis result |
| 3 | Patient Detail | `GET /profile` + `GET /history` + `GET /check-drift` | Profile + charts + adherence + alerts |
| 4 | Doctor Intelligence | `POST /doctor/chat` (inside patient detail) | Chat input + AI answer card |
| 5 | Report | `POST /reports/generate` | Loading → PDF download/preview |

**Sidebar nav:** Dashboard Home | Add Patient

---

## UX RULES

- **Speed.** Doctors have 2 minutes per patient. The risk queue must load in under 1 second. Use skeleton loaders.
- **Data density.** Unlike the mobile app (big fonts, simple), the dashboard should show **more data per screen** — tables, charts, stats.
- **Light mode default.** Background `#F9FAFB`, cards `#FFFFFF`, borders `#E5E7EB`, text `#111827`. Offer a dark mode toggle.
- **Risk colors everywhere.** HIGH = `#EF4444`, MODERATE = `#F59E0B`, LOW = `#10B981`. Use these on badges, chart dots, table rows.
- **Font:** Inter for everything. Professional and clean.
- **Charts:** Use Recharts. Systolic = red line. Diastolic = blue line. Glucose = amber line. Always show reference lines for normal values.
- **3 states.** Every data section: Loading (skeleton) → Success (content) → Error (retry + message).
- **Responsive.** Must work on 1920px desktop AND 1024px tablet (doctors use both).
