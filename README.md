# ChronicCare AI - YAKOUB's FastAPI Brain Service

Production-grade FastAPI service for chronic disease management in Algeria using AI-powered clinical reasoning.

## 🏥 Overview

ChronicCare AI is YAKOUB's intelligent backend service that:
- **Semantic Search** over 150+ proprietary Darija medical terms using pgvector
- **NOUR Clinical Reasoning** engine combining patient data with medical knowledge
- **Decision Tree Risk Scoring** calibrated for Algerian population demographics
- **Model Drift Detection** for continuous quality assurance
- **PDF Clinical Reports** generation for healthcare providers
- **Gemini Integration** for embeddings and AI reasoning

## 🏗️ Architecture

### Project Structure
```
app/
├── config.py              # Configuration management
├── main.py               # FastAPI application setup
├── schemas.py            # Pydantic models for validation
├── database/
│   └── connection.py     # Supabase connection manager
├── services/
│   ├── gemini_service.py      # Gemini API integration
│   ├── rag_service.py         # RAG (semantic search)
│   ├── risk_service.py        # Decision tree & risk scoring
│   ├── drift_service.py       # Model drift detection
│   └── pdf_service.py         # PDF report generation
├── routes/
│   └── api.py            # API endpoints
└── utils/
    ├── exceptions.py     # Custom exceptions
    └── logging.py        # Structured logging
```

### Core Services

#### 1. **Gemini Service**
- Text embeddings using Gemini 1.5 Flash
- NOUR clinical reasoning generation
- Batch embedding for efficiency

#### 2. **RAG Service**
- Vector similarity search over glossary
- Semantic term matching
- Fallback keyword search
- Context-aware retrieval

#### 3. **Risk Service**
- Decision tree classification (3 risk levels)
- Algerian-calibrated synthetic training data
- Weighted risk scoring
- Dynamic recommendations

#### 4. **Drift Detection Service**
- Monitors prediction accuracy
- Detects model performance degradation
- Triggers retraining recommendations
- Tracks metrics by risk category

#### 5. **PDF Service**
- Professional clinical report generation
- Color-coded risk indicators
- Vital signs presentation
- Recommendation formatting

## 🔌 API Endpoints

### Health & System
```
GET  /api/v1/health
```
Check service health and dependencies

### Embeddings
```
POST /api/v1/embed
```
Generate text embeddings

### Glossary
```
POST /api/v1/glossary/search    # Semantic search
GET  /api/v1/glossary            # Get all entries (paginated)
```

### Risk Assessment
```
POST /api/v1/risk-assessment
```
Assess chronic disease risk using decision tree

### NOUR Clinical Reasoning
```
POST /api/v1/nour
```
Generate clinical reasoning with risk assessment and glossary context

### Model Monitoring
```
POST /api/v1/predictions/record  # Record prediction
GET  /api/v1/drift-detection     # Detect drift
```

### Reports
```
POST /api/v1/reports/generate
```
Generate PDF clinical report

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Supabase project with pgvector enabled
- Google Generative AI API key

### Installation

1. **Clone and setup environment**
```bash
cd chronicare-ai
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
# - GEMINI_API_KEY
```

4. **Initialize database** (if needed)
```bash
# Run migrations in Supabase console or via SQL editor
# 1. Execute migrations/01_init_glossary.sql
# 2. Run migrations/02_seed_glossary.py to populate glossary
```

### Running the Service

**Development**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access documentation at `http://localhost:8000/docs`

## 📊 Medical Glossary

The service includes 150+ proprietary Darija medical terms covering:
- **Endocrine** - Diabetes, thyroid conditions
- **Cardiovascular** - Heart disease, hypertension
- **Respiratory** - Lung conditions, asthma
- **Renal** - Kidney disease, dialysis
- **Gastrointestinal** - Digestive disorders
- **Neurological** - Stroke, neuropathy
- **Rheumatological** - Arthritis, bone health
- **Medications** - Drug names and interactions
- **Vital Signs** - BP, glucose, heart rate
- **Symptoms** - Pain, fever, fatigue
- **Lab Tests** - Blood work, glucose monitoring
- **Lifestyle** - Diet, exercise, smoking

Each entry includes:
- Darija term (proprietary competitive advantage)
- French translation
- English translation
- Medical category
- Embedding vector

## 🔍 Example Usage

### Risk Assessment
```bash
curl -X POST http://localhost:8000/api/v1/risk-assessment \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### NOUR Clinical Reasoning
```bash
curl -X POST http://localhost:8000/api/v1/nour \
  -H "Content-Type: application/json" \
  -d '{
    "patient_symptoms": "Severe fatigue, frequent urination, blurred vision",
    "patient_data": {...},
    "include_glossary": true
  }'
```

### Glossary Search
```bash
curl -X POST http://localhost:8000/api/v1/glossary/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "chest pain and difficulty breathing",
    "limit": 10
  }'
```

## 🛡️ Error Handling

All errors follow a consistent format:
```json
{
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "field": "age",
    "reason": "must be positive"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 📈 Risk Scoring

**Low Risk** (Score 0-3)
- Annual health screening
- Continue current lifestyle
- Regular exercise

**Moderate Risk** (Score 3-6)
- Semi-annual review
- Optimize blood pressure
- Quarterly monitoring

**High Risk** (Score 6-10)
- Urgent clinical evaluation
- Monthly monitoring
- Specialist referral
- Intensive intervention

## 🔄 Model Drift Detection

The service monitors:
- **Accuracy** - Overall prediction accuracy
- **Category Performance** - Per-risk-level metrics
- **Confidence Scores** - Model certainty degradation
- **Threshold** - Default 5% accuracy drop triggers alert

## 📋 Logging

Structured JSON logging with:
- Timestamps
- Log levels
- Function/module context
- Error details
- Custom attributes

View logs in real-time via stdout

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📝 Configuration

Set environment variables:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `SUPABASE_DB_USER` - Database user
- `SUPABASE_DB_PASSWORD` - Database password
- `SUPABASE_DB_HOST` - Database host
- `SUPABASE_DB_NAME` - Database name
- `GEMINI_API_KEY` - Google Generative AI key
- `GEMINI_MODEL` - Model (default: gemini-1.5-flash)
- `DEBUG` - Debug mode (true/false)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## 🔐 Security

- Input validation via Pydantic
- Custom exception handling
- Structured error responses
- CORS middleware configured
- SQL injection prevention
- Type hints throughout

## 📦 Dependencies

- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Supabase** - Database client
- **google-generativeai** - Gemini integration
- **scikit-learn** - Decision tree modeling
- **reportlab** - PDF generation
- **uvicorn** - ASGI server

## 🚦 Performance

- Async/await throughout
- Connection pooling
- Model caching
- Batch embedding support
- Vector index optimization
- Efficient pagination

## 🔧 Maintenance

### Retraining the Decision Tree
```python
from app.services.risk_service import RiskScoringService
service = RiskScoringService()
service._train_model()  # Trains on synthetic data
```

### Seeding New Glossary Terms
Update `data/darija_medical_glossary.py` and run:
```bash
python migrations/02_seed_glossary.py
```

### Checking Model Metrics
```bash
curl http://localhost:8000/api/v1/drift-detection
```

## 📞 Support

For issues or questions:
1. Check logs: `app/` startup messages
2. Review API docs: `http://localhost:8000/docs`
3. Check configuration: `.env` file
4. Verify Supabase connection

## 📄 License

Proprietary - ChronicCare AI

## 🎯 Future Enhancements

- [ ] Multi-language support expansion
- [ ] Integration with wearable devices
- [ ] Advanced time-series analysis
- [ ] Telehealth provider portal
- [ ] Patient mobile app integration
- [ ] Real-time alert system
- [ ] Advanced drift detection with retraining
- [ ] Explainable AI (SHAP) integration
