# ChronicCare Patient App - API Quick Reference

**Base URL**: `https://web-production-fadce.up.railway.app/api/v1`

---

## Authentication Flow

### 1. Patient Registration/Onboarding
```bash
POST https://web-production-fadce.up.railway.app/api/v1/patients/onboard
Content-Type: application/json

{
  "is_import": false,
  "profile": {
    "name": "Ahmed Ben Salah",
    "age": 52,
    "gender": "M",
    "phone": "+212612345678",
    "address": "123 Rue Mohamed V, Casablanca",
    "date_of_birth": "1971-06-15",
    "family_contact_name": "Fatima",
    "family_contact_phone": "+212699999999",
    "medical_history_summary": "Type 2 diabetes, hypertension"
  },
  "initial_vitals": {
    "age": 52,
    "systolic_bp": 145,
    "diastolic_bp": 90,
    "fasting_glucose": 150,
    "bmi": 28.5,
    "smoking": false,
    "family_history": true,
    "comorbidities": 1
  }
}
```

**Response**: `{ patient_id, status, message, initial_risk, ai_analysis }`

---

## Daily Vitals & AI Analysis

### 2. Submit Vitals + Get AI Analysis (Primary Endpoint)
```bash
POST https://web-production-fadce.up.railway.app/api/v1/chat
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "patient_id": "pat_abc123xyz",
  "patient_symptoms": "شعرت بإرهاق شديد واحتياج متكرر للتبول وآلام في الرأس",
  "include_glossary": true,
  "patient_data": {
    "age": 52,
    "systolic_bp": 145,
    "diastolic_bp": 90,
    "fasting_glucose": 180,
    "bmi": 28.5,
    "smoking": false,
    "family_history": true,
    "comorbidities": 1
  }
}
```

**Response**:
```json
{
  "hela_response": "المريض يعاني من أعراض السكري المهمة...",
  "extracted_entities": {
    "symptoms": ["fatigue", "frequent urination", "headache"],
    "medications": [],
    "missed_medications": [],
    "vitals": {
      "systolic_bp": 145,
      "diastolic_bp": 90,
      "glucose": 180
    },
    "severity_hints": ["severe fatigue"],
    "clinical_note": "Patient reports severe fatigue, frequent urination, and headache"
  },
  "risk_score": "HIGH",
  "confidence": 0.85,
  "factors": ["Elevated glucose (180)", "High blood pressure", "Family history"],
  "monitoring_frequency": "Weekly",
  "glossary_context": [
    {
      "darija": "السكري",
      "french": "Diabète",
      "english": "Diabetes",
      "category": "endocrine"
    }
  ]
}
```

---

### 3. Get Patient History (For Charts)
```bash
GET https://web-production-fadce.up.railway.app/api/v1/patient/{patient_id}/history?days=30
Authorization: Bearer {JWT_TOKEN}
```

**Response**:
```json
{
  "patient_id": "pat_abc123xyz",
  "count": 15,
  "history": [
    {
      "date": "2024-01-01T09:00:00Z",
      "risk": 4.2,
      "systolic": 130,
      "diastolic": 85,
      "glucose": 140,
      "summary": "Patient feeling better, took all medications"
    },
    {
      "date": "2024-01-02T10:15:00Z",
      "risk": 5.0,
      "systolic": 135,
      "diastolic": 88,
      "glucose": 155,
      "summary": "Mild fatigue reported"
    }
  ]
}
```

---

### 4. Get Patient Profile
```bash
GET https://web-production-fadce.up.railway.app/api/v1/patient/{patient_id}/profile
Authorization: Bearer {JWT_TOKEN}
```

**Response**:
```json
{
  "id": "pat_abc123xyz",
  "name": "Ahmed Ben Salah",
  "age": 52,
  "gender": "M",
  "phone": "+212612345678",
  "address": "123 Rue Mohamed V, Casablanca",
  "date_of_birth": "1971-06-15",
  "family_contact_name": "Fatima (Daughter)",
  "family_contact_phone": "+212699999999",
  "family_access_granted": true,
  "medical_history_summary": "Type 2 diabetes x5 years, hypertension",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Risk Assessment & Monitoring

### 5. Check for Adherence Drop (Proactive Alert)
```bash
GET https://web-production-fadce.up.railway.app/api/v1/patient/{patient_id}/check-drift
Authorization: Bearer {JWT_TOKEN}
```

**Response**:
```json
{
  "patient_id": "pat_abc123xyz",
  "adherence_drop_detected": true,
  "adherence_score_previous": 0.92,
  "adherence_score_current": 0.65,
  "nurture_message": "We noticed you missed some log-ins this week. How can we help?",
  "recommendations": [
    "Enable medication reminders",
    "Check if medication is causing side effects",
    "Schedule a call with your doctor"
  ]
}
```

---

## Medical Education

### 6. Search Medical Glossary
```bash
POST https://web-production-fadce.up.railway.app/api/v1/glossary/search
Content-Type: application/json

{
  "query": "chest pain and difficulty breathing",
  "limit": 10,
  "language": "french"
}
```

**Response**:
```json
[
  {
    "id": 42,
    "darija": "ألم صدري",
    "french": "Douleur thoracique",
    "english": "Chest pain",
    "category": "cardiovascular"
  },
  {
    "id": 89,
    "darija": "ضيق التنفس",
    "french": "Dyspnée",
    "english": "Shortness of breath",
    "category": "respiratory"
  }
]
```

### 7. Get Full Glossary (Paginated)
```bash
GET https://web-production-fadce.up.railway.app/api/v1/glossary?skip=0&limit=50
```

---

## Reports

### 8. Generate PDF Clinical Report
```bash
POST https://web-production-fadce.up.railway.app/api/v1/reports/generate?patient_id=pat_abc123xyz&patient_name=Ahmed Ben Salah&adherence_days=30
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "patient_id": "pat_abc123xyz",
  "patient_symptoms": "Fatigue and frequent urination",
  "include_glossary": true,
  "patient_data": {
    "age": 52,
    "systolic_bp": 145,
    "diastolic_bp": 90,
    "fasting_glucose": 150,
    "bmi": 28.5,
    "smoking": false,
    "family_history": true,
    "comorbidities": 1
  }
}
```

**Response**: PDF file (binary)  
**Header**: `Content-Type: application/pdf`

---

## System Status

### 9. Health Check
```bash
GET https://web-production-fadce.up.railway.app/api/v1/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "gemini": "initialized",
    "model": "loaded",
    "environment": "production"
  }
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid patient data",
  "details": {
    "age": "must be between 0 and 150",
    "fasting_glucose": "must be between 40 and 500"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing/invalid JWT
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Backend error

---

## Frontend Integration Examples

### TypeScript API Client
```typescript
import axios from 'axios';

const API_BASE_URL = 'https://web-production-fadce.up.railway.app/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Example: Submit vitals
export const submitVitals = async (patientId: string, symptoms: string, vitals: any) => {
  return apiClient.post('/chat', {
    patient_id: patientId,
    patient_symptoms: symptoms,
    include_glossary: true,
    patient_data: vitals,
  });
};

// Example: Get history
export const getPatientHistory = async (patientId: string, days: number = 30) => {
  return apiClient.get(`/patient/${patientId}/history`, {
    params: { days },
  });
};
```

### SWR Hook Example
```typescript
import useSWR from 'swr';

const fetcher = (url: string) =>
  apiClient.get(url).then((res) => res.data);

export const usePatientHistory = (patientId: string, days: number = 30) => {
  const { data, error, isLoading, mutate } = useSWR(
    patientId ? `/patient/${patientId}/history?days=${days}` : null,
    fetcher,
    { revalidateOnFocus: false, revalidateInterval: 30000 } // Refetch every 30s
  );

  return {
    history: data?.history || [],
    isLoading,
    isError: !!error,
    mutate,
  };
};
```

---

## Notes

- All timestamps are in **ISO 8601 format** (UTC)
- All currency values (if applicable) are in **patient's local currency**
- Glucose values are in **mg/dL** (mg per deciliter)
- Blood pressure is in **mmHg** (millimeters of mercury)
- BMI is in **kg/m²** (kilograms per square meter)
- Always include **JWT token** in `Authorization` header for protected endpoints
- Maximum request body size: **1 MB**
- Rate limit: **100 requests per minute** per IP

---

**Last Updated**: January 2024  
**Status**: Production Ready
