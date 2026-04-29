# ChronicCare Patient App - Complete Developer Specification

**Status**: Production Ready ✅  
**API Base URL**: `https://web-production-fadce.up.railway.app/api/v1`  
**Version**: 1.0  
**Last Updated**: January 2024

---

## Quick Navigation

1. **Overview** (Section 1) - What you're building
2. **Technology Stack** (Section 2) - Tools & libraries
3. **Getting Started** (Section 3) - 5-step setup
4. **Design System** (Section 4) - Colors, fonts, components
5. **Database & API** (Section 5) - Complete endpoint reference
6. **TypeScript Types** (Section 6) - Copy-paste ready interfaces
7. **Component Architecture** (Section 7) - Page structure & components
8. **Implementation Timeline** (Section 8) - 6-phase roadmap
9. **Testing & Deployment** (Section 9) - Quality checklist

---

## 1. PROJECT OVERVIEW

### Vision
Build an intuitive, patient-facing diabetes management application that allows patients to track daily health metrics, receive AI-powered health insights, and maintain secure communication with their healthcare providers.

### Core Features

**1.1 User Authentication & Patient Profile**
- Secure login/registration (JWT tokens)
- Patient profile management (name, email, phone, medical history)
- Password reset & account settings
- Family member access control

**1.2 Daily Vitals Tracking**
- Blood pressure (systolic/diastolic)
- Blood glucose levels (fasting/random/postprandial)
- Body weight
- Heart rate
- Symptom logging (fatigue, blurred vision, neuropathy)
- Medication adherence tracking

**1.3 Health Data Visualization**
- 30-day health trends (line charts)
- Risk score gauge
- Clinical drift detection
- Comparative analysis (week-over-week, month-over-month)
- PDF report generation

**1.4 AI-Powered Insights**
- NOUR: Extended clinical reasoning
- Hela AI: Conversational health assistant
- Automated risk assessment
- Clinical glossary search (Darija/French/English)

**1.5 Communication Hub**
- Doctor messages & notifications
- Report sharing with healthcare team
- Appointment scheduling
- Medical glossary access

---

## 2. TECHNOLOGY STACK

### Frontend
```
Framework:        Next.js 16 (React 19.2)
Language:         TypeScript 5+
Styling:          Tailwind CSS 3+
Data Fetching:    SWR (stale-while-revalidate)
Form Handling:    React Hook Form
Validation:       Zod
Charts:           Recharts 2.10+
UI Components:    Headless UI + custom components
Icons:            Lucide React (optional)
Authentication:   JWT (localStorage + context)
HTTP Client:      Native fetch API
```

### Backend Integration
```
API Endpoint:     https://web-production-fadce.up.railway.app/api/v1
Protocol:         REST with JSON
Authentication:   Bearer Token (JWT)
CORS:             Enabled for production domain
Response Format:  Standard JSON with metadata
```

### Development Tools
```
Version Control:  Git & GitHub
Package Manager:  npm / yarn / pnpm
Environment:      Node.js 18+ LTS
Testing:          Jest + React Testing Library
Build:            Next.js built-in (Turbopack)
Deployment:       Vercel (recommended)
```

---

## 3. GETTING STARTED - 5-STEP SETUP

### Step 1: Create Next.js Project

```bash
npx create-next-app@latest patient-app --typescript --tailwind --eslint
cd patient-app
```

Select these options:
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- App Router: Yes
- Import alias: Yes (use `@/*`)

### Step 2: Install Dependencies

```bash
npm install \
  swr \
  react-hook-form \
  zod \
  @hookform/resolvers \
  recharts \
  lucide-react \
  date-fns \
  axios \
  js-cookie \
  jspdf \
  @react-pdf/renderer
```

### Step 3: Set Up Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=https://web-production-fadce.up.railway.app/api/v1
NEXT_PUBLIC_APP_NAME=ChronicCare
NEXT_PUBLIC_APP_URL=https://your-domain.com
```

### Step 4: Initialize Project Structure

```bash
mkdir -p src/{app,components,hooks,lib,types,services,context,utils,constants}
```

Directory structure:
```
src/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── register/
│   │   └── forgot-password/
│   ├── (dashboard)/
│   │   ├── dashboard/
│   │   ├── vitals/
│   │   ├── history/
│   │   ├── glossary/
│   │   ├── reports/
│   │   └── settings/
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── auth/
│   ├── dashboard/
│   ├── charts/
│   ├── forms/
│   ├── ui/
│   └── shared/
├── hooks/
│   ├── useAuth.ts
│   ├── useFetch.ts
│   └── useForm.ts
├── lib/
│   ├── api.ts
│   └── utils.ts
├── types/
│   └── index.ts
├── services/
│   ├── auth.ts
│   ├── patient.ts
│   ├── vitals.ts
│   └── ai.ts
├── context/
│   └── AuthContext.tsx
├── constants/
│   └── index.ts
└── utils/
    └── validation.ts
```

### Step 5: Configure Tailwind CSS

Update `tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0ea5e9',
        secondary: '#06b6d4',
        background: '#f8fafc',
        surface: '#ffffff',
        text: '#1e293b',
        border: '#e2e8f0',
      },
      fontFamily: {
        sans: ['var(--font-urbanist)'],
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
export default config
```

---

## 4. DESIGN SYSTEM

### Color Palette

```
Primary:      #0ea5e9 (Sky Blue)
Secondary:    #06b6d4 (Cyan)
Success:      #10b981 (Green)
Warning:      #f59e0b (Amber)
Danger:       #ef4444 (Red)
Background:   #f8fafc (Light Gray)
Surface:      #ffffff (White)
Text:         #1e293b (Dark Gray)
Border:       #e2e8f0 (Light Border)
```

### Typography

**Font Family**: Urbanist (Google Fonts)

```css
@import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@300;400;500;600;700;800&display=swap');
```

**Font Sizes**:
- H1: 32px (bold)
- H2: 24px (bold)
- H3: 20px (semibold)
- Body: 16px (regular)
- Small: 14px (regular)
- Caption: 12px (regular)

### Component Styles

**Glassmorphism Effect** (Primary):
```css
.glass {
  @apply bg-white/80 backdrop-blur-md border border-white/20 rounded-xl shadow-xl;
}
```

**Button Primary**:
```css
.btn-primary {
  @apply px-4 py-2 bg-sky-500 text-white rounded-lg font-semibold 
         hover:bg-sky-600 transition-colors disabled:opacity-50;
}
```

**Input Field**:
```css
.input-field {
  @apply w-full px-4 py-2 border border-gray-300 rounded-lg 
         focus:ring-2 focus:ring-sky-500 focus:border-transparent;
}
```

**Card**:
```css
.card {
  @apply p-6 bg-white rounded-xl shadow-sm border border-gray-100;
}
```

### Icon Usage
- Use Lucide React for consistent icons
- Icon size: 20px default, 24px for large, 16px for small
- Color: Match text color or use primary color for highlights

---

## 5. DATABASE & API REFERENCE

### Database Schema

**patients table**
```sql
CREATE TABLE patients (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  date_of_birth DATE,
  phone_number VARCHAR(20),
  address TEXT,
  city VARCHAR(100),
  country VARCHAR(100),
  medical_history TEXT,
  current_medications TEXT,
  allergies TEXT,
  blood_type VARCHAR(5),
  emergency_contact_name VARCHAR(255),
  emergency_contact_phone VARCHAR(20),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**patient_assessments table**
```sql
CREATE TABLE patient_assessments (
  id UUID PRIMARY KEY,
  patient_id UUID NOT NULL,
  assessment_date TIMESTAMP,
  blood_pressure_systolic INTEGER,
  blood_pressure_diastolic INTEGER,
  glucose_level FLOAT,
  weight FLOAT,
  heart_rate INTEGER,
  symptoms TEXT[],
  medication_adherence VARCHAR(50),
  risk_score FLOAT,
  clinical_drift_detected BOOLEAN,
  ai_analysis TEXT,
  created_at TIMESTAMP
);
```

### API Endpoints

**BASE URL**: `https://web-production-fadce.up.railway.app/api/v1`

#### Authentication

**POST /auth/login**
```json
Request:
{
  "email": "patient@example.com",
  "password": "securepassword"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "email": "patient@example.com",
    "name": "John Doe"
  }
}
```

**POST /auth/register**
```json
Request:
{
  "email": "patient@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}

Response: 201 Created
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { ... }
}
```

**POST /auth/refresh**
```json
Request:
{
  "refresh_token": "token"
}

Response: 200 OK
{
  "access_token": "new_token"
}
```

#### Patient Profile

**GET /patient/{patient_id}/profile**
```json
Response: 200 OK
{
  "id": "uuid",
  "user_id": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "phone_number": "+1234567890",
  "address": "123 Main St",
  "city": "New York",
  "country": "USA",
  "medical_history": "Type 2 Diabetes",
  "current_medications": ["Metformin 500mg"],
  "allergies": "Penicillin",
  "blood_type": "O+",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+0987654321"
}
```

**PUT /patient/{patient_id}/profile**
```json
Request:
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "address": "456 Oak Ave",
  "city": "Boston",
  "country": "USA"
}

Response: 200 OK
{
  "message": "Profile updated successfully",
  "patient": { ... }
}
```

#### Vitals & Chat (PRIMARY ENDPOINT)

**POST /chat**
```json
Request:
{
  "patient_id": "uuid",
  "message": "My glucose is 180 today and I feel dizzy",
  "vitals": {
    "blood_pressure_systolic": 140,
    "blood_pressure_diastolic": 90,
    "glucose_level": 180,
    "weight": 75,
    "heart_rate": 85
  },
  "symptoms": ["dizziness", "fatigue"]
}

Response: 200 OK
{
  "response": "Your glucose level is elevated...",
  "assessment": {
    "risk_level": "high",
    "risk_score": 0.75,
    "recommendations": ["Increase water intake", "Check medication"]
  },
  "vitals_saved": true
}
```

**GET /patient/{patient_id}/history?days=30**
```json
Response: 200 OK
{
  "total_records": 45,
  "records": [
    {
      "id": "uuid",
      "assessment_date": "2024-01-20T10:30:00Z",
      "blood_pressure_systolic": 130,
      "blood_pressure_diastolic": 85,
      "glucose_level": 145,
      "weight": 75.5,
      "heart_rate": 78,
      "symptoms": ["none"],
      "risk_score": 0.45
    }
  ]
}
```

#### AI Analysis

**POST /nour**
```json
Request:
{
  "patient_id": "uuid",
  "assessment_data": {
    "blood_pressure": "140/90",
    "glucose": 180,
    "weight": 75,
    "symptoms": "dizziness, fatigue"
  }
}

Response: 200 OK
{
  "clinical_reasoning": "Patient shows elevated BP and glucose...",
  "risk_factors": ["uncontrolled glucose", "elevated BP"],
  "recommendations": ["Consult with doctor", "Adjust medication"],
  "severity": "high"
}
```

**POST /risk-assessment**
```json
Request:
{
  "patient_id": "uuid"
}

Response: 200 OK
{
  "overall_risk_score": 0.65,
  "risk_components": {
    "glucose_control": 0.7,
    "blood_pressure": 0.6,
    "medication_adherence": 0.5,
    "symptom_presence": 0.8
  },
  "risk_level": "moderate",
  "alerts": []
}
```

**GET /patient/{patient_id}/check-drift**
```json
Response: 200 OK
{
  "drift_detected": false,
  "drift_type": null,
  "change_percentage": 5.2,
  "recommendation": "Continue current regimen"
}
```

#### Medical Glossary

**POST /glossary/search**
```json
Request:
{
  "term": "glucose",
  "language": "en"
}

Response: 200 OK
{
  "results": [
    {
      "term": "glucose",
      "definition": "A simple sugar that is...",
      "darija_term": "السكر",
      "example": "High glucose levels indicate..."
    }
  ]
}
```

#### Reports

**POST /reports/generate**
```json
Request:
{
  "patient_id": "uuid",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "format": "pdf"
}

Response: 200 OK
{
  "report_url": "https://..../report_12345.pdf",
  "report_id": "uuid",
  "generated_at": "2024-01-20T15:30:00Z"
}
```

---

## 6. TYPESCRIPT TYPES & INTERFACES

### Core Types

```typescript
// Authentication
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
}

// Patient Profile
export interface PatientProfile {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  phone_number: string;
  address: string;
  city: string;
  country: string;
  medical_history: string;
  current_medications: string[];
  allergies: string;
  blood_type: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  created_at: string;
  updated_at: string;
}

// Vitals & Assessment
export interface Vitals {
  blood_pressure_systolic: number;
  blood_pressure_diastolic: number;
  glucose_level: number;
  weight: number;
  heart_rate: number;
}

export interface PatientAssessment {
  id: string;
  patient_id: string;
  assessment_date: string;
  blood_pressure_systolic: number;
  blood_pressure_diastolic: number;
  glucose_level: number;
  weight: number;
  heart_rate: number;
  symptoms: string[];
  medication_adherence: string;
  risk_score: number;
  clinical_drift_detected: boolean;
  ai_analysis: string;
  created_at: string;
}

export interface ChatMessage {
  patient_id: string;
  message: string;
  vitals?: Vitals;
  symptoms: string[];
}

export interface ChatResponse {
  response: string;
  assessment: {
    risk_level: 'low' | 'moderate' | 'high';
    risk_score: number;
    recommendations: string[];
  };
  vitals_saved: boolean;
}

// AI Analysis
export interface RiskAssessment {
  overall_risk_score: number;
  risk_components: {
    glucose_control: number;
    blood_pressure: number;
    medication_adherence: number;
    symptom_presence: number;
  };
  risk_level: 'low' | 'moderate' | 'high';
  alerts: string[];
}

export interface NOURAnalysis {
  clinical_reasoning: string;
  risk_factors: string[];
  recommendations: string[];
  severity: 'low' | 'moderate' | 'high';
}

export interface ClinicalDrift {
  drift_detected: boolean;
  drift_type: string | null;
  change_percentage: number;
  recommendation: string;
}

// Glossary
export interface GlossaryTerm {
  term: string;
  definition: string;
  darija_term: string;
  example: string;
}

export interface GlossarySearchResult {
  results: GlossaryTerm[];
}

// Reports
export interface ReportGenerationRequest {
  patient_id: string;
  start_date: string;
  end_date: string;
  format: 'pdf' | 'json';
}

export interface GeneratedReport {
  report_url: string;
  report_id: string;
  generated_at: string;
}

// API Response
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Form Data
export interface VitalsFormData {
  blood_pressure_systolic: number;
  blood_pressure_diastolic: number;
  glucose_level: number;
  weight: number;
  heart_rate: number;
  symptoms: string[];
  medication_adherence: string;
  notes?: string;
}

export interface ProfileFormData {
  first_name: string;
  last_name: string;
  phone_number: string;
  address: string;
  city: string;
  country: string;
  medical_history?: string;
  current_medications?: string[];
  allergies?: string;
}
```

### Zod Validation Schemas

```typescript
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password must be 6+ characters'),
});

export const registerSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password must be 6+ characters'),
  first_name: z.string().min(2, 'Name is required'),
  last_name: z.string().min(2, 'Name is required'),
  phone_number: z.string().min(10, 'Valid phone required'),
});

export const vitalsSchema = z.object({
  blood_pressure_systolic: z.number().min(40).max(300),
  blood_pressure_diastolic: z.number().min(20).max(200),
  glucose_level: z.number().min(20).max(600),
  weight: z.number().min(10).max(300),
  heart_rate: z.number().min(30).max(200),
  symptoms: z.array(z.string()),
  medication_adherence: z.enum(['excellent', 'good', 'fair', 'poor']),
});

export const profileSchema = z.object({
  first_name: z.string().min(2),
  last_name: z.string().min(2),
  phone_number: z.string().min(10),
  address: z.string().optional(),
  city: z.string().optional(),
  country: z.string().optional(),
});
```

---

## 7. COMPONENT ARCHITECTURE

### Page Structure

```
app/
├── (auth)/
│   ├── login/page.tsx
│   ├── register/page.tsx
│   └── forgot-password/page.tsx
│
├── (dashboard)/
│   ├── dashboard/page.tsx        # Main dashboard with overview
│   ├── vitals/page.tsx           # Input vitals form
│   ├── history/page.tsx          # View health history
│   ├── glossary/page.tsx         # Search medical terms
│   ├── reports/page.tsx          # Download/view reports
│   └── settings/page.tsx         # User settings
│
└── layout.tsx
```

### Component Hierarchy

**Dashboard Components**:
```
Dashboard/
├── VitalsCard
│   ├── GlucoseGauge
│   ├── BloodPressureDisplay
│   └── WeightChart
├── RiskScoreCard
│   ├── RiskGauge
│   └── RiskTrend
├── AIInsights
│   ├── CHATResponse
│   └── Recommendations
├── RecentActivity
└── QuickActions
```

**Form Components**:
```
Forms/
├── VitalsForm
│   ├── BloodPressureInput
│   ├── GlucoseInput
│   ├── WeightInput
│   ├── HeartRateInput
│   └── SymptomCheckbox
├── ProfileForm
├── LoginForm
└── RegisterForm
```

**Chart Components**:
```
Charts/
├── GlucoseTrendChart
├── BloodPressureTrendChart
├── WeightTrendChart
├── RiskScoreTrend
└── ComparisonChart
```

**Shared Components**:
```
Shared/
├── Navbar
├── Sidebar
├── Navigation
├── LoadingSpinner
├── ErrorBoundary
├── Modal
├── Card
├── Button
└── Badge
```

### Example Component Code

**VitalsCard.tsx**:
```typescript
import React from 'react';
import { Vitals } from '@/types';

interface VitalsCardProps {
  vitals: Vitals;
  isLoading?: boolean;
}

export function VitalsCard({ vitals, isLoading }: VitalsCardProps) {
  if (isLoading) {
    return <div className="p-6 bg-white rounded-xl shadow-sm animate-pulse h-48" />;
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Vitals</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="glass p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Glucose</p>
          <p className="text-2xl font-bold text-sky-600">{vitals.glucose_level}</p>
          <p className="text-xs text-gray-500">mg/dL</p>
        </div>

        <div className="glass p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Blood Pressure</p>
          <p className="text-2xl font-bold text-sky-600">
            {vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic}
          </p>
          <p className="text-xs text-gray-500">mmHg</p>
        </div>

        <div className="glass p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Weight</p>
          <p className="text-2xl font-bold text-sky-600">{vitals.weight}</p>
          <p className="text-xs text-gray-500">kg</p>
        </div>

        <div className="glass p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Heart Rate</p>
          <p className="text-2xl font-bold text-sky-600">{vitals.heart_rate}</p>
          <p className="text-xs text-gray-500">bpm</p>
        </div>
      </div>
    </div>
  );
}
```

---

## 8. IMPLEMENTATION TIMELINE - 6 PHASES

### Phase 1: Project Setup & Authentication (Week 1)

**Objectives**:
- Initialize Next.js project with TypeScript
- Set up folder structure and design system
- Implement authentication (login, register, JWT)
- Create AuthContext for state management

**Deliverables**:
- ✓ Next.js 16 project with all dependencies installed
- ✓ TypeScript types and validation schemas
- ✓ AuthContext provider
- ✓ Login/Register pages with form validation
- ✓ JWT token management (storage, refresh)
- ✓ Protected routes middleware

**Tasks**:
1. Create Next.js project with TypeScript
2. Install all dependencies
3. Set up folder structure
4. Create Tailwind config with design tokens
5. Build AuthContext with useAuth hook
6. Implement login page with form validation
7. Implement register page
8. Add JWT token management
9. Create protected route wrapper

---

### Phase 2: Dashboard Core & Navigation (Week 2)

**Objectives**:
- Build main dashboard layout
- Create navigation (navbar + sidebar)
- Display patient profile summary
- Add responsive mobile design

**Deliverables**:
- ✓ Dashboard page with overview
- ✓ Navigation components (navbar, sidebar)
- ✓ Profile summary card
- ✓ Quick action buttons
- ✓ Mobile-responsive layout
- ✓ Loading states and error handling

**Tasks**:
1. Create layout.tsx with navigation
2. Build Navbar component
3. Build Sidebar component
4. Create Dashboard page structure
5. Add profile summary section
6. Implement quick action buttons
7. Add responsive design for mobile
8. Create loading skeleton components

---

### Phase 3: Vitals Tracking & AI Chat (Week 2-3)

**Objectives**:
- Build vitals input form with validation
- Integrate with /chat API endpoint
- Display AI analysis & recommendations
- Log symptoms and medication adherence

**Deliverables**:
- ✓ VitalsForm component with validation
- ✓ SymptomInput component
- ✓ Real-time form validation
- ✓ API integration with /chat endpoint
- ✓ AI response display
- ✓ Loading and error states
- ✓ Success confirmation

**Tasks**:
1. Create VitalsForm component
2. Implement Zod validation schema
3. Add BloodPressureInput, GlucoseInput, etc.
4. Build SymptomCheckbox component
5. Integrate with /chat API
6. Display AI analysis response
7. Show recommendations
8. Add form submission error handling
9. Create success toast notification

---

### Phase 4: Data Visualization & Trends (Week 3)

**Objectives**:
- Integrate Recharts for time-series graphs
- Display 30-day health trends
- Show risk score gauge
- Add comparative analysis

**Deliverables**:
- ✓ GlucoseTrendChart component
- ✓ BloodPressureTrendChart component
- ✓ WeightTrendChart component
- ✓ RiskScoreGauge component
- ✓ History page with all trends
- ✓ Date range filtering
- ✓ Export to PDF

**Tasks**:
1. Integrate Recharts library
2. Create GlucoseTrendChart component
3. Create BloodPressureTrendChart
4. Create WeightTrendChart
5. Build RiskScoreGauge (circular progress)
6. Create History page layout
7. Implement date filtering
8. Add PDF export functionality

---

### Phase 5: Advanced Features (Week 4)

**Objectives**:
- Implement medical glossary search
- Add risk assessment display
- Create clinical drift alerts
- Add report generation
- Profile settings management

**Deliverables**:
- ✓ Glossary search page
- ✓ Risk assessment card
- ✓ Clinical drift alerts
- ✓ PDF report generation
- ✓ Settings page
- ✓ Profile update form

**Tasks**:
1. Build GlossarySearch component
2. Integrate /glossary/search API
3. Display glossary results (Darija/English)
4. Create RiskAssessment component
5. Integrate /risk-assessment endpoint
6. Add ClinicalDrift alert component
7. Integrate /check-drift endpoint
8. Build report generation UI
9. Integrate /reports/generate endpoint
10. Create Settings page with profile update form
11. Implement profile edit functionality

---

### Phase 6: Testing, Optimization & Deployment (Week 4-5)

**Objectives**:
- Write unit and integration tests
- Optimize performance
- Audit accessibility (WCAG 2.1 AA)
- Deploy to production
- Monitor and handle errors

**Deliverables**:
- ✓ Unit tests for components (Jest)
- ✓ Integration tests for API calls
- ✓ E2E tests for critical flows
- ✓ Performance optimization (Lighthouse >90)
- ✓ Accessibility audit pass
- ✓ Error monitoring setup
- ✓ Production deployment

**Tasks**:
1. Set up Jest and React Testing Library
2. Write tests for authentication flows
3. Test API integration (SWR mocking)
4. Test component rendering
5. Test form validation
6. Optimize images and assets
7. Minify and lazy load components
8. Run Lighthouse audit
9. Fix accessibility issues
10. Set up Sentry for error tracking
11. Deploy to Vercel
12. Set up CI/CD pipeline
13. Monitor production metrics

---

## 9. TESTING & DEPLOYMENT CHECKLIST

### Before Deployment Checklist

**Code Quality**
- [ ] All TypeScript errors fixed (no `any` types)
- [ ] ESLint rules pass
- [ ] No console.log statements left
- [ ] Code follows naming conventions
- [ ] No unused imports/variables

**Testing**
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] E2E tests pass for critical flows
- [ ] Manual testing on desktop & mobile
- [ ] Test on Chrome, Firefox, Safari, Edge

**Performance**
- [ ] Lighthouse score >90
- [ ] Time to First Contentful Paint <2s
- [ ] Cumulative Layout Shift <0.1
- [ ] Images optimized (WebP format)
- [ ] Bundle size analyzed

**Security**
- [ ] JWT tokens properly stored
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Input validation on all forms
- [ ] No sensitive data in logs

**Accessibility**
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation works
- [ ] Screen reader tested
- [ ] Color contrast ratio >4.5:1
- [ ] Form labels associated

**Documentation**
- [ ] README.md complete
- [ ] API integration documented
- [ ] Component props documented
- [ ] Environment variables documented
- [ ] Deployment instructions clear

**Browser Compatibility**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

### Deployment Steps

**1. Set Up Vercel Project**
```bash
npm install -g vercel
vercel login
vercel link
```

**2. Configure Environment Variables**
```
NEXT_PUBLIC_API_BASE_URL=https://web-production-fadce.up.railway.app/api/v1
NEXT_PUBLIC_APP_NAME=ChronicCare
```

**3. Build & Test**
```bash
npm run build
npm run start
```

**4. Deploy**
```bash
vercel deploy --prod
```

**5. Post-Deployment**
- [ ] Verify all API endpoints working
- [ ] Test authentication flow
- [ ] Check email notifications
- [ ] Monitor error logs
- [ ] Verify HTTPS certificate
- [ ] Test on production domain

---

## 10. QUICK API INTEGRATION EXAMPLES

### Using SWR for Data Fetching

```typescript
// hooks/useFetch.ts
import useSWR from 'swr';

const fetcher = async (url: string) => {
  const token = localStorage.getItem('authToken');
  const res = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  if (!res.ok) throw new Error('API request failed');
  return res.json();
};

export function usePatientProfile(patientId: string) {
  const { data, error, isLoading } = useSWR(
    patientId ? `/api/v1/patient/${patientId}/profile` : null,
    fetcher
  );

  return { profile: data, error, isLoading };
}
```

### API Client Service

```typescript
// services/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('authToken');
  const url = `${API_BASE_URL}${endpoint}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.message);
  }

  return res.json();
}

// Usage
export const patientService = {
  getProfile: (id: string) =>
    apiCall<PatientProfile>(`/patient/${id}/profile`),
  
  updateProfile: (id: string, data: Partial<PatientProfile>) =>
    apiCall<PatientProfile>(`/patient/${id}/profile`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  getHistory: (id: string, days: number = 30) =>
    apiCall(`/patient/${id}/history?days=${days}`),

  sendChat: (message: ChatMessage) =>
    apiCall<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(message),
    }),
};
```

### Form Integration with Validation

```typescript
// components/forms/VitalsForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { vitalsSchema, VitalsFormData } from '@/types';

export function VitalsForm({ onSubmit }: { onSubmit: (data: VitalsFormData) => Promise<void> }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<VitalsFormData>({
    resolver: zodResolver(vitalsSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">Blood Glucose (mg/dL)</label>
        <input
          type="number"
          {...register('glucose_level', { valueAsNumber: true })}
          className="input-field"
        />
        {errors.glucose_level && (
          <span className="text-red-500 text-sm">{errors.glucose_level.message}</span>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="btn-primary w-full"
      >
        {isSubmitting ? 'Submitting...' : 'Submit Vitals'}
      </button>
    </form>
  );
}
```

---

## 11. TROUBLESHOOTING GUIDE

### Common Issues

**Issue**: 401 Unauthorized on API calls
**Solution**: 
- Check JWT token is stored in localStorage
- Verify Authorization header format: `Bearer {token}`
- Check token expiration time
- Implement token refresh logic

**Issue**: CORS errors
**Solution**:
- Verify production domain is whitelisted
- Check Origin header matches backend expectations
- Ensure credentials flag is set if needed

**Issue**: Chart not rendering
**Solution**:
- Ensure data array is not empty
- Check data format matches Recharts expectations
- Verify ResponsiveContainer has parent with defined height

**Issue**: Form validation not working
**Solution**:
- Check Zod schema matches form structure
- Verify zodResolver is properly imported
- Check form field names match schema

**Issue**: Mobile layout broken
**Solution**:
- Check responsive classes are applied
- Test with actual mobile device (not just browser dev tools)
- Verify viewport meta tag in layout
- Check Tailwind breakpoints (sm: 640px, md: 768px, lg: 1024px)

---

## 12. SUCCESS CRITERIA

By end of implementation, ensure:

✅ All 9 API endpoints integrated and tested
✅ Authentication flow fully functional (login > dashboard > logout)
✅ Dashboard displays real patient data
✅ Vitals form submits to API and returns AI analysis
✅ Charts render 30-day health trends
✅ Mobile responsive design (375px+ works perfectly)
✅ Accessibility audit passes (WCAG 2.1 AA)
✅ Performance metrics pass (Lighthouse >90)
✅ All error cases handled gracefully
✅ TypeScript strict mode passes
✅ Unit tests pass (>80% coverage)
✅ Deployed to production and tested

---

## 13. NEXT STEPS

1. **Week 1**: Clone the repository and follow Phase 1 setup
2. **Weekly**: Follow the 6-phase timeline
3. **Daily**: Reference API cheatsheet and TypeScript types
4. **Testing**: Run tests after each component
5. **Deployment**: Follow deployment checklist before going live

**Support Resources**:
- API Documentation: This file (Section 5)
- TypeScript Types: Section 6
- Component Examples: Section 7
- Troubleshooting: Section 11

---

**Generated**: January 2024
**Status**: Production Ready
**API URL**: https://web-production-fadce.up.railway.app/api/v1
**Questions?**: Reference relevant section in this document
