# ChronicCare — Project Status Summary

## Overview
**Platform**: SaaS for chronic disease management in Algeria  
**Frontend**: Chaker (Next.js dashboard)  
**Backend**: Yakoub (FastAPI AI brain)  
**Database**: Supabase (PostgreSQL + pgvector)  
**Status**: In Development

---

## What's Already Done

### Database ✅
- [x] Supabase setup SQL (pgvector, glossary_vectors table, match function)
- [x] 102+ medical terms embedded (glossary_with_embeddings.json)
- [x] Vector search working (cosine similarity tested)

### RAG Pipeline ✅
- [x] Embedding service (Gemini integration)
- [x] Semantic search (pgvector match function)
- [x] Full glossary with 150+ Darija terms ready

### Patient Assessment ✅
- [x] Risk scoring model structure
- [x] Decision tree framework
- [x] Assessment calculation endpoint

### Documentation ✅
- [x] API documentation (complete)
- [x] Deployment guide (complete)
- [x] Architecture documentation (complete)

---

## What YAKOUB (FastAPI) Needs to Do

**Total Phases**: 10  
**Est. Time**: 5-6 hours  
**Priority**: HIGH (blocks Chaker)

| Phase | Task | Status |
|-------|------|--------|
| 1 | Environment setup | ⬜ TODO |
| 2 | Supabase SQL setup | ⬜ TODO |
| 3 | Glossary CSV (150+ rows) | ⬜ TODO |
| 4 | Embed glossary | ⬜ TODO |
| 5 | Train decision tree | ⬜ TODO |
| 6 | Build 5 services | ⬜ TODO |
| 7 | Build 6 routes (/ai/*) | ⬜ TODO |
| 8 | Main app + startup checks | ⬜ TODO |
| 9 | Railway deployment | ⬜ TODO |
| 10 | Test + send URL to Seghir | ⬜ TODO |

**Checklist**: See `YAKOUB_TASKS.md`

---

## What CHAKER (Next.js) Needs to Do

**Total Phases**: 10  
**Est. Time**: 4-5 hours  
**Blocked by**: Yakoub's Phase 10 (needs API URL)

| Phase | Task | Status |
|-------|------|--------|
| 1 | Environment setup | ⬜ TODO |
| 2 | Auth (login page) | ⬜ TODO |
| 3 | Doctor dashboard | ⬜ TODO |
| 4 | Realtime risk badge | ⬜ TODO |
| 5 | Patient detail page | ⬜ TODO |
| 6 | OpenAI clinical summary | ⬜ TODO |
| 7 | PDF download | ⬜ TODO |
| 8 | Family dashboard | ⬜ TODO |
| 9 | Family alerts page | ⬜ TODO |
| 10 | Test + integration loop | ⬜ TODO |

**Checklist**: See `CHAKER_TASKS.md`

---

## Integration Points (MUST WORK)

### Yakoub → Supabase
- Embed glossary → `glossary_vectors` table
- Save risk scores → `risk_scores` table
- Save conversations → `conversations` table

### Yakoub → Chaker (via API)
- `/doctor/:id/patients` → Patient list with risk badges
- `/patient/:id/full` → Full patient data for detail page
- `/pdf/:patient_id` → Generate & return signed PDF URL
- `/alerts/:patient_id` → Alert list

### Chaker → Supabase (Realtime)
- Subscribe to `risk_scores` → update dashboard badges live
- Subscribe to `alerts` → notify family

### Chaker → OpenAI
- Server-side only (API route)
- Never expose API key to client

---

## Dependencies

### Yakoub's Stack
- FastAPI + uvicorn
- Google Generative AI (Gemini embeddings)
- Supabase Python client
- scikit-learn (decision tree)
- ReportLab (PDF generation)

### Chaker's Stack
- Next.js 14+
- Supabase JS client + SSR
- OpenAI (gpt-4o-mini)
- Recharts (visualizations)
- TailwindCSS

### Shared
- Supabase PostgreSQL + pgvector

---

## Timeline

**Phase 1**: Yakoub builds backend (5-6 hours)  
**Phase 2**: Chaker builds frontend (4-5 hours) — can start after Yakoub Phase 8  
**Integration**: 1-2 hours testing full loop  
**Total**: ~12-13 hours

---

## Critical Success Criteria

**H24 Full Loop Test**:
1. ✅ Yakoub's `/ai/chat` endpoint works
2. ✅ Risk score saved to Supabase
3. ✅ Chaker's dashboard badge updates live
4. ✅ Doctor can view patient detail + summary
5. ✅ PDF downloads correctly
6. ✅ No API keys exposed in client code

If all 6 criteria pass: **READY FOR ALPHA**

---

## File Locations

### Yakoub (FastAPI)
```
app/
  ├─ main.py
  ├─ services/
  │  ├─ gemini_service.py
  │  ├─ rag_service.py
  │  ├─ risk_service.py
  │  ├─ drift_service.py
  │  └─ pdf_service.py
  ├─ routes/
  │  ├─ chat.py
  │  ├─ checkin.py
  │  ├─ drift.py
  │  ├─ pdf.py
  │  └─ glossary.py
  ├─ database/
  │  ├─ supabase_client.py
  │  └─ glossary_loader.py
  └─ models/
data/darija_medical_glossary.csv
scripts/train_decision_tree.py
models/risk_tree.pkl
```

### Chaker (Next.js)
```
app/
  ├─ (auth)/
  │  └─ login/page.tsx
  ├─ doctor/
  │  ├─ dashboard/page.tsx
  │  └─ patient/[id]/page.tsx
  ├─ family/
  │  ├─ dashboard/page.tsx
  │  └─ alerts/page.tsx
  ├─ api/
  │  └─ summary/route.ts
  └─ lib/
     └─ openai.ts
```

---

## Next Steps

1. **Yakoub**: Start Phase 1 (environment) → complete checklist
2. **Chaker**: Wait for Yakoub Phase 8 → then start Phase 1
3. **Both**: Coordinate Phase 10 (integration testing)
4. **Seghir**: Prepare test data + API contracts
