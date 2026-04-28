# ChronicCare AI System - Complete Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Database Schema](#database-schema)
5. [Integration Points](#integration-points)
6. [Critical Fixes Applied](#critical-fixes-applied)
7. [Medical Glossary (Darija)](#medical-glossary-darija)
8. [Development Workflow](#development-workflow)
9. [Deployment & Environment](#deployment--environment)

---

## System Overview

**ChronicCare AI** is a FastAPI-based healthcare intelligence system designed to provide clinical decision support for chronic disease management, particularly targeting the Moroccan healthcare market with Darija (Moroccan Arabic) language support.

### Key Features
- **Clinical Reasoning**: NOUR (Needs-Oriented Understanding Response) framework for patient assessment
- **Risk Scoring**: Automatic patient risk stratification (HIGH, MODERATE, LOW)
- **Medical Glossary**: Comprehensive Darija/French/English medical terminology database
- **Drift Detection**: Identifies patient health deterioration patterns
- **PDF Reports**: Generates clinical reports for patient records
- **RAG (Retrieval-Augmented Generation)**: Context-aware responses using medical knowledge base

### Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **AI Engine**: Google Gemini API
- **Deployment**: Vercel
- **Language Models**: Gemini for natural language processing

---

## Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Seghir Express (Frontend)                 │
│                  (Calls POST /ai/chat)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Request
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Application                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         API Routes Layer (/api/v1, /ai)             │  │
│  │  - /ai/chat (Primary Endpoint)                      │  │
│  │  - /ai/drift/{patient_id}                           │  │
│  │  - /ai/pdf/{patient_id}                             │  │
│  │  - /ai/glossary                                     │  │
│  │  - /api/v1/health (Health Check)                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │         Service Layer (Business Logic)             │  │
│  │                                                     │  │
│  │  ┌─────────────────────────────────────────┐      │  │
│  │  │ GeminiService                           │      │  │
│  │  │ - generate_nour_response()              │      │  │
│  │  │ - generate_clinical_reasoning()         │      │  │
│  │  └─────────────────────────────────────────┘      │  │
│  │                                                     │  │
│  │  ┌─────────────────────────────────────────┐      │  │
│  │  │ RiskService                             │      │  │
│  │  │ - assess_patient_risk()                 │      │  │
│  │  │ - calculate_risk_factors()              │      │  │
│  │  └─────────────────────────────────────────┘      │  │
│  │                                                     │  │
│  │  ┌─────────────────────────────────────────┐      │  │
│  │  │ RAGService                              │      │  │
│  │  │ - search_medical_terms()                │      │  │
│  │  │ - build_glossary_context()              │      │  │
│  │  └─────────────────────────────────────────┘      │  │
│  │                                                     │  │
│  │  ┌─────────────────────────────────────────┐      │  │
│  │  │ DriftService                            │      │  │
│  │  │ - detect_health_deterioration()         │      │  │
│  │  │ - identify_critical_changes()           │      │  │
│  │  └─────────────────────────────────────────┘      │  │
│  │                                                     │  │
│  │  ┌─────────────────────────────────────────┐      │  │
│  │  │ PDFService                              │      │  │
│  │  │ - generate_report()                     │      │  │
│  │  │ - format_clinical_data()                │      │  │
│  │  └─────────────────────────────────────────┘      │  │
│  └─────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │     Data Access Layer (Database)                    │  │
│  │                                                     │  │
│  │  • Supabase Connection                              │  │
│  │  • Query Builder / ORM                              │  │
│  │  • Row Level Security (RLS)                         │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          │ Database Queries
                          │
┌─────────────────────────▼────────────────────────────────────┐
│              Supabase PostgreSQL Database                     │
│                                                               │
│  Tables:                                                      │
│  - users (patient profiles)                                  │
│  - conversations (chat history)                              │
│  - medical_glossary (Darija/French/English terms)            │
│  - risk_scores (assessment history)                          │
│  - patient_data (vital signs, measurements)                  │
│  - drift_detection_logs (health change tracking)             │
└────────────────────────────────────────────────────────────────┘
```

### Service Layer Details

#### 1. **GeminiService**
Handles all natural language processing and clinical reasoning using Google Gemini API.

```python
# Key Methods
generate_nour_response(patient_symptoms, glossary_context, risk_assessment)
  → Returns clinical assessment in Darija/French

generate_clinical_reasoning(patient_data, medical_history)
  → Generates detailed clinical analysis
```

#### 2. **RiskService**
Calculates patient risk scores based on medical factors.

```python
# Key Methods
assess_patient_risk(patient_data)
  → Returns: {
       "category": "HIGH" | "MODERATE" | "LOW",
       "probabilities": {"high": 0.8, "moderate": 0.15, ...},
       "recommendations": ["Monitor daily", "Reduce salt intake", ...],
       "monitoring_frequency": "daily" | "weekly" | "monthly"
     }
```

#### 3. **RAGService**
Retrieves and augments responses with medical knowledge base context.

```python
# Key Methods
search_medical_terms(symptoms, limit=5)
  → Returns relevant glossary entries from medical_glossary table

build_glossary_context(darija_terms)
  → Constructs contextual explanations for patient understanding
```

#### 4. **DriftService**
Detects changes in patient health status over time.

```python
# Key Methods
detect_health_deterioration(patient_id, time_window="30days")
  → Identifies critical health changes requiring intervention
```

#### 5. **PDFService**
Generates clinical reports in PDF format for patient records.

```python
# Key Methods
generate_report(patient_id, patient_name, data)
  → Returns: FileResponse (PDF document)
```

---

## API Endpoints

### Primary Endpoint: `/ai/chat` (POST)

**Purpose**: Main endpoint for patient-doctor interaction with integrated risk assessment.

**Request**:
```json
{
  "patient_id": "uuid",
  "patient_symptoms": "وجع الراس، نخنق، حريق المعدة",
  "patient_data": {
    "age": 45,
    "weight_kg": 85,
    "blood_pressure": "140/90",
    "existing_conditions": ["diabetes", "hypertension"],
    "current_medications": ["metformin", "lisinopril"]
  },
  "include_glossary": true
}
```

**Response**:
```json
{
  "nour_response": "بناء على الأعراض اللي قلتي...",
  "extracted_entities": {
    "symptoms": ["وجع الراس", "نخنق", "حريق المعدة"],
    "missed_meds": []
  },
  "risk_score": "HIGH",
  "confidence": 0.85,
  "factors": ["High blood pressure", "Recent weight loss", "Chest pain"],
  "monitoring_frequency": "daily",
  "glossary_context": [
    {
      "darija_term": "وجع الراس",
      "french_term": "Migraine",
      "english_term": "Headache",
      "description": "..."
    }
  ]
}
```

**Headers**:
```
x-internal-key: YOUR_INTERNAL_API_KEY
Content-Type: application/json
```

---

### Secondary Endpoints

#### `/ai/drift/{patient_id}` (POST)
Detects health deterioration patterns.

**Request**:
```json
{
  "time_window": "30days",
  "vital_signs": {
    "blood_pressure": "145/95",
    "weight": 82
  }
}
```

**Response**:
```json
{
  "drift_detected": true,
  "severity": "medium",
  "changes": [
    {
      "metric": "blood_pressure",
      "previous": "140/90",
      "current": "145/95",
      "change_percent": 3.5,
      "recommendation": "Schedule appointment"
    }
  ]
}
```

---

#### `/ai/pdf/{patient_id}` (POST)
Generates clinical report PDF.

**Request**:
```json
{
  "patient_name": "Ahmed Ben Salah",
  "include_risk_assessment": true,
  "date_range": "last_30_days"
}
```

**Response**: Binary PDF file

---

#### `/ai/glossary` (GET)
Retrieves all medical glossary entries.

**Query Parameters**:
- `skip`: 0 (pagination)
- `limit`: 100

**Response**:
```json
{
  "total": 204,
  "items": [
    {
      "id": 103,
      "darija_term": "السكري",
      "french_term": "Diabète",
      "english_term": "Diabetes",
      "category": "endocrine",
      "severity": 1
    }
  ]
}
```

---

#### `/ai/glossary/match` (POST)
Searches glossary by medical term.

**Request**:
```json
{
  "query": "السكري",
  "limit": 5,
  "language": "darija"
}
```

**Response**:
```json
{
  "matches": [
    {
      "darija_term": "السكري",
      "match_score": 0.98,
      "related_terms": ["نسبة السكر في الدم", "السكري من النوع الثاني"]
    }
  ]
}
```

---

#### `/api/v1/health` (GET)
System health check.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-04-28T10:00:00Z",
  "dependencies": {
    "database": "connected",
    "gemini_api": "available",
    "rag_service": "ready"
  }
}
```

---

## Database Schema

### Table: `users`
Patient profiles and metadata.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  age INT,
  gender VARCHAR(10),
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(20),
  medical_id VARCHAR(50) UNIQUE,
  profile_data JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Table: `medical_glossary`
Medical terminology in Darija, French, and English.

```sql
CREATE TABLE medical_glossary (
  id BIGINT PRIMARY KEY,
  darija_term VARCHAR(255) NOT NULL,
  french_term VARCHAR(255),
  english_term VARCHAR(255),
  category VARCHAR(100),
  severity INT,
  description TEXT,
  related_terms TEXT[],
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Categories**:
- endocrine
- cardiovascular
- respiratory
- gastrointestinal
- renal
- neurological
- rheumatological
- medication
- symptoms
- vital_signs
- lab_tests
- imaging
- lifestyle
- preventive_care
- medical_history

### Table: `conversations`
Chat history and interactions.

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  patient_symptoms TEXT NOT NULL,
  ai_response TEXT NOT NULL,
  risk_score VARCHAR(20),
  confidence FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Table: `risk_scores`
Historical risk assessment records.

```sql
CREATE TABLE risk_scores (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  assessment_date TIMESTAMP,
  risk_category VARCHAR(20),
  confidence FLOAT,
  factors TEXT[],
  monitoring_frequency VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Table: `patient_data`
Vital signs and measurements.

```sql
CREATE TABLE patient_data (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  blood_pressure VARCHAR(20),
  heart_rate INT,
  weight_kg FLOAT,
  height_cm FLOAT,
  temperature_c FLOAT,
  glucose_level INT,
  measurement_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Table: `drift_detection_logs`
Health change tracking.

```sql
CREATE TABLE drift_detection_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  drift_detected BOOLEAN,
  severity VARCHAR(20),
  changes JSONB,
  detection_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Integration Points

### 1. Seghir Express Integration

**Seghir's Express app** calls your AI service at the `/ai/chat` endpoint:

```javascript
// Example from Seghir's frontend
const response = await fetch('https://your-api.vercel.app/ai/chat', {
  method: 'POST',
  headers: {
    'x-internal-key': process.env.INTERNAL_API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    patient_id: patientId,
    patient_symptoms: userInput,
    patient_data: patientProfile,
    include_glossary: true
  })
});
```

**Response Flow**:
1. Seghir sends patient symptoms
2. Your AI system:
   - Assesses risk (RiskService)
   - Generates clinical response (GeminiService)
   - Fetches medical glossary context (RAGService)
   - Merges everything into unified response
3. Seghir receives risk_score + clinical assessment in single call

### 2. Gemini API Integration

**Configuration**:
```python
from app.services.gemini_service import get_gemini_service

service = get_gemini_service()
response = service.generate_nour_response(
    patient_symptoms="وجع الراس",
    glossary_context="[medical terms]",
    risk_assessment="HIGH"
)
```

**Environment Variable**:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Supabase Integration

**Connection**:
```python
from supabase import create_client

supabase = create_client(
    url=os.getenv("SUPABASE_URL"),
    key=os.getenv("SUPABASE_KEY")
)
```

**Usage**:
```python
# Fetch glossary
glossary = supabase.table("medical_glossary").select("*").execute()

# Update risk score
supabase.table("risk_scores").insert({
    "user_id": patient_id,
    "risk_category": "HIGH",
    "confidence": 0.85
}).execute()
```

---

## Critical Fixes Applied

### Fix 1: Contract-Compliant Routes (`/ai/*` prefix)

**Problem**: Seghir's Express service expected endpoints at `/ai/*` but your system only had `/api/v1/*`.

**Solution**:
- Added new `/ai/chat` endpoint as primary entry point
- Created route aliases mapping `/ai/*` to existing `/api/v1/*` handlers
- Maintains backward compatibility with both prefixes

**Files Modified**:
- `app/routes/api.py` - Added `/ai/chat` endpoint
- `app/main.py` - Added route aliasing layer

**Location**: Lines 54-140 in `app/routes/api.py`

---

### Fix 2: Risk Scoring Merged into `/ai/chat`

**Problem**: Risk assessment was a separate endpoint, requiring Seghir to make multiple API calls.

**Solution**:
- Integrated RiskService directly into `/ai/chat` response
- Single endpoint returns: clinical response + risk_score + confidence + factors
- Reduces latency and improves user experience

**Response Structure**:
```json
{
  "nour_response": "clinical assessment",
  "risk_score": "HIGH",
  "confidence": 0.85,
  "factors": [...],
  "glossary_context": [...]
}
```

---

### Fix 3: API Key Authentication (`INTERNAL_API_KEY`)

**Problem**: No service-to-service authentication between Seghir and your AI system.

**Solution**:
- Added `verify_internal_api_key()` dependency function
- All endpoints validate `x-internal-key` header
- Returns 401 Unauthorized if key missing/invalid
- Secure inter-service communication

**Implementation**:
```python
def verify_internal_api_key(x_internal_key: str = Header(None)) -> None:
    expected_key = os.getenv("INTERNAL_API_KEY")
    if expected_key and x_internal_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid key")
```

**Setup**:
```
INTERNAL_API_KEY=your_secure_key_here
```

---

## Medical Glossary (Darija)

### Update Completed: 20 Darija Terms Corrected

The glossary was updated from Modern Standard Arabic (MSA) to **conversational Moroccan Darija** for better patient comprehension.

#### Examples of Corrections

| Old (MSA) | New (Darija) | English |
|-----------|--------------|---------|
| شياط الدم | الضغط / ضغط الدم طالع | High blood pressure |
| قصور الكلى | الكلاوي راهي ما تخدمش مليح | Kidney failure |
| ضعف القلب | القلب ضعيف | Heart failure |
| السعال | كحة | Cough |
| ضيق التنفس | نخنق / ما نقدرش نتنفس مليح | Shortness of breath |
| حموضة المعدة | حريق المعدة | Acid reflux |
| الصداع | وجع الراس / راسي يوجعني | Headache |

### Total Glossary Stats

- **Total Entries**: 204 medical terms
- **Categories**: 13+ (endocrine, cardiovascular, respiratory, etc.)
- **Languages**: Darija + French + English
- **Coverage**: Chronic disease management, medications, vital signs, symptoms

### Glossary Access

**Endpoint**: `GET /ai/glossary`

```python
# Fetch all glossary terms
GET /ai/glossary?skip=0&limit=100

# Search specific term
POST /ai/glossary/match
{
  "query": "السكري",
  "language": "darija"
}
```

---

## Development Workflow

### Local Development Setup

1. **Clone Repository**
```bash
git clone https://github.com/yakouben/rag-biovatech.git
cd rag-biovatech
```

2. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
# - GEMINI_API_KEY
# - INTERNAL_API_KEY
```

5. **Run Development Server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### File Structure

```
rag-biovatech/
├── app/
│   ├── main.py                 # FastAPI app setup + route aliases
│   ├── config.py               # Configuration & settings
│   ├── routes/
│   │   └── api.py              # All API endpoints
│   ├── services/
│   │   ├── gemini_service.py   # LLM integration
│   │   ├── risk_service.py     # Risk scoring
│   │   ├── rag_service.py      # Knowledge retrieval
│   │   ├── drift_service.py    # Health change detection
│   │   ├── pdf_service.py      # Report generation
│   │   └── ...
│   ├── schemas.py              # Pydantic models
│   └── utils/
│       ├── exceptions.py       # Custom exceptions
│       └── logging.py          # Logging setup
├── scripts/
│   ├── export_maladies.py      # Export glossary to JSON
│   ├── update_darija_terms.py  # Update glossary in DB
│   └── ...
├── database_setup_clean.sql    # Database initialization
├── requirements.txt            # Python dependencies
└── README.md
```

### Common Development Tasks

#### Run Database Scripts
```bash
# Export glossary
python scripts/export_maladies.py

# Update Darija terms
python scripts/update_darija_terms.py
```

#### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# AI Chat
curl -X POST http://localhost:8000/ai/chat \
  -H "x-internal-key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test-123",
    "patient_symptoms": "وجع الراس",
    "patient_data": {},
    "include_glossary": true
  }'

# Get glossary
curl http://localhost:8000/ai/glossary
```

#### Debugging

Use `console.log("[v0] ...")` style logging in services:

```python
logger.info("[v0] Processing patient symptoms: %s", symptoms)
logger.debug("[v0] Risk assessment: %s", risk_data)
logger.error("[v0] Error in Gemini API: %s", str(error))
```

---

## Deployment & Environment

### Environment Variables

**Required**:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
INTERNAL_API_KEY=your_secure_internal_key
```

**Optional**:
```
LOG_LEVEL=INFO
ENVIRONMENT=production
GEMINI_MODEL=gemini-pro
```

### Vercel Deployment

1. **Connect GitHub Repository**
   - Push to `api-endpoint-review` branch
   - Vercel automatically deploys

2. **Set Environment Variables**
   - Go to Vercel Project Settings → Environment Variables
   - Add all variables from `.env`

3. **Deploy**
```bash
git push origin api-endpoint-review
# Vercel automatically builds and deploys
```

4. **Monitor Logs**
   - Vercel Dashboard → Deployments → View Logs
   - Or use Vercel CLI: `vercel logs`

### Production Checklist

- [ ] All environment variables set in Vercel
- [ ] INTERNAL_API_KEY configured and shared securely with Seghir team
- [ ] Database backups enabled in Supabase
- [ ] API rate limiting configured
- [ ] Error logging and monitoring active
- [ ] CORS configured for Seghir domain
- [ ] SSL/TLS certificate valid
- [ ] Health check endpoint monitored

---

## Troubleshooting

### Common Issues

#### 401 Unauthorized on `/ai/chat`
**Cause**: Missing or invalid `x-internal-key` header
**Solution**: 
```bash
# Verify key in request
curl -H "x-internal-key: your_actual_key" http://localhost:8000/ai/chat
```

#### Gemini API Errors
**Cause**: Invalid or expired GEMINI_API_KEY
**Solution**:
1. Check API key in Google Cloud Console
2. Verify quota limits
3. Restart application with new key

#### Database Connection Failures
**Cause**: Invalid Supabase credentials
**Solution**:
```python
# Test connection
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
result = supabase.table("users").select("count").execute()
print(result)  # Should return count without errors
```

#### Glossary Terms Not Updating
**Cause**: Medical glossary table locked or permission issues
**Solution**:
```bash
# Run update script
python scripts/update_darija_terms.py
# Check Supabase RLS policies
```

---

## Support & Contact

- **Team Lead**: [Your Name]
- **API Documentation**: `/docs` endpoint
- **Issue Tracking**: GitHub Issues
- **Emergency Contact**: [On-call Engineer]

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-28 | Initial release with contract compliance fixes |
| | | - Added `/ai/chat` endpoint |
| | | - Integrated risk scoring into chat response |
| | | - Added API key authentication |
| | | - Updated 20 Darija glossary terms |
| | | - Comprehensive documentation |

---

**Last Updated**: 2026-04-28  
**Document Version**: 1.0.0  
**Status**: Production Ready ✅
