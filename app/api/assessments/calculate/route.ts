import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

/**
 * POST /api/assessments/calculate
 * Calculate patient cardiovascular risk score based on health metrics
 * 
 * Request:
 * {
 *   "patient_id": "uuid",
 *   "age": 55,
 *   "systolic_bp": 140,
 *   "diastolic_bp": 90,
 *   "fasting_glucose": 120,
 *   "bmi": 28.5,
 *   "smoking": true,
 *   "family_history": true,
 *   "comorbidities": 1
 * }
 * 
 * Response:
 * {
 *   "risk_score": 0.72,
 *   "risk_level": "HIGH",
 *   "assessment_id": "uuid",
 *   "recommendations": [...]
 * }
 */

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
);

interface AssessmentData {
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

export async function POST(request: NextRequest) {
  try {
    const data: AssessmentData = await request.json();

    // Validate required fields
    const required = ['patient_id', 'age', 'systolic_bp', 'diastolic_bp', 'fasting_glucose', 'bmi', 'smoking', 'family_history', 'comorbidities'];
    for (const field of required) {
      if (!(field in data)) {
        return NextResponse.json(
          { error: `Missing required field: ${field}` },
          { status: 400 }
        );
      }
    }

    // Calculate risk score using Framingham-style algorithm
    const riskScore = calculateCVDRisk(data);
    const riskLevel = getRiskLevel(riskScore);
    const recommendations = generateRecommendations(data, riskLevel);

    // Save assessment to database
    const { data: assessment, error } = await supabase
      .from('patient_assessments')
      .insert({
        patient_id: data.patient_id,
        age: data.age,
        systolic_bp: data.systolic_bp,
        diastolic_bp: data.diastolic_bp,
        fasting_glucose: data.fasting_glucose,
        bmi: data.bmi,
        smoking: data.smoking,
        family_history: data.family_history,
        comorbidities: data.comorbidities,
        risk_score: riskScore,
        risk_level: riskLevel,
        assessment_date: new Date().toISOString(),
      })
      .select()
      .single();

    if (error) throw error;

    return NextResponse.json({
      risk_score: riskScore,
      risk_level: riskLevel,
      assessment_id: assessment?.id,
      recommendations,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('[v0] Assessment calculation error:', error);
    return NextResponse.json(
      { error: 'Assessment calculation failed', details: String(error) },
      { status: 500 }
    );
  }
}

/**
 * Framingham CVD Risk Score (simplified)
 * Based on: age, BP, glucose, BMI, lifestyle factors
 */
function calculateCVDRisk(data: AssessmentData): number {
  let score = 0;

  // Age factor (0-0.15)
  if (data.age >= 55) score += 0.15;
  else if (data.age >= 45) score += 0.10;

  // Blood pressure (0-0.20)
  if (data.systolic_bp >= 160 || data.diastolic_bp >= 100) score += 0.20;
  else if (data.systolic_bp >= 140 || data.diastolic_bp >= 90) score += 0.15;
  else if (data.systolic_bp >= 130 || data.diastolic_bp >= 80) score += 0.10;

  // Fasting glucose (0-0.20)
  if (data.fasting_glucose >= 200) score += 0.20;
  else if (data.fasting_glucose >= 126) score += 0.15;
  else if (data.fasting_glucose >= 100) score += 0.10;

  // BMI (0-0.15)
  if (data.bmi >= 35) score += 0.15;
  else if (data.bmi >= 30) score += 0.10;
  else if (data.bmi >= 25) score += 0.05;

  // Smoking (0-0.15)
  if (data.smoking) score += 0.15;

  // Family history (0-0.10)
  if (data.family_history) score += 0.10;

  // Comorbidities (0-0.15)
  score += Math.min(data.comorbidities * 0.05, 0.15);

  return Math.min(score, 1.0); // Cap at 1.0
}

function getRiskLevel(score: number): 'LOW' | 'MODERATE' | 'HIGH' | 'VERY_HIGH' {
  if (score >= 0.8) return 'VERY_HIGH';
  if (score >= 0.6) return 'HIGH';
  if (score >= 0.4) return 'MODERATE';
  return 'LOW';
}

function generateRecommendations(data: AssessmentData, riskLevel: string): string[] {
  const recommendations: string[] = [];

  if (riskLevel === 'HIGH' || riskLevel === 'VERY_HIGH') {
    recommendations.push('Consult with a cardiologist for further evaluation');
    recommendations.push('Consider daily blood pressure monitoring');
  }

  if (data.systolic_bp >= 140 || data.diastolic_bp >= 90) {
    recommendations.push('Implement lifestyle modifications: reduce sodium, increase exercise');
    recommendations.push('Discuss antihypertensive medication with your physician');
  }

  if (data.fasting_glucose >= 126) {
    recommendations.push('Screen for diabetes - follow up with endocrinologist');
    recommendations.push('Modify diet: reduce refined carbohydrates');
  }

  if (data.bmi >= 30) {
    recommendations.push('Weight management program recommended');
    recommendations.push('Increase physical activity to 150 min/week');
  }

  if (data.smoking) {
    recommendations.push('Smoking cessation program strongly recommended');
  }

  if (recommendations.length === 0) {
    recommendations.push('Maintain current healthy lifestyle');
    recommendations.push('Annual health check-ups recommended');
  }

  return recommendations;
}
