# YAKOUB — FastAPI AI Brain Checklist

## PHASE 1: Environment Setup
- [ ] Create `.env` with:
  - `GEMINI_API_KEY=...`
  - `SUPABASE_URL=...`
  - `SUPABASE_SERVICE_KEY=...`
  - `INTERNAL_API_KEY=...`
- [ ] Add `.env` to `.gitignore`
- [ ] Run: `pip install -r requirements.txt`
- [ ] Create folder structure:
  ```
  app/
    ├─ services/
    ├─ routes/
    ├─ database/
    ├─ models/
    └─ main.py
  data/
  scripts/
  models/
  ```

---

## PHASE 2: Supabase Setup
- [ ] Open Supabase SQL editor
- [ ] Copy & run `supabase_setup.sql`:
  - Enable pgvector extension
  - Create `glossary_vectors` table
  - Create `match_glossary_terms` function
- [ ] Verify: Table appears in Supabase dashboard

---

## PHASE 3: Glossary CSV
- [ ] Create `data/darija_medical_glossary.csv`
- [ ] Add 150+ rows with columns:
  ```
  darija_term, french_term, clinical_term, context
  ```
- [ ] Coverage (minimum per category):
  - [ ] Diabetes: 20+ terms
  - [ ] Cardiac: 20+ terms
  - [ ] Hypertension: 15+ terms
  - [ ] Medication adherence: 15+ terms
  - [ ] General/emotional: 20+ terms
  - [ ] Digestive/respiratory/neuro: 30+ terms
- [ ] Verify: Row count >= 150

---

## PHASE 4: Embed Glossary
- [ ] Build `database/supabase_client.py` (singleton)
- [ ] Build `database/glossary_loader.py`:
  - Read CSV
  - Call Gemini embeddings API
  - Upsert 768-dim vectors to Supabase
- [ ] Run: `python database/glossary_loader.py`
- [ ] Verify: 150+ rows in `glossary_vectors` table

---

## PHASE 5: Train Decision Tree
- [ ] Build `scripts/train_decision_tree.py` with Algerian distributions:
  ```
  Age: normal(63±10), clipped 40-85
  Adherence: normal(0.58±0.18), clipped 0.1-1.0
  BP systolic: normal(145±20), clipped 100-200
  Blood sugar: normal(8.5±2.5), clipped 4.0-18.0
  Co-occurrence: both=40%, diabetes=25%, hypertension=20%, cardiac=15%
  ```
- [ ] Run: `python scripts/train_decision_tree.py`
- [ ] Verify: `models/risk_tree.pkl` exists
- [ ] Verify: Accuracy printed in terminal

---

## PHASE 6: Build Services

### 6.1: gemini_service.py
- [ ] `embed_text(text)` → 768-dim vector
- [ ] `generate_nour_response(patient_text, matched_terms, patient_profile)` → JSON
  - [ ] Use `response_mime_type="application/json"`
  - [ ] Include JSON parse fallback (try/catch)
  - [ ] Persona: Darija only, warm, never diagnose, max 1 follow-up

### 6.2: rag_service.py
- [ ] `search_glossary(text, top_k=10)` → embed query → pgvector search
- [ ] `process_chat(patient_id, text, patient_profile)` → full RAG pipeline

### 6.3: risk_service.py
- [ ] Load `models/risk_tree.pkl` ONCE at startup (not per request)
- [ ] Guard: if missing → return fallback, don't crash
- [ ] `score_risk(patient_profile, extracted_entities, latest_checkin)` → {risk_score, confidence, factors}

### 6.4: drift_service.py
- [ ] `analyze_drift(patient_id)` → fetch 30 check-ins → Z-score on BP & blood sugar
- [ ] Return: {drift_detected, bp_z_score, bs_z_score, direction, bp_trend[], bs_trend[]}
- [ ] Skip if < 5 check-ins

### 6.5: pdf_service.py
- [ ] Fetch patient profile + clinic info from Supabase
- [ ] Fetch last 30 conversations, risk scores, adherence log
- [ ] Build PDF with ReportLab (A4):
  - [ ] Clinic logo
  - [ ] Patient info
  - [ ] Risk trend (colored blocks)
  - [ ] Adherence %
  - [ ] Nour summary
  - [ ] Footer
- [ ] Save: `/tmp/patient_{id}_report.pdf`
- [ ] Return: file path

---

## PHASE 7: Build Routes

### 7.1: POST /ai/chat
- [ ] Verify `INTERNAL_API_KEY` header
- [ ] Call `rag_service.process_chat()`
- [ ] Call `risk_service.score_risk()`
- [ ] Return: {nour_response, extracted_entities, risk_score, confidence, factors}

### 7.2: POST /ai/checkin
- [ ] Verify `INTERNAL_API_KEY` header
- [ ] Score vitals with Decision Tree
- [ ] Run drift detection
- [ ] Return: {risk_score, drift_flag, streak}

### 7.3: POST /ai/drift/{patient_id}
- [ ] Verify `INTERNAL_API_KEY` header
- [ ] Call `drift_service.analyze_drift(patient_id)`
- [ ] Return: full drift result

### 7.4: POST /ai/pdf/{patient_id}
- [ ] Verify `INTERNAL_API_KEY` header
- [ ] Call `pdf_service.generate_pdf(patient_id)`
- [ ] Return: {file_path}

### 7.5: GET /ai/glossary
- [ ] Return full glossary from Supabase

### 7.6: POST /ai/glossary/match
- [ ] Embed input → pgvector search → return top 5 matches

---

## PHASE 8: Main App
- [ ] Build `app/main.py`:
  - [ ] Register all routers under `/ai` prefix
  - [ ] Startup validation:
    - [ ] `models/risk_tree.pkl` exists
    - [ ] Supabase connection live
    - [ ] Glossary has 150+ rows
    - [ ] Gemini API key set
  - [ ] `GET /health` → {status, timestamp, glossary_count, model_loaded}
  - [ ] Add CORS middleware
  - [ ] Add request logging middleware

---

## PHASE 9: Deployment (Railway)
- [ ] Create `Procfile` at repo root:
  ```
  web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- [ ] Verify `requirements.txt` at repo root
- [ ] Add all env variables in Railway → Variables tab:
  - [ ] GEMINI_API_KEY
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_SERVICE_KEY
  - [ ] INTERNAL_API_KEY
- [ ] Deploy to Railway
- [ ] Verify: `GET /health` returns 200 on live URL

---

## PHASE 10: Test & Handoff
- [ ] Test `GET /health` → 200 ✅
- [ ] Test `POST /ai/glossary/match` with `{"text": "rasi yederni"}` → returns clinical terms ✅
- [ ] Test `POST /ai/chat` with full patient profile → valid JSON (5 fields) ✅
- [ ] Verify risk_score is exactly: "LOW" | "MODERATE" | "HIGH" ✅
- [ ] Verify nour_response in Darija ✅
- [ ] Send Seghir: Railway URL + INTERNAL_API_KEY ✅
- [ ] Confirm field names match contract ✅

---

## Critical: Full Loop Test
When complete, Seghir will call `/ai/chat` → your system saves risk_score to DB → Chaker's dashboard badge turns RED live. If that works: you're done.
