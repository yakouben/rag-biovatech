# Supabase Database Setup Guide

## Step 1: Enable pgvector Extension

1. Go to your Supabase project dashboard
2. Click on **SQL Editor** in the left sidebar
3. Click **New Query**
4. Paste this SQL and run it:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Step 2: Create the Medical Glossary Table

In the SQL Editor, paste and run this:

```sql
CREATE TABLE IF NOT EXISTS medical_glossary (
    id BIGSERIAL PRIMARY KEY,
    darija_term TEXT NOT NULL UNIQUE,
    french_term TEXT,
    english_term TEXT,
    category TEXT,
    severity INTEGER DEFAULT 1,
    description TEXT,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_medical_glossary_darija ON medical_glossary(darija_term);
CREATE INDEX IF NOT EXISTS idx_medical_glossary_category ON medical_glossary(category);
CREATE INDEX IF NOT EXISTS idx_medical_glossary_embedding ON medical_glossary USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Enable Row Level Security (optional, for production)
ALTER TABLE medical_glossary ENABLE ROW LEVEL SECURITY;
```

## Step 3: Verify Table Creation

Run this query to confirm the table was created:

```sql
SELECT * FROM medical_glossary LIMIT 1;
```

You should see the table schema with no errors.

## Step 4: Seed the Glossary Data

Once the table is created, go back to your terminal and run:

```bash
cd /vercel/share/v0-project
source .venv/bin/activate
python setup_db.py
```

This will populate the table with 150+ Algerian medical terms.

## Step 5: Verify Data is Seeded

In Supabase SQL Editor, run:

```sql
SELECT COUNT(*) as total_terms FROM medical_glossary;
SELECT DISTINCT category FROM medical_glossary;
```

You should see ~150 terms across multiple categories.

## Step 6: Start the Server

```bash
cd /vercel/share/v0-project
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

## Step 7: Test the Endpoints

Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try these endpoints:
1. **GET /health** - Should return 200
2. **GET /api/v1/glossary/all** - Should return all 150+ terms
3. **GET /api/v1/glossary/search?term=السكري** - Should return diabetes term

## Troubleshooting

### If you get "relation medical_glossary does not exist"
- Make sure you ran the CREATE TABLE SQL in Step 2
- Verify the table exists in Supabase: Tables > medical_glossary

### If setup_db.py fails with auth error
- Double-check your SUPABASE_URL and SUPABASE_KEY in .env
- Make sure the .env file is in /vercel/share/v0-project/

### If embeddings fail
- Ensure GEMINI_API_KEY is set in .env
- Test with: `curl -X POST http://localhost:8000/api/v1/embedding -H "Content-Type: application/json" -d '{"text":"hello"}'`

## All Done!

Your ChronicCare YAKOUB FastAPI service is now ready with:
- ✅ Supabase database connected
- ✅ Medical glossary table with 150+ terms
- ✅ pgvector embeddings ready
- ✅ All 8 endpoints functional

Happy coding!
