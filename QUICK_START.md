# RAG Medical Assistant - 5 Minute Quick Start

**TL;DR:** Everything is done. Just use it.

---

## For Frontend Developers (Copy-Paste Ready)

### Step 1: Import Hooks
```typescript
import { useRAG, useGlossarySearch, useRiskAssessment } from '@/app/hooks/useRAG';
```

### Step 2: Use in Component
```typescript
'use client';

export function MedicalSearch() {
  const { query, result, loading } = useRAG();

  return (
    <div>
      <button onClick={() => query("What is diabetes?")}>
        Ask AI
      </button>
      {result && <p>{result.ai_response}</p>}
    </div>
  );
}
```

### Step 3: Done
That's it. Works immediately. No setup needed.

---

## For Backend (What to Deploy)

### 1. Create .env.local
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxxxx
```

### 2. Create Database
```bash
# Copy contents of database_setup_clean.sql
# Paste in Supabase SQL editor
# Run
```

### 3. Load Glossary
```bash
# Option A: SQL
INSERT INTO medical_glossary ...

# Option B: Python
python scripts/load_glossary.py
```

### 4. Deploy
```bash
git push
# Vercel auto-deploys
# Add .env vars to Vercel dashboard
# Done ✅
```

---

## API Endpoints (3 Total)

### 1. RAG Query
```bash
curl -X POST http://localhost:3000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is diabetes?"}'
```

### 2. Search Glossary
```bash
curl -X POST http://localhost:3000/api/glossary/search \
  -H "Content-Type: application/json" \
  -d '{"query":"diabetes"}'
```

### 3. Risk Assessment
```bash
curl -X POST http://localhost:3000/api/assessments/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id":"uuid",
    "age":55,
    "systolic_bp":140,
    "diastolic_bp":90,
    "fasting_glucose":120,
    "bmi":28.5,
    "smoking":true,
    "family_history":true,
    "comorbidities":1
  }'
```

---

## React Hook Examples

### Search Medical Terms
```typescript
const { search, results, loading } = useGlossarySearch();

<input onChange={(e) => search(e.target.value)} />
{results.map(term => (
  <div key={term.id}>
    <strong>{term.darija}</strong> - {term.english}
  </div>
))}
```

### Calculate Risk
```typescript
const { calculate, result } = useRiskAssessment();

<button onClick={() => calculate(formData)}>
  Calculate Risk
</button>

{result && (
  <div>
    <h3>{result.risk_level}</h3>
    <p>{(result.risk_score * 100).toFixed(0)}%</p>
    <ul>
      {result.recommendations.map((rec, i) => (
        <li key={i}>{rec}</li>
      ))}
    </ul>
  </div>
)}
```

### Ask Medical Question
```typescript
const { query, result, loading, error } = useRAG();

<input 
  onChange={(e) => setQuestion(e.target.value)}
  placeholder="Ask a medical question..."
/>

<button onClick={() => query(question)} disabled={loading}>
  {loading ? 'Thinking...' : 'Ask'}
</button>

{error && <p className="error">{error}</p>}
{result && <p>{result.ai_response}</p>}
```

---

## File Locations

| Purpose | File |
|---------|------|
| React Hooks | `app/hooks/useRAG.ts` |
| Database Schema | `database_setup_clean.sql` |
| API Endpoints | `app/api/rag/query/route.ts` |
| | `app/api/glossary/search/route.ts` |
| | `app/api/assessments/calculate/route.ts` |
| Python Engine | `scripts/rag_engine.py` |
| Testing | `scripts/test_integration.py` |
| Data | `maladies_export.json` |

---

## Environment Variables

```env
# Required
NEXT_PUBLIC_SUPABASE_URL=your_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key

# Optional (for better AI)
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

---

## Test Everything Works

```bash
# Dev server
pnpm dev

# Test API
curl http://localhost:3000/api/glossary/search -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"diabetes"}'

# Run tests
python scripts/test_integration.py
```

---

## Common Tasks

### Add New Medical Term
```sql
INSERT INTO medical_glossary (darija_term, french_term, english_term, category, description)
VALUES ('جديد', 'nouveau', 'new', 'General', 'Description');
```

### Query Patient Risk
```typescript
const result = await calculate({
  patient_id: 'uuid',
  age: 55,
  systolic_bp: 140,
  diastolic_bp: 90,
  fasting_glucose: 120,
  bmi: 28.5,
  smoking: true,
  family_history: true,
  comorbidities: 1
});

console.log(result.risk_level); // 'HIGH'
```

### Search Medical Terms Programmatically
```typescript
const { search, results } = useGlossarySearch();
await search("diabetes", 10);
console.log(results); // Array of GlossaryTerm objects
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "SUPABASE_URL not found" | Add to `.env.local` |
| "No results from glossary" | Check data loaded: `SELECT COUNT(*) FROM medical_glossary;` |
| "API returns 500" | Check Supabase connection |
| "Hooks return errors" | Ensure dev server running: `pnpm dev` |

---

## Full Documentation

- **API Details:** See `API_DOCUMENTATION.md`
- **Deployment:** See `DEPLOYMENT_GUIDE.md`
- **Architecture:** See `RAG_IMPLEMENTATION.md`
- **Status:** See `FINAL_CHECKLIST.md`

---

## That's It!

✅ Database ready
✅ APIs ready
✅ Hooks ready
✅ Documentation ready

Start building! 🚀
