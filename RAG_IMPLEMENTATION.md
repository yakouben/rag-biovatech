# RAG Medical Assistant - Complete Implementation Guide

**Status:** ✅ Production-Ready

This is a complete, production-ready Retrieval-Augmented Generation (RAG) system for medical assistance in Moroccan Arabic (Darija), French, and English.

---

## What You Have

### Backend Components

#### 1. **Database Schema** (`database_setup_clean.sql`)
```sql
✅ patients - User patient records
✅ medical_glossary - Medical terms with embeddings (Darija/French/English)
✅ patient_assessments - Risk scores & health metrics
✅ model_metrics - Model performance tracking
✅ Row Level Security (RLS) - Data privacy policies
```

#### 2. **Next.js API Routes** (Serverless Functions)
```
✅ POST /api/rag/query - Semantic search + LLM generation
✅ POST /api/glossary/search - Full-text medical term search
✅ POST /api/assessments/calculate - Cardiovascular risk scoring
```

#### 3. **Python RAG Engine** (`scripts/rag_engine.py`)
```
✅ EmbeddingService - Text-to-vector embeddings
✅ SemanticSearch - Vector similarity search
✅ MedicalLLM - LLM integration (Claude/OpenAI)
✅ RAGEngine - Full orchestration
```

#### 4. **React Hooks** (`app/hooks/useRAG.ts`)
```
✅ useRAG() - Execute RAG queries
✅ useGlossarySearch() - Search medical terms
✅ useRiskAssessment() - Calculate risk scores
```

---

## Quick Start (5 minutes)

### 1. Set Environment Variables
```bash
# Create .env.local in project root
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Optional
```

### 2. Initialize Database
```bash
# Create tables in Supabase
psql < database_setup_clean.sql

# Load medical glossary
python scripts/load_glossary.py  # Creates table from maladies_export.json
```

### 3. Install & Run
```bash
pnpm install
pnpm dev
# App runs at http://localhost:3000
```

### 4. Test API
```bash
# Terminal 2
curl -X POST http://localhost:3000/api/glossary/search \
  -H "Content-Type: application/json" \
  -d '{"query":"diabetes"}'
```

---

## Frontend Developer Quick Start

### Use the React Hooks

```typescript
'use client';

import { useRAG, useGlossarySearch, useRiskAssessment } from '@/app/hooks/useRAG';

export function YourComponent() {
  // Hook 1: RAG Query (semantic search + LLM)
  const { query, result, loading, error } = useRAG();
  
  // Hook 2: Glossary Search
  const { search, results } = useGlossarySearch();
  
  // Hook 3: Risk Assessment
  const { calculate, result: assessment } = useRiskAssessment();

  return (
    <div>
      {/* Glossary Search UI */}
      <input onChange={(e) => search(e.target.value)} />
      {results.map(term => (
        <div key={term.id}>
          <strong>{term.darija}</strong> ({term.english})
          <p>{term.description}</p>
        </div>
      ))}

      {/* RAG Query UI */}
      <button onClick={() => query("What is diabetes in Darija?")}>
        Ask Medical Question
      </button>
      {result && (
        <div>
          <p>{result.ai_response}</p>
          <p>Confidence: {(result.confidence * 100).toFixed(0)}%</p>
        </div>
      )}

      {/* Risk Assessment UI */}
      <button onClick={() => calculate({ 
        patient_id: 'uuid',
        age: 55,
        systolic_bp: 140,
        diastolic_bp: 90,
        fasting_glucose: 120,
        bmi: 28.5,
        smoking: true,
        family_history: true,
        comorbidities: 1
      })}>
        Calculate Risk
      </button>
      {assessment && (
        <div>
          <h3>Risk Level: {assessment.risk_level}</h3>
          <p>Score: {(assessment.risk_score * 100).toFixed(0)}%</p>
          <ul>
            {assessment.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

## Architecture

### Request Flow

```
User Input
    ↓
React Component uses Hook (useRAG, etc.)
    ↓
Calls Next.js API Route (/api/rag/query, etc.)
    ↓
API Route processes request
    ├─ Query Supabase (medical_glossary)
    ├─ Semantic search (vector similarity)
    ├─ Call LLM (Claude/OpenAI via Vercel AI Gateway)
    └─ Return structured response
    ↓
React Hook updates state
    ↓
Component renders result
```

### Data Flow

```
Medical Glossary JSON
    ↓
Loaded into Supabase (medical_glossary table)
    ↓
User asks question
    ↓
API extracts relevant terms (semantic search)
    ↓
LLM generates contextual answer
    ↓
Return AI response + sources to frontend
```

---

## API Reference (Quick)

### 1. RAG Query
```typescript
const { query, result } = useRAG();

// Execute
await query("What is diabetes?", patientId);

// Result
result = {
  query: "What is diabetes?",
  ai_response: "...",
  relevant_terms: [...],
  confidence: 0.85
}
```

### 2. Glossary Search
```typescript
const { search, results } = useGlossarySearch();

await search("diabetes", limit=10);

// results = [
//   {
//     id: "1",
//     darija: "السكري",
//     french: "Diabète",
//     english: "Diabetes",
//     category: "Endocrine",
//     description: "..."
//   }
// ]
```

### 3. Risk Assessment
```typescript
const { calculate, result } = useRiskAssessment();

await calculate({
  patient_id: "uuid",
  age: 55,
  systolic_bp: 140,
  diastolic_bp: 90,
  fasting_glucose: 120,
  bmi: 28.5,
  smoking: true,
  family_history: true,
  comorbidities: 1
});

// result = {
//   risk_score: 0.72,
//   risk_level: "HIGH",
//   assessment_id: "uuid",
//   recommendations: [...]
// }
```

Full API docs: See `API_DOCUMENTATION.md`

---

## File Structure

```
/vercel/share/v0-project/
├── app/
│   ├── api/
│   │   ├── rag/
│   │   │   └── query/
│   │   │       └── route.ts          ← RAG query endpoint
│   │   ├── glossary/
│   │   │   └── search/
│   │   │       └── route.ts          ← Glossary search
│   │   └── assessments/
│   │       └── calculate/
│   │           └── route.ts          ← Risk calculation
│   └── hooks/
│       └── useRAG.ts                 ← React hooks for all 3 endpoints
│
├── scripts/
│   ├── rag_engine.py                 ← Python RAG orchestrator
│   ├── setup_db.py                   ← Database setup
│   └── load_glossary.py              ← Load medical glossary
│
├── migrations/
│   ├── 01_init_glossary.sql
│   └── 02_fix_schema_issues.sql      ← Latest schema fixes
│
├── database_setup_clean.sql          ← Main schema definition
├── maladies_export.json              ← Medical glossary data
├── requirements.txt                   ← Python dependencies
├── API_DOCUMENTATION.md              ← Complete API reference
├── DEPLOYMENT_GUIDE.md               ← Deploy to production
└── RAG_IMPLEMENTATION.md             ← This file
```

---

## How It Works: Example

### User asks: "What is diabetes in Darija?"

1. **Frontend sends request:**
   ```typescript
   const { result } = await query("What is diabetes in Darija?");
   ```

2. **API Route processes:**
   - Receives question
   - Searches `medical_glossary` for "diabetes"
   - Finds relevant terms with embeddings
   - Sends context to LLM

3. **LLM generates response:**
   ```
   Input: "What is diabetes in Darija?" + Medical context
   Output: "السكري (Darija: السكري) هو حالة مزمنة تؤثر على مستويات السكر في الدم..."
   ```

4. **API returns:**
   ```json
   {
     "query": "What is diabetes in Darija?",
     "ai_response": "السكري (Darija: السكري) هو...",
     "relevant_terms": [
       {
         "darija": "السكري",
         "english": "Diabetes",
         "description": "..."
       }
     ],
     "confidence": 0.92
   }
   ```

5. **Frontend displays:**
   - AI response
   - Confidence score
   - Source terms

---

## Deployment Checklist

- [ ] Database schema created in Supabase
- [ ] Medical glossary loaded (`maladies_export.json`)
- [ ] Environment variables set (NEXT_PUBLIC_SUPABASE_URL, ANON_KEY)
- [ ] `.env.local` created locally
- [ ] `pnpm install` completed
- [ ] `pnpm dev` runs without errors
- [ ] All 3 API endpoints tested locally
- [ ] Frontend hooks integrated into components
- [ ] Pushed to GitHub
- [ ] Deployed to Vercel
- [ ] Environment variables added to Vercel dashboard
- [ ] Tested in production (https://your-app.vercel.app)

---

## Key Features

✅ **Multilingual Support**
- Darija (Moroccan Arabic)
- French
- English

✅ **Semantic Search**
- Vector embeddings for medical terms
- Contextual relevance scoring
- Similar term suggestions

✅ **LLM Integration**
- Claude or OpenAI via Vercel AI Gateway
- Contextual medical answers
- Fallback to mock responses in dev

✅ **Patient Risk Assessment**
- Cardiovascular risk scoring
- Evidence-based recommendations
- Historical tracking

✅ **Production Ready**
- Row-level security (RLS)
- Error handling
- Rate limiting ready
- Serverless architecture

---

## Troubleshooting

### "Failed to fetch from API"
- Check NEXT_PUBLIC_SUPABASE_URL in .env.local
- Verify database tables exist
- Check browser console for errors

### "LLM returning generic responses"
- Add ANTHROPIC_API_KEY to .env.local
- Restart dev server
- Check API rate limits

### "No glossary results"
- Verify `maladies_export.json` loaded
- Run: `SELECT COUNT(*) FROM medical_glossary;` in Supabase
- Check RLS policies allow read access

### "Slow API responses"
- Check Supabase free tier limits
- Add database indexes (see DEPLOYMENT_GUIDE.md)
- Use caching for frequent queries

---

## Next Steps for Frontend Developers

1. **Create pages** using the provided hooks
2. **Add error boundaries** around RAG components
3. **Implement loading states** for better UX
4. **Cache results** client-side with SWR
5. **Add analytics** to track usage
6. **Optimize** based on user feedback

### Example Component
```typescript
'use client';

import { useRAG } from '@/app/hooks/useRAG';
import { useState } from 'react';

export function MedicalAssistantPage() {
  const { query, result, loading, error } = useRAG();
  const [input, setInput] = useState('');

  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1>Medical Assistant</h1>
      
      <div className="space-y-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a medical question..."
          className="w-full p-2 border rounded"
        />
        
        <button
          onClick={() => query(input)}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </div>

      {error && <p className="text-red-500">{error}</p>}

      {result && (
        <div className="mt-8 space-y-4">
          <div className="p-4 bg-gray-50 rounded">
            <p className="text-lg">{result.ai_response}</p>
          </div>
          
          <div className="text-sm text-gray-600">
            Confidence: {(result.confidence * 100).toFixed(0)}%
          </div>

          {result.relevant_terms.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Sources</h3>
              <ul className="space-y-2">
                {result.relevant_terms.map(term => (
                  <li key={term.id} className="text-sm">
                    <strong>{term.darija}</strong> / {term.english}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
```

---

## Support

- **API Docs:** `API_DOCUMENTATION.md`
- **Deployment:** `DEPLOYMENT_GUIDE.md`
- **Schema:** `database_setup_clean.sql`
- **RAG Engine:** `scripts/rag_engine.py`
- **React Hooks:** `app/hooks/useRAG.ts`

---

**Ready to build! 🚀**

Your frontend devs can now:
1. Import the hooks
2. Build UI components
3. Connect to the APIs
4. Deploy with confidence

Everything is production-ready. Just build the UI!
