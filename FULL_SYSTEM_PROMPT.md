# 🚨 ChronicCare / Hela AI — FULL SYSTEM REBUILD PROMPT
> **For: Flutter App Dev + Dashboard Dev**
> **From: Yakoub (Backend Lead / Architect)**
> Copy-paste into Cursor / Windsurf. The previous UI/UX was wrong. This is the truth.

---

## THE BIG PICTURE — How The System Actually Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE CHRONICCARE FLOW                         │
│                                                                 │
│  DOCTOR (Web Dashboard)                                         │
│    │                                                            │
│    ├─ 1. Creates account (email + password)                     │
│    ├─ 2. Onboards patient (fills profile form)                  │
│    ├─ 3. System generates SECURE QR CODE                        │
│    │      └─ Patient receives OTP via EMAIL to unlock QR        │
│    │      └─ QR contains: patient_id + encrypted profile link   │
│    ├─ 4. Declares medications (name, dose, schedule, photo)     │
│    ├─ 5. Monitors Risk Queue (AI auto-sorts by danger)          │
│    ├─ 6. Asks AI about patient history (Doctor-Chat RAG)        │
│    └─ 7. Generates PDF clinical reports                         │
│                                                                 │
│  PATIENT (Mobile App — scans QR to activate)                    │
│    │                                                            │
│    ├─ 1. Scans QR code → OTP email verification                 │
│    ├─ 2. Lands on Home with health summary                      │
│    ├─ 3. Chats with HELA AI (Darija/French/Arabic)              │
│    ├─ 4. Gets medication reminders (Pharma API — photo+dose)    │
│    ├─ 5. Receives nurture nudges when adherence drops           │
│    ├─ 6. Views health timeline (BP, glucose, risk trends)       │
│    └─ 7. Downloads PDF summary of all history                   │
│                                                                 │
│  AI ENGINE (FastAPI Backend — runs automatically)               │
│    │                                                            │
│    ├─ Tracks every patient daily (cron / background)            │
│    ├─ Detects adherence drift → triggers notifications          │
│    ├─ Detects HIGH risk spikes → alerts doctor immediately      │
│    └─ Centralizes ALL data so any doctor can continue care      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## PROBLEM WE SOLVE

> A diabetic/hypertensive patient in Algeria sees their doctor once a month. Between visits, **nobody tracks them.** They forget medications, their BP spikes, nobody knows until it's too late. If they switch doctors, all history is lost.

**Our solution:** Centralized AI-powered tracking that works 24/7 between doctor visits.

---

## 🔌 BACKEND API (Base URL + Auth)

```
Base URL: https://web-production-fadce.up.railway.app/api/v1
Auth Header: X-Internal-Key: [from .env]
```

---

## 📱 MOBILE APP — SCREEN-BY-SCREEN SPEC

### FLOW: Patient Activation (QR + OTP)

**Step 1 — QR Scan Screen**
- Patient opens app → camera screen to scan QR code provided by doctor.
- QR contains: `{ patient_id, doctor_id, clinic_name }` (JSON encoded, encrypted).

**Step 2 — OTP Verification Screen**
- After scanning, app sends `POST /api/v1/auth/verify-qr` with the QR payload.
- Backend sends OTP to patient's registered email.
- UI: 6-digit OTP input field. Timer (60s resend). "Check your email" message.
- On success → patient is activated, token stored locally.

**Step 3 — Welcome Screen**
- Shows: "Welcome [Name]! Your doctor [Dr. X] has connected you to ChronicCare."
- CTA: "Start Your Health Journey" → navigates to Home.

---

### SCREEN 1: Home Dashboard

**API calls on load:**
- `GET /patient/{id}/check-drift` → nurture card
- `GET /patient/{id}/history?days=7` → quick chart
- `GET /patient/{id}/profile` → name, age, medications

**Layout:**
- **Greeting:** "Marhba, [Name] 👋" (Amiri font if Arabic name)
- **Nurture Card** (conditional): amber gradient, shows `nurture_message_darija` if `trigger_notification == true`. Buttons: "نتكلمو" → Chat | "Labess" → dismiss.
- **Risk Gauge:** Circular arc showing latest risk (GREEN/YELLOW/RED).
- **Medication Reminder Card:** Shows next medication due. Photo of pill + name + dose + time. Button: "✓ Taken" or "⏰ Remind me later".
- **Mini Glucose Chart:** Last 7 days. Tap → full History screen.

**Bottom Nav:** Home | Chat | History | Dictionary (4 tabs)

---

### SCREEN 2: Hela Chat

**API:** `POST /api/v1/chat`

**Request:**
```json
{
  "patient_id": "string",
  "patient_symptoms": "Darija/French/Arabic text",
  "patient_data": {
    "age": 65, "systolic_bp": 155, "diastolic_bp": 95,
    "fasting_glucose": 140, "bmi": 27.5,
    "smoking": false, "family_history": true, "comorbidities": 1
  },
  "include_glossary": true
}
```

**Response:**
```json
{
  "hela_response": "AI clinical answer (Darija/French)",
  "extracted_entities": { "vitals": {...}, "symptoms": [...], "medications": [...] },
  "risk_score": "HIGH | MODERATE | LOW",
  "confidence": 0.87,
  "factors": ["elevated BP", "high glucose"],
  "glossary_context": [{ "darija": "sokor", "french": "Diabète", "arabic": "السكري" }]
}
```

**UI Rules:**
- WhatsApp-style dark chat. Patient = right (helaBlue). Hela = left (cardBg) with avatar.
- **Microphone button** (speech_to_text). Pulsing red dot when recording.
- **"Hela is thinking…"** = 3 bouncing dots animation (2-4 sec).
- After response: Risk Badge (colored) + confidence %. Glossary chips (tappable → bottom sheet). Expandable "Detected Entities" panel.
- If `confidence < 0.70`: show "⚠️ Consultez un médecin".

---

### SCREEN 3: Medication Reminders (NEW — Pharma API Integration)

**Concept:** Doctor declares medications via dashboard. App reminds patient at scheduled times.

**Data structure (from backend):**
```json
{
  "medications": [
    {
      "id": "med_001",
      "name": "Metformin 500mg",
      "dose": "1 tablet",
      "schedule": ["08:00", "20:00"],
      "photo_url": "https://pharma-api.com/images/metformin.jpg",
      "instructions": "Take with food",
      "declared_by": "Dr. Benali"
    }
  ]
}
```

**UI:**
- Card per medication: pill photo + name + dose + next time due.
- "✓ I took it" button → records adherence. "Skip" → records miss.
- At scheduled times: **push notification** with pill photo + name + dose.
- Missed dose → counter-increments, feeds into drift detection.

---

### SCREEN 4: Health Timeline

**API:** `GET /api/v1/patient/{id}/history?days=30`

**Response:** Array of `{ date, risk, systolic, diastolic, glucose, summary }`

**UI:**
- Range selector: 7j | 14j | 30j | 90j
- **Chart 1 — BP:** Two lines (systolic red-dashed, diastolic blue-solid). Reference lines at 120/80.
- **Chart 2 — Glucose:** Single amber line. Reference at 100 mg/dL.
- **Risk Timeline:** Row of colored dots per day.
- **Summary Cards:** Last 7 entries with tap-to-expand.

---

### SCREEN 5: Medical Dictionary

**API:** `POST /api/v1/glossary/search`

**UI:** RTL search bar → debounce 400ms → cards with Darija (large, Amiri) + French + Arabic + description.

---

### SCREEN 6: My Profile & QR Code

- Shows patient profile info (name, age, doctor, clinic).
- **"Show My QR Code"** button → requires **OTP re-verification** (medical ethics).
- QR contains: encrypted link to full profile + chat history + all test results.
- **"Download PDF Summary"** button → calls `POST /api/v1/reports/generate` → saves PDF.
- This QR is what they show a **new doctor** to transfer ALL their centralized data.

---

## 🖥️ WEB DASHBOARD — SCREEN-BY-SCREEN SPEC

### SCREEN D1: Doctor Auth (Sign Up / Sign In)
- Email + password registration. Email verification.
- Profile: name, specialty, clinic name, license number.

### SCREEN D2: Patient Management (The Core)

**Onboard New Patient:**
- Form: name, age, gender, phone, email, address, date of birth.
- Family contact (name + phone + access toggle).
- Previous clinic ID (for imports).
- Initial vitals (BP, glucose, BMI, smoking, family history).
- **API:** `POST /api/v1/patients/onboard`

**After onboarding:**
- System generates **QR code** containing `{ patient_id, doctor_id }`.
- QR is NOT visible until doctor triggers **OTP email** to patient's registered email.
- Patient must enter OTP on their phone to activate QR scanning.

**Patient List:**
- Table: Name | Risk | Last Check-in | Adherence % | Actions
- Color-coded risk badges. Sortable columns.
- "🔴 Alert" icon if adherence dropped >30% in 48h.

---

### SCREEN D3: Risk Queue (Triage Dashboard)

**API:** `GET /api/v1/patients/risk-queue`

**UI:**
- Auto-sorted by risk (HIGH first). Shows: patient name, risk score, last symptoms, days since last check-in.
- **Red Alert** for patients with: risk=HIGH AND adherence drop >30%.
- Click patient → opens their full profile + history.

---

### SCREEN D4: Doctor-Chat RAG (AI over Patient History)

**API:** `POST /api/v1/doctor/chat`

**Request:** `{ patient_id, question, include_raw_history }`

**UI:**
- Select patient from dropdown → type question like "Has she mentioned chest pain this month?"
- AI answers using last 50 assessments as context.
- **Citations:** Each claim links to the specific historical note. Tapping scrolls to it.

---

### SCREEN D5: Medication Declaration (Pharma Integration)

**Doctor declares per patient:**
- Medication name (autocomplete from Pharma API)
- Dose, frequency, schedule times
- Upload or fetch pill photo from Pharma API
- Special instructions

**This data feeds into:**
- Patient's medication reminder screen (mobile app)
- Adherence tracking (did they tap "taken"?)
- Drift detection (missed doses → nurture notification)

---

### SCREEN D6: Clinical Reports

**API:** `POST /api/v1/reports/generate?patient_id=...&patient_name=...&adherence_days=30`

**UI:** One-click "Generate PDF" button per patient. PDF includes: vitals, risk assessment, AI clinical notes, adherence score, recommendations. Downloadable + printable.

---

## 🎨 DESIGN TOKENS

```
Risk Colors:    LOW=#2ECC71  MODERATE=#F1C40F  HIGH=#E74C3C
Brand:          helaBlue=#3498DB  darkBg=#0D1117  cardBg=#161B22
Surface:        surfaceBg=#21262D  textPrimary=#E6EDF3  textSecondary=#8B949E
Nurture:        amberStart=#F59E0B  amberEnd=#D97706
Fonts:          Inter (Latin)  Amiri (Arabic/Darija)
Min font:       16px. Min touch target: 48x48px (elderly users).
RTL:            All Darija/Arabic text must render RTL.
```

---

## ⚠️ CRITICAL RULES

1. **API key from .env only** (flutter_dotenv). Never hardcode.
2. **Single ApiService class** (dio). No scattered HTTP calls.
3. **Every screen = 3 states:** Loading (shimmer) | Success | Error (retry).
4. **Offline:** Show "Vérifiez votre connexion / تحقق من اتصالك" — never crash.
5. **QR security:** OTP email required before QR is accessible. Medical ethics compliance.
6. **Data centralization:** ALL patient data (chats, tests, medications) stored in Supabase. Any doctor with QR access can see full history.
7. **Animations:** Hela avatar pulses while thinking. Charts animate in (800ms). Screen transitions = FadeTransition (300ms).

---

## 🧪 ACCEPTANCE CRITERIA

| Feature | Test | Pass |
|---------|------|------|
| QR Scan | Scan valid QR | OTP email sent, 6-digit input shown |
| OTP | Enter correct code | Patient activated, navigates to Home |
| Home | Adherence dropped | Amber nurture card with Darija message |
| Chat | Send Darija text | Response + risk badge + glossary chips |
| Chat | confidence < 0.70 | Warning label shown |
| Meds | Scheduled time hits | Push notification with pill photo + dose |
| Meds | Tap "Taken" | Adherence recorded, counter updates |
| History | Select 90j range | Charts re-fetch and re-render |
| Profile QR | Tap "Show QR" | OTP re-verification required first |
| PDF | Tap "Download" | PDF saved to device, preview opens |
| Dashboard | Open Risk Queue | Patients sorted HIGH→LOW, alerts visible |
| Doctor Chat | Ask about patient | AI answers with citations to history |
| Onboard | Fill form, submit | QR generated, OTP flow triggered |
| Offline | Kill network | Graceful error message, no crash |

---

## FEATURES YOU SHOULD ALSO ADD (What Yakoub Forgot)

1. **Emergency Contact Alert:** If risk = HIGH for 3+ consecutive days → auto-send SMS to `family_contact_phone` (if `family_access_granted == true`).
2. **Appointment Scheduling:** Let doctor set next appointment date. Patient sees countdown on Home. Reminder notification 24h before.
3. **Symptom Photo Upload:** Patient can attach a photo (wound, swelling) to their chat message. Backend stores in Supabase storage.
4. **Fasting Timer:** For glucose tests — patient taps "Start Fasting" and the app counts 8 hours with a notification when ready.
5. **Multilingual Toggle:** Settings screen to switch entire UI between Darija, French, and Arabic. Persist choice in SharedPreferences.
6. **Dark/Light Mode:** Toggle in settings. Default = dark.
7. **Doctor Notes:** After viewing AI analysis, doctor can add their own clinical note that gets saved alongside the AI assessment.
8. **Export All Data:** Patient can export ALL their data (JSON or PDF bundle) via the Profile QR screen — data portability for switching clinics.
9. **Vitals Self-Entry:** Between doctor visits, patient can manually log BP + glucose readings from home devices. These feed into the charts and risk engine.
10. **Weekly AI Summary:** Every Sunday, the AI generates a natural-language weekly summary ("This week your glucose averaged 135, your BP was stable...") and pushes it as a notification.
