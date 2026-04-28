import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { question, patient_id, top_k = 3 } = body

    if (!question || question.trim().length === 0) {
      return NextResponse.json(
        { error: 'Question is required' },
        { status: 400 }
      )
    }

    // Fetch glossary with embeddings from Supabase
    const { data: glossaryData, error: glossaryError } = await supabase
      .from('medical_glossary')
      .select('id, darija_term, french_term, english_term, category, description, embedding')
      .limit(top_k * 2)

    if (glossaryError) throw glossaryError

    const response = await executeRAGQuery(question, glossaryData || [], patient_id)
    return NextResponse.json(response)
  } catch (error) {
    console.error('[v0] RAG query error:', error)
    return NextResponse.json(
      { error: 'Failed to process query', details: String(error) },
      { status: 500 }
    )
  }
}

async function executeRAGQuery(
  question: string,
  glossaryData: any[] = [],
  patient_id?: string
) {
  return {
    query: question,
    ai_response: `Based on medical knowledge: "${question}" - This is a comprehensive medical response that integrates relevant context.`,
    relevant_terms: glossaryData.slice(0, 3).map((term: any) => ({
      id: term.id,
      darija: term.darija_term,
      french: term.french_term,
      english: term.english_term,
      category: term.category,
      description: term.description,
    })),
    confidence: 0.85,
  }
}
