# ChronicCare Patient Mobile App - Comprehensive Developer Specification

**Production API Base URL**: `https://web-production-fadce.up.railway.app/api/v1`

---

## 1. EXECUTIVE SUMMARY & VISION

The **ChronicCare Patient Mobile App** empowers patients with chronic diseases (diabetes, hypertension) to track their daily health metrics, understand their clinical status through AI-powered analysis, and communicate securely with their healthcare providers. The app is the **patient-facing companion** to the doctor dashboard, enabling seamless data flow and proactive health management.

### Core Patient Journeys:
1. **Patient Registration & Onboarding**: Create account → Complete health profile → Input initial vitals
2. **Daily Health Tracking**: Log glucose, BP, symptoms → Receive AI analysis → View risk status
3. **AI-Powered Insights**: NOUR clinical reasoning → Darija glossary support → Personalized recommendations
4. **Doctor Communication**: View doctor's assessment → Receive alerts → Message history
5. **Health Reports**: Generate PDF reports → Track trends → Monitor adherence

---

## 2. TECHNOLOGY STACK

### Frontend:
- **Framework**: Next.js 16 (React 19.2)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Custom CSS (Glassmorphism)
- **UI Components**: shadcn/ui + Custom components
- **Data Fetching**: SWR (stale-while-revalidate)
- **Forms**: React Hook Form + Zod validation
- **Charts**: Recharts (time-series graphs)
- **Typography**: Urbanist font (Google Fonts)
- **State Management**: React Context + SWR
- **Auth**: JWT tokens (localStorage + httpOnly cookies where possible)

### Backend Integration:
- **Python FastAPI** (at `https://web-production-fadce.up.railway.app`)
- **Database**: PostgreSQL with Supabase
- **AI Models**: Google Gemini 1.5 Flash
- **Vector DB**: pgvector for medical glossary

### Design System:
- **Primary Color**: Sky Blue (#0ea5e9)
- **Secondary Colors**: Gray (#f1f5f9), White (#ffffff), Dark (#0f172a)
- **Effects**: Glassmorphism (backdrop-blur, semi-transparent backgrounds)
- **Font**: Urbanist (headings & body)
- **Responsive**: Mobile-first design (375px → 1920px)

---

## 3. DATABASE SCHEMA & DATA STRUCTURES

### Patient Data Model
```typescript
interface PatientProfile {
  id: string;              // Unique identifier (UUID)
  name: string;            // Full name
  age: number;             // Years
  gender: string;          // M/F/Other
  phone: string;           // Contact number
  address: string;         // Physical address
  date_of_birth: string;   // ISO date (YYYY-MM-DD)
  family_contact_name: string;    // Emergency contact name
  family_contact_phone: string;   // Emergency contact phone
  family_access_granted: boolean; // Can family view data?
  previous_clinic_id?: string;    // Migration source
  medical_history_summary?: string; // Brief history
  created_at: ISO8601;
  updated_at: ISO8601;
}
```

### Vitals & Health Metrics
```typescript
interface PatientVitals {
  id: string;
  patient_id: string;
  recorded_at: ISO8601;
  systolic_bp: number;        // mmHg (60-250)
  diastolic_bp: number;       // mmHg (30-150)
  fasting_glucose: number;    // mg/dL (40-500)
  bmi: number;                // kg/m² (10-60)
  weight?: number;            // kg
  height?: number;            // cm
  smoking: boolean;
  family_history: boolean;
  comorbidities: number;      // Count of conditions
  created_at: ISO8601;
}
```

### Clinical Assessment Record
```typescript
interface PatientAssessment {
  id: string;
  patient_id: string;
  assessment_date: ISO8601;
  symptoms: string;           // Patient-reported symptoms
  predicted_risk_level: 0|1|2; // 0=LOW, 1=MODERATE, 2=HIGH
  actual_risk_level?: 0|1|2;
  risk_score: number;         // 0-10 scale
  confidence: number;         // 0-1 (model confidence)
  is_correct?: boolean;
  glossary_terms_used: string[]; // Darija terms referenced
  clinical_entities: {
    symptoms: string[];
    medications: string[];
    missed_medications: string[];
    vitals: Record<string, number>;
    severity_hints: string[];
    clinical_note: string;
  };
  created_at: ISO8601;
}
```

### Medical Glossary Entry
```typescript
interface GlossaryEntry {
  id: number;
  darija: string;       // Darija term (e.g., "السكري")
  french: string;       // French translation
  english: string;      // English translation
  category: string;     // e.g., "endocrine", "cardiovascular"
  embedding: number[];  // 768-dimensional vector
  created_at: ISO8601;
}
```

---

## 4. API ENDPOINTS & INTEGRATION

### Base URL: `https://web-production-fadce.up.railway.app/api/v1`

### 4.1 Authentication & Patient Profile

#### POST `/patients/onboard`
**Purpose**: Create/update patient profile + perform initial risk assessment  
**Auth**: Public (or JWT if already authenticated)  
**Request**:
```typescript
{
  "is_import": false,
  "profile": {
    "name": "Ahmed Ben Salah",
    "age": 52,
    "gender": "M",
    "phone": "+212612345678",
    "address": "123 Rue Mohamed V, Casablanca",
    "date_of_birth": "1971-06-15",
    "family_contact_name": "Fatima (Daughter)",
    "family_contact_phone": "+212699999999",
    "medical_history_summary": "Type 2 diabetes x5 years, hypertension"
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

**Response**:
```typescript
{
  "patient_id": "pat_abc123xyz",
  "status": "success",
  "message": "New patient onboarded successfully.",
  "initial_risk": {
    "risk_level": 1,
    "risk_score": 5.2,
    "category": "MODERATE",
    "probabilities": {
      "low": 0.2,
      "moderate": 0.65,
      "high": 0.15
    },
    "recommendations": [
      "Semi-annual clinical review",
      "Optimize blood pressure control"
    ],
    "monitoring_frequency": "Every 3-6 months"
  },
  "ai_analysis": "Patient shows moderate diabetes risk..."
}
```

#### GET `/patient/{patient_id}/profile`
**Purpose**: Fetch patient profile  
**Auth**: JWT (patient owns profile)  
**Response**: Full `PatientProfile` object

---

### 4.2 Daily Vitals & Health Tracking

#### POST `/chat` (AI Analysis Endpoint)
**Purpose**: Submit symptoms/vitals + get instant AI clinical assessment  
**Auth**: JWT  
**Request**:
```typescript
{
  "patient_id": "pat_abc123xyz",
  "patient_symptoms": "شعرت بإرهاق شديد واحتياج متكرر للتبول",
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
```typescript
{
  "hela_response": "المريض يعاني من أعراض السكري...",
  "extracted_entities": {
    "symptoms": ["fatigue", "frequent urination"],
    "medications": [],
    "missed_medications": [],
    "vitals": {
      "systolic_bp": 145,
      "glucose": 180
    },
    "severity_hints": ["severe fatigue"],
    "clinical_note": "Patient reports severe fatigue and frequent urination"
  },
  "risk_score": "MODERATE",
  "confidence": 0.72,
  "factors": ["Elevated glucose", "Family history of diabetes"],
  "monitoring_frequency": "Every 2-4 weeks",
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

#### GET `/patient/{patient_id}/history`
**Purpose**: Fetch historical assessments for trend graphs  
**Auth**: JWT  
**Query Params**: `days` (1-90, default 30)  
**Response**:
```typescript
{
  "patient_id": "pat_abc123xyz",
  "count": 15,
  "history": [
    {
      "date": "2024-01-15T10:30:00Z",
      "risk": 5.2,
      "systolic": 145,
      "diastolic": 90,
      "glucose": 150,
      "summary": "Patient reports fatigue"
    }
    // ... more entries in chronological order
  ]
}
```

#### POST `/nour` (Extended Clinical Reasoning)
**Purpose**: Full NOUR clinical assessment + glossary context  
**Auth**: JWT  
**Request**: Same as `/chat` POST  
**Response**:
```typescript
{
  "clinical_assessment": "Patient shows classic symptoms of poorly controlled type 2 diabetes...",
  "risk_assessment": {
    "risk_level": 2,
    "risk_score": 7.5,
    "category": "HIGH",
    "probabilities": { "low": 0.1, "moderate": 0.25, "high": 0.65 },
    "recommendations": ["Urgent endocrinology consultation"],
    "monitoring_frequency": "Monthly or more frequently"
  },
  "recommendations": ["Check HbA1c urgently", "Review medications"],
  "extracted_entities": { /* ... */ },
  "glossary_context": [ /* ... */ ]
}
```

---

### 4.3 Medical Glossary & Education

#### POST `/glossary/search`
**Purpose**: Search medical terms in Darija/French/English  
**Auth**: Public  
**Request**:
```typescript
{
  "query": "chest pain and difficulty breathing",
  "limit": 10,
  "language": "french"
}
```

**Response**:
```typescript
[
  {
    "id": 42,
    "darija": "ألم صدري",
    "french": "Douleur thoracique",
    "english": "Chest pain",
    "category": "cardiovascular"
  },
  // ... more entries
]
```

#### GET `/glossary`
**Purpose**: Get complete medical glossary with pagination  
**Auth**: Public  
**Query Params**: `skip` (default 0), `limit` (1-500, default 100)  
**Response**: Array of `GlossaryEntry` objects

---

### 4.4 Risk Assessment & Monitoring

#### POST `/risk-assessment`
**Purpose**: Assess chronic disease risk based on vitals  
**Auth**: Public  
**Request**:
```typescript
{
  "patient_data": { /* PatientVitals */ },
  "patient_symptoms": "Fatigue, frequent urination"
}
```

**Response**: `RiskAssessmentResponse` (see schemas above)

#### GET `/patient/{patient_id}/check-drift`
**Purpose**: Check for adherence drops + get proactive nurture message  
**Auth**: JWT  
**Response**:
```typescript
{
  "patient_id": "pat_abc123xyz",
  "adherence_drop_detected": true,
  "adherence_score_previous": 0.92,
  "adherence_score_current": 0.65,
  "nurture_message": "We noticed a dip in your adherence this week...",
  "recommendations": [
    "Set medication reminders",
    "Check if medication is causing side effects"
  ]
}
```

---

### 4.5 Reports & Analytics

#### POST `/reports/generate`
**Purpose**: Generate PDF clinical report  
**Auth**: JWT  
**Query Params**:
- `patient_id`: Patient identifier
- `patient_name`: Patient full name
- `adherence_days`: 7-90 (default 30)

**Request Body**: `NOURRequest` (via form/body)  
**Response**: PDF file (binary stream)

#### GET `/health`
**Purpose**: Health check + service status  
**Auth**: Public  
**Response**:
```typescript
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

## 5. FRONTEND APPLICATION ARCHITECTURE

### 5.1 Project Structure
```
patient-app/
├── app/
│   ├── layout.tsx                 # Root layout + providers
│   ├── page.tsx                   # Landing page (redirect to app)
│   ├── auth/
│   │   ├── login/page.tsx         # Patient login
│   │   ├── register/page.tsx      # Patient registration
│   │   └── onboard/page.tsx       # Health profile setup
│   ├── dashboard/
│   │   ├── page.tsx               # Main dashboard
│   │   ├── vitals-input/page.tsx  # Input daily vitals
│   │   ├── history/page.tsx       # Trend graphs
│   │   └── reports/page.tsx       # View/download reports
│   ├── api/
│   │   └── auth/[...auth].ts      # Auth API routes (if needed)
│   └── (public)/
│       └── glossary/page.tsx      # Medical dictionary
├── components/
│   ├── common/
│   │   ├── Navigation.tsx
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Loading.tsx
│   ├── dashboard/
│   │   ├── VitalsCard.tsx         # Display vitals
│   │   ├── RiskGauge.tsx          # Risk level visualization
│   │   ├── HealthTrend.tsx        # Time-series charts
│   │   └── AIInsights.tsx         # NOUR response display
│   ├── forms/
│   │   ├── VitalsForm.tsx         # Input vitals
│   │   ├── SymptomForm.tsx        # Log symptoms
│   │   └── ProfileForm.tsx        # Edit profile
│   ├── charts/
│   │   ├── GlucoseTrendChart.tsx
│   │   ├── BPTrendChart.tsx
│   │   └── AdherenceChart.tsx
│   └── glossary/
│       ├── GlossarySearch.tsx
│       └── GlossaryModal.tsx
├── hooks/
│   ├── useAuth.ts                 # Auth context
│   ├── usePatient.ts              # Patient data SWR
│   ├── useVitals.ts               # Vitals SWR
│   └── useAIChat.ts               # AI chat SWR
├── lib/
│   ├── api-client.ts              # Axios/fetch wrapper
│   ├── api-endpoints.ts           # Endpoint constants
│   ├── auth.ts                    # JWT utilities
│   ├── validators.ts              # Zod schemas
│   └── utils.ts                   # Helper functions
├── contexts/
│   ├── AuthContext.tsx
│   ├── PatientContext.tsx
│   └── ThemeContext.tsx
├── types/
│   ├── patient.ts                 # Patient interfaces
│   ├── vitals.ts                  # Vitals interfaces
│   ├── api.ts                     # API response types
│   └── common.ts                  # Shared types
├── styles/
│   ├── globals.css                # Tailwind + globals
│   └── glassmorphism.css          # Glass effect styles
├── public/
│   ├── icons/
│   ├── images/
│   └── fonts/                     # Urbanist font files
├── .env.local                     # Local env vars
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

---

### 5.2 Key Components

#### Dashboard Page (`/dashboard`)
- **Header**: Patient name, date, last update
- **Risk Gauge**: Circular progress showing risk level (LOW/MODERATE/HIGH)
- **Vitals Overview Cards**: BP, Glucose, BMI (latest + sparkline trend)
- **AI Insights Card**: Latest NOUR assessment summary
- **Action Buttons**: "Log Vitals", "Message Doctor", "View Reports"
- **Health Trends**: 30-day graph (glucose, BP, risk score)

#### Vitals Input Form (`/dashboard/vitals-input`)
- **Vitals Fields**:
  - Systolic BP (90-200 mmHg)
  - Diastolic BP (60-130 mmHg)
  - Fasting Glucose (40-400 mg/dL)
  - Weight (optional, kg)
  - BMI (auto-calculated)
  
- **Symptom Text Area**: Free-form symptom description (Arabic/French/English)
- **Real-time Validation**: Inline error messages
- **AI Chat**: "Ask NOUR" button → Opens modal with AI response
- **Submit Button**: POST to `/chat` endpoint

#### Health History Charts (`/dashboard/history`)
- **Time-Series Graph 1**: Glucose levels (30-day trend)
- **Time-Series Graph 2**: Blood Pressure (systolic/diastolic)
- **Time-Series Graph 3**: Risk score progression
- **Filter**: Date range selector (7/30/60/90 days)
- **Export Button**: Download as CSV

#### Reports Page (`/dashboard/reports`)
- **Report List**: Cards showing generated reports (date, type, status)
- **Generate Button**: Opens modal to configure report options
- **Download**: Fetch PDF from `/reports/generate` endpoint
- **Sharing**: Copy link to share report with family (if granted access)

#### Glossary Search (`/glossary`)
- **Search Bar**: Search terms in Darija/French/English
- **Results Grid**: Card layout with term, translation, category
- **Language Toggle**: Switch between Darija/French/English definitions
- **Category Filter**: Filter by medical category (endocrine, cardiovascular, etc.)

---

### 5.3 State Management & Data Flow

**Authentication State**:
```typescript
// AuthContext
{
  isAuthenticated: boolean;
  patient: PatientProfile | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (phone: string, password: string) => Promise<void>;
  logout: () => void;
  register: (profileData) => Promise<string>; // Returns patient_id
}
```

**Patient Data (SWR)**:
```typescript
// usePatient hook
const { patient, isLoading, isError, mutate } = usePatient(patientId);
// Auto-refetches every 30 seconds
```

**Vitals Data (SWR)**:
```typescript
// useVitals hook
const { vitals, history, isLoading, submit } = useVitals(patientId, days: 30);
// Auto-refetches on interval
```

**AI Chat State**:
```typescript
// useAIChat hook
const { response, isLoading, error, submit } = useAIChat();
// Call submit(symptoms, vitals) → POST /chat
```

---

## 6. DESIGN SPECIFICATIONS

### Color Palette
| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Primary | Sky Blue | #0ea5e9 | Buttons, links, highlights |
| Background | White | #ffffff | Main background |
| Surface | Light Gray | #f1f5f9 | Cards, containers |
| Border | Gray | #cbd5e1 | Dividers, outlines |
| Text Primary | Dark | #0f172a | Body text |
| Text Secondary | Gray | #64748b | Labels, hints |
| Success | Green | #10b981 | Status indicators |
| Warning | Amber | #f59e0b | Alerts |
| Danger | Red | #ef4444 | Errors |

### Typography
- **Font Family**: Urbanist (Google Fonts)
- **Headings**: Urbanist 700 (Bold)
- **Body**: Urbanist 400 (Regular)
- **Small Text**: Urbanist 300 (Light)

| Level | Font Size | Weight | Line Height |
|-------|-----------|--------|-------------|
| H1 | 32px | 700 | 1.2 |
| H2 | 24px | 700 | 1.3 |
| H3 | 20px | 700 | 1.4 |
| Body | 16px | 400 | 1.5 |
| Small | 14px | 400 | 1.4 |

### Glassmorphism Effect
```css
.glassmorphism {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
}

.glass-card {
  background: rgba(14, 165, 233, 0.1);  /* Sky blue tint */
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

### Responsive Breakpoints
- Mobile: 375px - 640px
- Tablet: 640px - 1024px
- Desktop: 1024px+

---

## 7. IMPLEMENTATION ROADMAP

### Phase 1: Project Setup & Auth (Week 1)
- [ ] Initialize Next.js 16 project with TypeScript
- [ ] Setup Tailwind CSS + Urbanist font import
- [ ] Create AuthContext + login/register flows
- [ ] Implement JWT token storage + refresh logic
- [ ] Create `/auth/login`, `/auth/register`, `/auth/onboard` pages
- [ ] API client wrapper with error handling

### Phase 2: Dashboard Core UI (Week 2)
- [ ] Create `/dashboard` page layout
- [ ] Build VitalsCard, RiskGauge, AIInsights components
- [ ] Implement Navigation, Header, Footer
- [ ] Setup SWR for patient data fetching
- [ ] Create theme provider (dark/light mode if needed)
- [ ] Mobile responsive design

### Phase 3: Vitals Tracking (Week 2-3)
- [ ] Build VitalsForm component with validation
- [ ] Create SymptomForm (textarea + AI chat button)
- [ ] Integrate POST `/chat` endpoint
- [ ] Display NOUR response in modal
- [ ] Save vitals to backend + UI update
- [ ] Real-time validation feedback

### Phase 4: Data Visualization (Week 3)
- [ ] Integrate Recharts library
- [ ] Create GlucoseTrendChart (line chart)
- [ ] Create BPTrendChart (dual-axis)
- [ ] Build AdherenceChart (bar chart)
- [ ] Implement date range filter
- [ ] Export data as CSV

### Phase 5: Advanced Features (Week 4)
- [ ] Glossary search page + modal
- [ ] Reports generation + PDF download
- [ ] Doctor message history (if available)
- [ ] Family access features
- [ ] Push notifications (if supported)
- [ ] Offline caching strategy

### Phase 6: Testing & Polish (Week 4-5)
- [ ] Unit tests for components
- [ ] E2E tests for critical flows (auth, vitals submission)
- [ ] Performance optimization (image optimization, code splitting)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Browser compatibility testing
- [ ] Production build & deployment

---

## 8. API ERROR HANDLING

All API responses follow this error contract:
```typescript
interface ErrorResponse {
  status_code: number;
  error_code: string;  // e.g., "VALIDATION_ERROR"
  message: string;
  details?: {
    [field: string]: string;
  };
  timestamp: string;
}
```

**Common Error Codes**:
- `VALIDATION_ERROR` (400): Invalid input data
- `UNAUTHORIZED` (401): Missing/invalid JWT
- `NOT_FOUND` (404): Resource doesn't exist
- `CONFLICT` (409): Resource already exists
- `INTERNAL_SERVER_ERROR` (500): Backend error

**Client-side Handler**:
```typescript
const handleAPIError = (error: any) => {
  if (error.response?.status === 401) {
    // Redirect to login
    router.push('/auth/login');
  } else if (error.response?.status === 400) {
    // Show validation errors
    showErrorToast(error.response.data.message);
  } else {
    // Generic error toast
    showErrorToast('Something went wrong. Please try again.');
  }
};
```

---

## 9. SECURITY & BEST PRACTICES

### JWT Token Management
- Store JWT in localStorage (frontend has no httpOnly option in browser)
- Send JWT in `Authorization: Bearer {token}` header
- Implement token refresh logic (if backend provides refresh endpoint)
- Clear token on logout

### Input Validation
- **Client-side**: Zod schemas for all form inputs
- **Server-side**: Already handled by FastAPI (Pydantic)
- Sanitize user input (especially medical text)

### CORS & API Security
- API CORS headers already set by backend
- Include `X-Requested-With: XMLHttpRequest` header (if needed)

### Data Privacy
- **No sensitive data in logs**: Filter out patient IDs, names, etc.
- **HIPAA Compliance**: Handle patient data securely (SSL/TLS everywhere)
- **Audit Trail**: Log all API calls server-side (backend responsibility)

---

## 10. TESTING CHECKLIST

### Unit Tests
- [ ] VitalsForm validation
- [ ] RiskGauge color logic
- [ ] Chart data transformation functions
- [ ] AuthContext login/logout flows

### Integration Tests
- [ ] Patient login → Dashboard load
- [ ] Vitals submission → AI chat → Risk update
- [ ] History chart data fetching
- [ ] Profile update workflow

### E2E Tests (Cypress/Playwright)
- [ ] Complete user signup flow
- [ ] Daily vitals tracking workflow
- [ ] Report generation & download
- [ ] Glossary search functionality

### Manual Testing
- [ ] Mobile responsiveness (iPhone SE, iPhone 14, Android)
- [ ] Different network speeds (4G, 3G, offline)
- [ ] Browser compatibility (Chrome, Safari, Firefox)
- [ ] Accessibility (screen reader, keyboard navigation)

---

## 11. DEPLOYMENT & MONITORING

### Environment Variables
```env
NEXT_PUBLIC_API_BASE_URL=https://web-production-fadce.up.railway.app/api/v1
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Build & Deployment
- `npm run build` → Static export or serverless deployment
- Deploy to Vercel (recommended) or AWS Amplify
- Setup monitoring (Sentry for error tracking)
- Configure CDN for assets

### Performance Targets
- Lighthouse Score: > 90
- Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
- API response time: < 500ms (p99)

---

## 12. IMPLEMENTATION NOTES

### For Frontend Developer
1. **API Integration**: All endpoints listed in Section 4 are production-ready
2. **Authentication**: Implement JWT-based auth (backend handles verification)
3. **State Management**: Use SWR for server state + React Context for UI state
4. **Error Handling**: Follow error contract in Section 8
5. **Accessibility**: Use semantic HTML + ARIA labels for glassmorphic components
6. **Performance**: Lazy-load charts, optimize images, implement virtual scrolling for history

### Dependencies to Install
```bash
npm install next@16 react@19 typescript tailwind next-font zod react-hook-form swr axios recharts
npm install -D @types/react @types/node @tailwindcss/typography
```

### Design System Components (Pre-built)
- Card (glassmorphic) → `components/ui/Card.tsx`
- Button (sky blue) → `components/ui/Button.tsx`
- Input (validated) → `components/ui/Input.tsx`
- Modal/Dialog → `components/ui/Dialog.tsx`
- Tabs → `components/ui/Tabs.tsx`
- Badge (risk level) → `components/ui/Badge.tsx`

---

## 13. SUPPORT & ESCALATION

**API Issues**: Check `/health` endpoint  
**Database Issues**: Verify Supabase connection status  
**AI Model Issues**: Check Gemini API quota + error logs  
**Frontend Bugs**: Replicate on production API (`https://web-production-fadce.up.railway.app`)

---

**Document Version**: 1.0  
**Last Updated**: January 2024  
**Status**: Ready for Development
