-- Migration: Create medical_knowledge table for RAG guidelines
-- 04_create_medical_knowledge.sql

-- Enable pgvector if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create medical_knowledge table
CREATE TABLE IF NOT EXISTS medical_knowledge (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    embedding vector(3072), -- For gemini-embedding-2
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Disable RLS for MVP to allow easy ingestion
ALTER TABLE medical_knowledge DISABLE ROW LEVEL SECURITY;

-- No index needed for MVP (pgvector dimension limit 2000)
-- Sequential scan is fine for small knowledge bases

-- Function for similarity search
CREATE OR REPLACE FUNCTION search_medical_knowledge (
  query_embedding vector(3072),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id int,
  category TEXT,
  title TEXT,
  content TEXT,
  source TEXT,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    medical_knowledge.id,
    medical_knowledge.category,
    medical_knowledge.title,
    medical_knowledge.content,
    medical_knowledge.source,
    1 - (medical_knowledge.embedding <=> query_embedding) AS similarity
  FROM medical_knowledge
  WHERE 1 - (medical_knowledge.embedding <=> query_embedding) > match_threshold
  ORDER BY medical_knowledge.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
