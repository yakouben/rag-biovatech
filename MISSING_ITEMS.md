# WHAT'S MISSING - Gap Analysis

## ✅ DONE (RAG Foundation)

### Database
- ✅ Schema created (database_setup_clean.sql)
- ✅ pgvector ready for Supabase
- ✅ RLS policies added

### RAG Engine
- ✅ Python RAG engine (rag_engine.py)
- ✅ 102 medical terms embedded (glossary_with_embeddings.json)
- ✅ Semantic search working
- ✅ Integration tests ready

### API Stubs (Basic)
- ✅ app/api/rag/query/route.ts (85 lines)
- ✅ app/api/glossary/search/route.ts (50 lines)
- ✅ app/api/assessments/calculate/route.ts (184 lines)

### React Hooks
- ✅ app/hooks/useRAG.ts (196 lines)

---

## ❌ MISSING - Must Build Now

### YAKOUB's Backend (FastAPI - AI Brain)

#### Phase 1-2: Setup
- ❌ `.env` file (GEMINI_API_KEY, SUPABASE credentials)
- ❌ FastAPI folder structure (app/services, routes, database, models)
- ❌ Supabase SQL setup (pgvector, glossary_vectors table, match function)

#### Phase 3-4: Glossary Loading
- ❌ `data/darija_medical_glossary.csv` (150+ rows)
- ❌ `database/glossary_loader.py` (read CSV → embed with Gemini → insert vectors)
- ❌ Run embedding pipeline

#### Phase 5: Decision Tree Model
- ❌ `scripts/train_decision_tree.py` (build risk model)
- ❌ Train with Algerian data distributions
- ❌ Save `models/risk_tree.pkl`

#### Phase 6: Services (5 files)
- ❌ `app/services/gemini_service.py` (embeddings + Nour responses)
- ❌ `app/services/rag_service.py` (RAG pipeline)
- ❌ `app/services/risk_service.py` (risk scoring)
- ❌ `app/services/drift_service.py` (detect BP/sugar anomalies)
- ❌ `app/services/pdf_service.py` (generate reports)

#### Phase 7: API Routes (6 endpoints)
- ❌ POST /ai/chat (RAG + risk)
- ❌ POST /ai/checkin (vitals + drift)
- ❌ POST /ai/drift/:patient_id
- ❌ POST /ai/pdf/:patient_id
- ❌ GET /ai/glossary
- ❌ POST /ai/glossary/match

#### Phase 8-9: App & Deployment
- ❌ `app/main.py` (FastAPI app)
- ❌ `Procfile` for Railway
- ❌ Deploy to Railway
- ❌ Get live URL

---

### CHAKER's Frontend (Next.js - Dashboard)

#### Phase 1: Setup
- ❌ `.env.local` (OPENAI_API_KEY, Supabase credentials)
- ❌ npm install dependencies

#### Phase 2-3: Auth & Doctor Dashboard
- ❌ `app/login/page.tsx` (email/password form)
- ❌ Role-based redirect (doctor vs family)
- ❌ Doctor dashboard (patient list with risk badges)
- ❌ Middleware for route protection

#### Phase 4-5: Patient Detail
- ❌ `app/doctor/patient/[id]/page.tsx`
  - Patient info section
  - Risk timeline (7-day history)
  - Medication adherence chart
  - Recent conversations

#### Phase 6: AI Summary
- ❌ OpenAI integration button
- ❌ `app/api/summary/route.ts` (server-side only)
- ❌ Display French clinical summary
- ❌ Loading state

#### Phase 7-8: PDF + Family Dashboard
- ❌ PDF download button
- ❌ `app/family/dashboard/page.tsx` (single patient view)
- ❌ `app/family/alerts/page.tsx` (alert management)

#### Phase 9: Realtime Updates
- ❌ Supabase Realtime subscription (risk_scores table)
- ❌ Live badge color updates
- ❌ Live alert notifications

---

## Critical Integration Points (NOT DONE)

1. **Yakoub → Database**
   - Glossary vectors must be in Supabase
   - Risk scores must be saved to DB

2. **Yakoub → Chaker**
   - POST /ai/chat endpoint called by doctor action
   - Risk score returned and saved
   - Realtime badge update triggered

3. **Chaker → OpenAI**
   - API key never exposed to client
   - Summary generation server-side only

4. **Full Loop**
   - Doctor logs in → sees patients
   - Clicks action → calls /ai/chat
   - Yakoub processes + saves risk
   - Chaker's badge updates live (realtime)
   - Doctor sees high-risk alert
   - Downloads PDF from backend

---

## Summary

| Area | YAKOUB | CHAKER |
|------|--------|--------|
| RAG Foundation | ✅ Done | ✅ Done |
| Backend API | ❌ 0% | - |
| Frontend Pages | - | ❌ 0% |
| Database Integration | ❌ 0% | - |
| Realtime Updates | - | ❌ 0% |
| **Total Progress** | **~5%** | **~5%** |

---

## Next Steps (Priority Order)

### Week 1: Yakoub
1. Setup FastAPI + env
2. Create glossary CSV (150+ terms)
3. Load glossary + embeddings
4. Train decision tree
5. Build 5 services
6. Build 6 API routes
7. Deploy to Railway

### Week 2: Chaker
1. Setup Next.js env + dependencies
2. Auth system + role redirect
3. Doctor dashboard + patient list
4. Patient detail page
5. OpenAI summary integration
6. Realtime updates + alerts
7. PDF download
8. Family dashboard

### Week 3: Integration
1. Test /ai/chat flow
2. Test realtime badge updates
3. Test full loop (login → action → update)
4. Production deployment

---

## Files Still Needed

```
FastAPI Backend:
  app/
    ├─ main.py
    ├─ services/
    │  ├─ gemini_service.py
    │  ├─ rag_service.py
    │  ├─ risk_service.py
    │  ├─ drift_service.py
    │  └─ pdf_service.py
    ├─ routes/
    │  ├─ ai.py
    │  └─ health.py
    └─ database/
       ├─ supabase_client.py
       └─ glossary_loader.py

Data:
  data/
    └─ darija_medical_glossary.csv

Models:
  models/
    └─ risk_tree.pkl (generated)

Scripts:
  scripts/
    └─ train_decision_tree.py

Deployment:
  Procfile

Next.js Frontend:
  app/
    ├─ login/
    │  └─ page.tsx
    ├─ doctor/
    │  ├─ dashboard/
    │  │  └─ page.tsx
    │  └─ patient/
    │     └─ [id]/
    │        └─ page.tsx
    ├─ family/
    │  ├─ dashboard/
    │  │  └─ page.tsx
    │  └─ alerts/
    │     └─ page.tsx
    └─ api/
       └─ summary/
          └─ route.ts

Lib utilities:
  lib/
    ├─ openai.ts
    ├─ supabase.ts
    └─ auth.ts
```

---

## Status: Ready to Build

- ✅ Checklists created
- ✅ Architecture documented
- ✅ Database ready
- ✅ RAG foundation ready
- ❌ Actual implementation needed

**What to do:** Follow YAKOUB_TASKS.md and CHAKER_TASKS.md phase by phase.
