# RAG Medical Assistant API Documentation

Complete API reference for the RAG (Retrieval-Augmented Generation) medical system.

## Base URL
```
http://localhost:3000/api
```

---

## 1. RAG Query Endpoint

**Purpose:** Execute semantic search + LLM generation for medical Q&A

### Request
```http
POST /rag/query
Content-Type: application/json

{
  "question": "What is diabetes in Darija?",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",  // Optional
  "top_k": 3                                               // Number of relevant terms (default: 3)
}
```

### Response (200 OK)
```json
{
  "query": "What is diabetes in Darija?",
  "ai_response": "السكري (السكري) هو حالة مزمنة تؤثر على مستويات السكر في الدم...",
  "relevant_terms": [
    {
      "id": "1",
      "darija": "السكري",
      "french": "Diabète",
      "english": "Diabetes",
      "category": "Endocrine",
      "description": "A chronic condition affecting blood sugar levels"
    }
  ],
  "confidence": 0.85
}
```

### Error Responses
- **400 Bad Request:** Question is required or invalid format
- **500 Internal Server Error:** LLM or search service failed

### Client Usage (React)
```typescript
import { useRAG } from '@/app/hooks/useRAG';

function MedicalAssistant() {
  const { query, result, loading, error } = useRAG();

  const handleQuery = async () => {
    await query("What is diabetes?", patientId);
  };

  return (
    <div>
      <button onClick={handleQuery} disabled={loading}>
        {loading ? 'Searching...' : 'Ask'}
      </button>
      {result && <p>{result.ai_response}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
```

---

## 2. Glossary Search Endpoint

**Purpose:** Full-text search over medical glossary (Darija/French/English)

### Request
```http
POST /glossary/search
Content-Type: application/json

{
  "query": "diabetes",
  "limit": 10  // Optional, default: 10
}
```

### Response (200 OK)
```json
{
  "results": [
    {
      "id": "1",
      "darija_term": "السكري",
      "french_term": "Diabète",
      "english_term": "Diabetes",
      "category": "Endocrine",
      "severity": 3,
      "description": "A chronic metabolic disorder...",
      "related_terms": ["glucose", "insulin", "hyperglycemia"]
    }
  ],
  "count": 1,
  "query": "diabetes"
}
```

### Client Usage (React)
```typescript
import { useGlossarySearch } from '@/app/hooks/useRAG';

function SearchMedicalTerms() {
  const { search, results, loading } = useGlossarySearch();

  return (
    <div>
      <input 
        onChange={(e) => search(e.target.value)}
        placeholder="Search medical terms..."
      />
      {loading && <p>Searching...</p>}
      <ul>
        {results.map(term => (
          <li key={term.id}>
            <strong>{term.darija_term}</strong> - {term.english_term}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 3. Risk Assessment Endpoint

**Purpose:** Calculate cardiovascular risk score based on patient health metrics

### Request
```http
POST /assessments/calculate
Content-Type: application/json

{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "age": 55,
  "systolic_bp": 140,
  "diastolic_bp": 90,
  "fasting_glucose": 120,
  "bmi": 28.5,
  "smoking": true,
  "family_history": true,
  "comorbidities": 1
}
```

### Response (200 OK)
```json
{
  "risk_score": 0.72,
  "risk_level": "HIGH",
  "assessment_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "recommendations": [
    "Consult with a cardiologist for further evaluation",
    "Consider daily blood pressure monitoring",
    "Implement lifestyle modifications: reduce sodium, increase exercise",
    "Discuss antihypertensive medication with your physician"
  ],
  "timestamp": "2024-04-28T16:35:00.000Z"
}
```

### Risk Levels
| Score | Level | Action |
|-------|-------|--------|
| < 0.4 | LOW | Maintain healthy lifestyle, annual check-ups |
| 0.4 - 0.6 | MODERATE | Lifestyle modifications, quarterly monitoring |
| 0.6 - 0.8 | HIGH | Specialist consultation, medication consideration |
| ≥ 0.8 | VERY_HIGH | Immediate medical intervention |

### Client Usage (React)
```typescript
import { useRiskAssessment } from '@/app/hooks/useRAG';

function RiskCalculator() {
  const { calculate, result, loading } = useRiskAssessment();

  const handleSubmit = async (formData) => {
    await calculate(formData);
  };

  return (
    <div>
      <form onSubmit={(e) => {
        e.preventDefault();
        handleSubmit({
          patient_id: formData.patient_id,
          age: parseInt(formData.age),
          systolic_bp: parseInt(formData.systolic_bp),
          diastolic_bp: parseInt(formData.diastolic_bp),
          fasting_glucose: parseInt(formData.fasting_glucose),
          bmi: parseFloat(formData.bmi),
          smoking: formData.smoking === 'true',
          family_history: formData.family_history === 'true',
          comorbidities: parseInt(formData.comorbidities),
        });
      }}>
        {/* Form fields */}
        <button disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Risk'}
        </button>
      </form>

      {result && (
        <div>
          <h3>Risk Level: {result.risk_level}</h3>
          <p>Score: {(result.risk_score * 100).toFixed(1)}%</p>
          <ul>
            {result.recommendations.map((rec, i) => (
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

## Error Handling

All endpoints follow standard HTTP status codes:

### 400 Bad Request
Missing or invalid required fields
```json
{
  "error": "Missing required field: age",
  "details": "..."
}
```

### 500 Internal Server Error
Server-side processing failed
```json
{
  "error": "Assessment calculation failed",
  "details": "Database connection error"
}
```

### Client Error Handling Example
```typescript
try {
  await query("What is diabetes?");
} catch (error) {
  console.error('RAG query failed:', error);
  // Show user-friendly error message
}
```

---

## Environment Variables Required

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxxxx

# LLM (optional - falls back to mock)
ANTHROPIC_API_KEY=xxxxx
OPENAI_API_KEY=xxxxx
```

---

## Rate Limiting (Production)

Recommended rate limits:
- RAG Query: 10 requests/minute per user
- Glossary Search: 30 requests/minute per user
- Assessment Calculate: 5 requests/minute per user

---

## Examples

### Complete Flow: Patient Assessment + Medical Consultation

```typescript
import { useRAG, useRiskAssessment } from '@/app/hooks/useRAG';

function PatientFlow() {
  const { query: ragQuery } = useRAG();
  const { calculate } = useRiskAssessment();

  async function handlePatient(patientData) {
    // Step 1: Calculate risk
    const riskResult = await calculate({
      patient_id: patientData.id,
      age: patientData.age,
      systolic_bp: patientData.systolic_bp,
      diastolic_bp: patientData.diastolic_bp,
      fasting_glucose: patientData.fasting_glucose,
      bmi: patientData.bmi,
      smoking: patientData.smoking,
      family_history: patientData.family_history,
      comorbidities: patientData.comorbidities,
    });

    // Step 2: Generate medical consultation based on risk
    const ragResult = await ragQuery(
      `Patient has ${riskResult.risk_level} cardiovascular risk. What are key interventions?`,
      patientData.id
    );

    return {
      risk: riskResult,
      consultation: ragResult,
    };
  }

  return (
    // UI implementation
  );
}
```

---

## Support & Debugging

Check console logs for:
```
[v0] RAG Query: What is diabetes?
[v0] Found 3 relevant terms
[v0] LLM response generated
```

For detailed debugging, check `/vercel/share/v0-project/scripts/rag_engine.py` logs.
