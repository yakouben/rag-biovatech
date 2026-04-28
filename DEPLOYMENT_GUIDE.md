# RAG System Deployment Guide

Complete guide for setting up and deploying the RAG medical assistant.

## Architecture Overview

```
┌─────────────┐
│  Frontend   │  (React/Next.js 16)
│  (Nextjs)   │
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────────────────────┐
│  Next.js API Routes         │
│ ├─ /api/rag/query           │
│ ├─ /api/glossary/search     │
│ └─ /api/assessments/calculate
└──────┬──────────────────────┘
       │ SQL Queries
       ▼
┌──────────────────────────────┐
│  Supabase PostgreSQL         │
│ ├─ patients                  │
│ ├─ medical_glossary          │
│ ├─ patient_assessments       │
│ └─ model_metrics             │
└──────────────────────────────┘

Python RAG Engine (Optional - for enhanced embeddings)
├─ scripts/rag_engine.py
├─ Semantic search with vector embeddings
└─ LLM integration (Claude/OpenAI)
```

---

## Prerequisites

- Node.js 18+ (for Next.js)
- Python 3.10+ (for RAG engine)
- Supabase account (free tier works)
- OpenAI or Anthropic API key (optional for mock mode)

---

## Step 1: Supabase Setup

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Copy credentials (URL, ANON_KEY)

### 1.2 Initialize Database Schema
```bash
cd /vercel/share/v0-project

# Run migration script
psql -h <supabase-host> -U postgres -d postgres -f database_setup_clean.sql
# Or use Supabase SQL editor to paste the contents
```

### 1.3 Verify Tables Created
```sql
-- Check in Supabase SQL editor
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

---

## Step 2: Environment Setup

### 2.1 Create `.env.local`
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxxxx

# LLM (optional - uses Vercel AI Gateway zero-config if not set)
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# Python backend (if running RAG engine)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=xxxxx
```

### 2.2 Verify .env.local loaded
```bash
# Next.js will automatically pick up .env.local in development
echo $NEXT_PUBLIC_SUPABASE_URL
```

---

## Step 3: Load Medical Glossary Data

### 3.1 Check maladies_export.json exists
```bash
ls -lh /vercel/share/v0-project/maladies_export.json
```

### 3.2 Load glossary into Supabase
```bash
# Python script to load data
cd /vercel/share/v0-project
python scripts/load_glossary.py
```

Or manually via SQL:
```sql
-- Load from JSON file into medical_glossary table
INSERT INTO medical_glossary (darija_term, french_term, english_term, category, description)
SELECT 
  term->>'darija' as darija_term,
  term->>'french' as french_term,
  term->>'english' as english_term,
  term->>'category' as category,
  term->>'description' as description
FROM json_to_recordset(pg_read_file('maladies_export.json')) 
AS term(darija text, french text, english text, category text, description text);
```

---

## Step 4: Install Dependencies

### Frontend Dependencies
```bash
cd /vercel/share/v0-project
pnpm install
# or npm install / yarn install
```

### Python Dependencies (for RAG engine)
```bash
pip install -r requirements.txt
# or
uv sync
```

---

## Step 5: Run Locally

### Development Server
```bash
# Terminal 1: Start Next.js dev server
cd /vercel/share/v0-project
pnpm dev

# App runs at http://localhost:3000
```

### Test RAG Engine (Optional)
```bash
# Terminal 2: Test Python RAG
cd /vercel/share/v0-project
python scripts/rag_engine.py

# Output should show:
# [v0] RAG Query: What is diabetes?
# [v0] Found X relevant terms
# === RAG Result ===
# Query: What is diabetes?
# Confidence: 0.XX
# Response: ...
```

### Test API Endpoints
```bash
# Test glossary search
curl -X POST http://localhost:3000/api/glossary/search \
  -H "Content-Type: application/json" \
  -d '{"query":"diabetes","limit":5}'

# Test risk assessment
curl -X POST http://localhost:3000/api/assessments/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id":"test-123",
    "age":55,
    "systolic_bp":140,
    "diastolic_bp":90,
    "fasting_glucose":120,
    "bmi":28.5,
    "smoking":true,
    "family_history":true,
    "comorbidities":1
  }'

# Test RAG query
curl -X POST http://localhost:3000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is diabetes?","top_k":3}'
```

---

## Step 6: Deploy to Vercel

### 6.1 Connect GitHub Repository
```bash
# Push to GitHub
git remote add origin https://github.com/yourusername/rag-biovatech.git
git push -u origin main
```

### 6.2 Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login and deploy
vercel login
vercel deploy --prod
```

Or use Vercel dashboard:
1. Go to [vercel.com](https://vercel.com)
2. Import GitHub repository
3. Add environment variables (NEXT_PUBLIC_SUPABASE_URL, etc.)
4. Deploy

### 6.3 Configure Production Environment Variables
In Vercel dashboard → Settings → Environment Variables:
```
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

---

## Step 7: Verify Production

### Test deployed APIs
```bash
# Replace https://your-app.vercel.app with actual URL
curl https://your-app.vercel.app/api/glossary/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"diabetes"}'
```

### Monitor with Vercel Analytics
- Go to Vercel dashboard → Deployments
- Check logs for errors
- Monitor API response times

---

## Frontend Integration

### Use the provided React Hooks

```typescript
// components/MedicalAssistant.tsx
'use client';

import { useRAG, useGlossarySearch, useRiskAssessment } from '@/app/hooks/useRAG';

export function MedicalAssistant() {
  const { query, result, loading } = useRAG();
  const { search, results } = useGlossarySearch();

  return (
    <div>
      <h1>Medical Assistant</h1>
      
      {/* Search glossary */}
      <input 
        onChange={(e) => search(e.target.value)}
        placeholder="Search medical terms..."
      />
      <ul>
        {results.map(term => (
          <li key={term.id}>{term.darija} - {term.english}</li>
        ))}
      </ul>

      {/* RAG Query */}
      <button onClick={() => query("What is diabetes?")}>
        Ask
      </button>
      {result && <p>{result.ai_response}</p>}
    </div>
  );
}
```

---

## Troubleshooting

### "NEXT_PUBLIC_SUPABASE_URL is not set"
- Check `.env.local` in project root
- Restart dev server: `pnpm dev`

### "Failed to connect to Supabase"
- Verify credentials in Vercel Settings
- Test connection: `curl https://xxxxx.supabase.co/rest/v1/`

### "RAG query returns empty results"
- Check `medical_glossary` table has data
- Run: `SELECT COUNT(*) FROM medical_glossary;`

### "LLM returns generic responses"
- Anthropic/OpenAI key may be missing
- Falls back to mock responses in test mode
- Add `ANTHROPIC_API_KEY` to `.env.local`

### API responses are slow
- Check Supabase database size (free tier has limits)
- Consider adding indexes to `medical_glossary` table
- Monitor with Vercel Analytics

---

## Performance Optimization

### Add Vector Indexes (Production)
```sql
-- Speed up similarity search
CREATE INDEX ON medical_glossary USING ivfflat (embedding vector_cosine_ops);
```

### Cache Glossary Locally
```typescript
// hooks/useRAG.ts - add caching
const cache = new Map();

export function useGlossarySearch() {
  const [cache, setCache] = useState(new Map());
  
  const search = useCallback(async (query: string) => {
    if (cache.has(query)) {
      return cache.get(query);
    }
    // ... fetch and cache
  }, [cache]);
}
```

### Rate Limiting (Production)
Use Vercel's built-in rate limiting or add middleware:
```typescript
// middleware.ts
import { rateLimit } from '@/lib/rate-limit';

export async function middleware(request: NextRequest) {
  const ip = request.ip || 'unknown';
  const { success } = await rateLimit(ip);
  
  if (!success) {
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
  }
}
```

---

## Database Backup

### Backup Supabase Data
```bash
# Use Supabase CLI
supabase db pull --db-url "postgresql://..." > backup.sql

# Or manual backup
pg_dump -h xxxxx.supabase.co -U postgres -d postgres > backup.sql
```

---

## Support & Monitoring

### View Logs
- **Frontend:** Vercel dashboard → Deployments → Logs
- **Database:** Supabase dashboard → Logs
- **Python:** Check console output or use logging

### Monitor Performance
```bash
# View real-time metrics
curl https://your-app.vercel.app/api/health
```

---

## Next Steps

1. ✅ Database setup complete
2. ✅ API routes ready
3. ✅ Frontend hooks available
4. **Build your UI components** using the provided hooks
5. **Test all endpoints** before production
6. **Monitor** performance and errors in production
7. **Iterate** based on user feedback
