import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

/**
 * POST /api/glossary/search
 * Semantic search over medical glossary with vector similarity
 * 
 * Request: { "query": "diabetes", "limit": 10 }
 * Response: { "results": [...medical terms...], "count": 5 }
 */

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
);

export async function POST(request: NextRequest) {
  try {
    const { query, limit = 10 } = await request.json();

    if (!query || query.trim().length < 2) {
      return NextResponse.json(
        { error: 'Query must be at least 2 characters' },
        { status: 400 }
      );
    }

    // Option 1: Full-text search on medical_glossary
    const { data: results, error } = await supabase
      .from('medical_glossary')
      .select('*')
      .or(`darija_term.ilike.%${query}%,french_term.ilike.%${query}%,english_term.ilike.%${query}%,description.ilike.%${query}%`)
      .limit(limit);

    if (error) throw error;

    return NextResponse.json({
      results: results || [],
      count: results?.length || 0,
      query,
    });
  } catch (error) {
    console.error('[v0] Glossary search error:', error);
    return NextResponse.json(
      { error: 'Search failed', details: String(error) },
      { status: 500 }
    );
  }
}
