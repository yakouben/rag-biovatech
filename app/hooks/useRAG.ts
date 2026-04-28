'use client';

import { useState, useCallback } from 'react';

export interface GlossaryTerm {
  id: string;
  darija: string;
  french: string;
  english: string;
  category: string;
  description: string;
}

export interface RAGResult {
  query: string;
  ai_response: string;
  relevant_terms: GlossaryTerm[];
  confidence: number;
}

export interface UseRAGState {
  loading: boolean;
  error: string | null;
  result: RAGResult | null;
}

/**
 * Hook for RAG queries (semantic search + LLM)
 * 
 * Usage:
 * const { query, loading, result, error } = useRAG();
 * 
 * // Execute query
 * await query("What is diabetes?", patientId);
 */
export function useRAG() {
  const [state, setState] = useState<UseRAGState>({
    loading: false,
    error: null,
    result: null,
  });

  const query = useCallback(async (question: string, patientId?: string) => {
    setState({ loading: true, error: null, result: null });

    try {
      const response = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          patient_id: patientId,
          top_k: 3,
        }),
      });

      if (!response.ok) {
        throw new Error(`RAG query failed: ${response.statusText}`);
      }

      const result = (await response.json()) as RAGResult;
      setState({ loading: false, error: null, result });
      return result;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      setState({ loading: false, error: errorMsg, result: null });
      throw error;
    }
  }, []);

  return {
    ...state,
    query,
  };
}

/**
 * Hook for glossary term search
 * 
 * Usage:
 * const { search, results, loading } = useGlossarySearch();
 * await search("diabetes");
 */
export function useGlossarySearch() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<GlossaryTerm[]>([]);

  const search = useCallback(async (query: string, limit: number = 10) => {
    if (!query.trim()) {
      setResults([]);
      return [];
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/glossary/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      const glossaryResults = data.results || [];
      setResults(glossaryResults);
      return glossaryResults;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMsg);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    search,
    results,
    loading,
    error,
  };
}

/**
 * Hook for risk assessment calculations
 * 
 * Usage:
 * const { calculate, result, loading } = useRiskAssessment();
 * await calculate({ patient_id, age, systolic_bp, ... });
 */
export interface AssessmentInput {
  patient_id: string;
  age: number;
  systolic_bp: number;
  diastolic_bp: number;
  fasting_glucose: number;
  bmi: number;
  smoking: boolean;
  family_history: boolean;
  comorbidities: number;
}

export interface AssessmentResult {
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'VERY_HIGH';
  assessment_id: string;
  recommendations: string[];
  timestamp: string;
}

export function useRiskAssessment() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AssessmentResult | null>(null);

  const calculate = useCallback(async (data: AssessmentInput) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/assessments/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`Assessment calculation failed: ${response.statusText}`);
      }

      const result = (await response.json()) as AssessmentResult;
      setResult(result);
      return result;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMsg);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    calculate,
    result,
    loading,
    error,
  };
}
