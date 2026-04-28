import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const { query, limit = 10 } = await request.json()

    if (!query || query.trim().length < 2) {
      return NextResponse.json(
        { error: 'Query must be at least 2 characters' },
        { status: 400 }
      )
    }

    const { data: results, error } = await supabase
      .from('medical_glossary')
      .select('id, darija_term, french_term, english_term, category, description')
      .or(
        `darija_term.ilike.%${query}%,french_term.ilike.%${query}%,english_term.ilike.%${query}%,description.ilike.%${query}%`
      )
      .limit(limit)

    if (error) throw error

    return NextResponse.json({
      results: results || [],
      count: results?.length || 0,
      query,
    })
  } catch (error) {
    console.error('[v0] Glossary search error:', error)
    return NextResponse.json(
      { error: 'Search failed', details: String(error) },
      { status: 500 }
    )
  }
}
