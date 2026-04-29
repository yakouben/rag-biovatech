# ChronicCare Dashboard - Developer Specification & Implementation Guide

## 🎯 Executive Vision
Build a **risk-aware, culturally-native clinical dashboard** for doctors managing chronic disease patients. This is not a data repository—it's an **Early Warning System** that brings intelligent triage, seamless patient handovers, and AI-powered insights into one elegant interface.

---

## 📋 Core Features (From Product Storytelling)

### 1. **Risk Queue (Smart Triage)**
- **What it does**: Displays patients sorted by AI-calculated risk scores (0-10 scale)
- **Why it matters**: Doctors see high-risk patients first, not in arbitrary calendar order
- **Visual**: Color-coded cards (Red=High Risk 8+, Yellow=Medium 5-7, Green=Low <5)

### 2. **Smart Onboarding (Add/Import Patients)**
- **Import History**: Seamlessly pull patient data from other clinics
- **Family Access**: Add family members as contacts for SMS/cultural care coordination
- **Clinical Summary Auto-Generation**: AI reads imported history and flags critical trends

### 3. **Clinical Drift Detection (Alerts)**
- **Medication Adherence Drop**: Detects when adherence falls below threshold
- **Vital Trending**: Identifies rising BP, glucose, weight patterns
- **Smart Notifications**: Sends culturally-warm SMS reminders in Darija

### 4. **Hela Doctor AI Chat**
- **RAG Search**: Deep search across patient's entire history + medical glossary
- **Clinical Reasoning**: Connects dots between old data and current symptoms
- **Instant Insights**: "How has BP responded to this medication over 6 months?"

### 5. **Automated Clinical Reports**
- **One-Click Generation**: PDF with imported history, risk scores, adherence graphs
- **Specialist Handovers**: Pre-formatted for sending to cardiologists, endocrinologists
- **Secure Sharing**: Email or print-ready format

---

## 🎨 Design & UX Requirements

### Typography
- **Font Family**: Urbanist (primary, all text)
- **Load from**: Google Fonts or Vercel Fonts

### Color Palette (Glassmorphism Theme)
```
Primary: Sky Blue (#0B8FEF or #1E90FF)
Secondary: Light Sky (#E0F2FE)
Success/Safe: Green (#10B981)
Warning: Amber (#F59E0B)
Critical/Risk: Red (#EF4444)
Neutral: Dark Gray (#1F2937)
Background: Near-White (#F8FAFC)
Glass Effect: Semi-transparent overlays (rgba with 15-20% opacity)
```

### UX Principles
- **No Vibecoding**: Avoid overly animated, gradient-heavy, or neon effects
- **Glassmorphic Cards**: Subtle frosted glass effect on modals and panels
- **Spacious Layout**: Clear breathing room between elements
- **Accessibility**: WCAG AA compliant, high contrast on critical elements

---

## 🏗️ Technical Architecture

### Frontend Stack
- **Framework**: Next.js 16 (App Router)
- **UI Components**: React 19 + custom Tailwind CSS
- **State Management**: SWR (for patient data caching)
- **Forms**: React Hook Form + Zod validation
- **Chat Interface**: Streaming UI for Hela AI responses
- **PDF Generation**: html2pdf or pdfkit (server-side)

### Backend Stack (Required)
- **Framework**: Next.js API Routes
- **Database**: PostgreSQL (Supabase or Neon recommended)
- **AI/RAG**: OpenAI Embeddings + Vector Search
- **File Storage**: Vercel Blob (for PDFs, patient attachments)
- **SMS Gateway**: Twilio or Vonage (for Darija notifications)

---

## 📊 Database Schema (Core Tables)

```sql
-- Users (Doctors, Clinic Staff)
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE,
  role ENUM('doctor', 'nurse', 'admin'),
  clinic_id UUID,
  created_at TIMESTAMP
);

-- Patients
CREATE TABLE patients (
  id UUID PRIMARY KEY,
  clinic_id UUID,
  first_name TEXT,
  last_name TEXT,
  phone TEXT,
  dob DATE,
  conditions TEXT[] (e.g., ['Diabetes', 'Hypertension']),
  risk_score FLOAT (0-10),
  risk_updated_at TIMESTAMP,
  created_at TIMESTAMP,
  FOREIGN KEY (clinic_id) REFERENCES clinics(id)
);

-- Vitals (Latest readings)
CREATE TABLE vitals (
  id UUID PRIMARY KEY,
  patient_id UUID,
  recorded_at TIMESTAMP,
  systolic INT,
  diastolic INT,
  glucose INT,
  weight FLOAT,
  heart_rate INT,
  notes TEXT,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Patient History (Imported from other clinics)
CREATE TABLE patient_history (
  id UUID PRIMARY KEY,
  patient_id UUID,
  source_clinic_id TEXT,
  imported_from_clinic_name TEXT,
  imported_at TIMESTAMP,
  data JSONB (stores full history)
);

-- Medication Adherence
CREATE TABLE adherence_logs (
  id UUID PRIMARY KEY,
  patient_id UUID,
  medication_name TEXT,
  scheduled_date DATE,
  taken BOOLEAN,
  logged_at TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Family Contacts
CREATE TABLE family_contacts (
  id UUID PRIMARY KEY,
  patient_id UUID,
  contact_name TEXT,
  phone TEXT,
  relationship TEXT (e.g., 'Son', 'Daughter', 'Spouse'),
  language ENUM('darija', 'french', 'english'),
  consent_sms BOOLEAN,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Clinical Notes & Chat History
CREATE TABLE clinical_notes (
  id UUID PRIMARY KEY,
  patient_id UUID,
  user_id UUID,
  content TEXT,
  ai_generated BOOLEAN,
  created_at TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Alert Rules (Drift Detection Config)
CREATE TABLE alert_rules (
  id UUID PRIMARY KEY,
  clinic_id UUID,
  rule_type ENUM('adherence_drop', 'vital_trend', 'glucose_spike'),
  threshold FLOAT,
  action TEXT (e.g., 'send_sms'),
  enabled BOOLEAN,
  FOREIGN KEY (clinic_id) REFERENCES clinics(id)
);
```

---

## 🔌 Required API Endpoints

### Patient Management
```
GET    /api/patients?clinic_id=X&sort=risk  → List patients with risk scores
GET    /api/patients/[id]                    → Single patient + full history
POST   /api/patients                         → Create new patient
POST   /api/patients/[id]/import             → Import history from clinic
PATCH  /api/patients/[id]                    → Update patient info
```

### Vitals & Monitoring
```
GET    /api/patients/[id]/vitals             → Recent vitals
POST   /api/patients/[id]/vitals             → Log new vital reading
GET    /api/patients/[id]/risk-score         → Calculate AI risk score
```

### Family & Contacts
```
GET    /api/patients/[id]/family             → List family contacts
POST   /api/patients/[id]/family             → Add family member
POST   /api/patients/[id]/send-sms           → Send Darija notification
```

### AI & Clinical Chat
```
POST   /api/chat/hele                        → Stream Hela AI response
GET    /api/patients/[id]/clinical-summary   → AI-generated summary
```

### Reports
```
POST   /api/reports/generate-pdf             → Generate clinical PDF
GET    /api/reports/[id]                     → Retrieve generated report
```

### Alerts & Drift Detection
```
GET    /api/alerts                           → List active alerts for clinic
GET    /api/alerts/[patient_id]              → Patient-specific alerts
POST   /api/alerts/[id]/dismiss              → Dismiss alert
```

---

## 🎛️ Dashboard Pages & Components

### Main Dashboard (`/dashboard`)
- **Top Bar**: Clinic name, doctor name, quick search
- **Left Sidebar**: Navigation (Patients, Reports, Settings, Profile)
- **Risk Queue Section**: Sortable patient cards by risk
- **Quick Stats**: Total patients, alerts count, today's adherence %

### Patient Detail View (`/dashboard/patients/[id]`)
- **Header**: Patient name, age, conditions, current risk score
- **Tabs**:
  - **Vitals**: Chart of BP, glucose, weight over time
  - **Adherence**: Medication timeline + compliance %
  - **History**: Imported data timeline
  - **Alerts**: Active clinical drift alerts
  - **Family**: Family contact info
  - **Chat**: Hela AI conversation panel
- **Actions**: Generate Report, Edit Info, Add Vitals, Message Family

### Add/Import Patient Modal (`/dashboard/patients/new`)
- **Form Fields**: Name, DOB, Conditions, Phone
- **Toggle**: "Import from Another Clinic"
- **Import Fields**: Previous Clinic ID, Search & fetch history
- **Family Section**: Add family members inline

### Reports Gallery (`/dashboard/reports`)
- **List**: Generated PDFs with dates
- **Actions**: Download, Email to Specialist, Delete

### Settings (`/dashboard/settings`)
- **Clinic Info**: Name, address, contact
- **Alert Rules**: Customize drift detection thresholds
- **SMS Gateway**: Twilio/Vonage keys
- **Users**: Add doctors/nurses

---

## 🔐 Key Implementation Notes

1. **Risk Scoring Algorithm**: Must be configurable per clinic; default uses:
   - HbA1c trend (diabetes risk)
   - BP trend (hypertension risk)
   - Adherence drop (behavioral risk)
   - Vital spike detection (acute risk)

2. **RAG/Vector Search**: Patient history must be indexed in embeddings for Hela AI:
   - Store embeddings of all vitals, notes, and historical data
   - On chat query, retrieve relevant historical context

3. **SMS Localization**: Support Darija, French, English
   - Pre-written templates for common messages
   - Example Darija: "Ammi, labess? Maranich nchoufek khdit dwa..."

4. **Accessibility**: 
   - Dark mode support (blue theme adapts)
   - Keyboard navigation
   - Screen reader friendly

5. **Performance**: 
   - Cache patient lists with SWR
   - Lazy-load patient history
   - Debounce risk score recalculation

---

## 📌 Customization & Editing Capabilities

The dashboard must support **zero-code clinic customization**:

### Editable Elements
- Dashboard layout (drag-drop widget positions)
- Alert thresholds (doctors adjust risk sensitivity)
- SMS message templates
- Color theming (light/dark mode)
- Patient card display fields

### Admin Panel for Customization (`/admin/customize`)
- **Dashboard Builder**: Drag widgets, reorder sections
- **Alert Config**: Set thresholds for each condition
- **SMS Templates**: Edit Darija/French messages
- **Theme Editor**: Adjust primary color, fonts

---

## ✅ Quality Checklist

- [ ] All pages load in <2 seconds
- [ ] Risk scores update in real-time
- [ ] SMS sends are logged and trackable
- [ ] PDF generation works offline-capable
- [ ] AI chat responses stream smoothly
- [ ] Mobile responsive (tablets for clinic use)
- [ ] Dark mode glassmorphic theme works
- [ ] Accessibility audit passes WCAG AA
- [ ] Patient data encrypted at rest
- [ ] All API calls have proper error handling

---

## 🚀 Implementation Priority

**Phase 1 (MVP)**: Risk Queue + Patient List + Vitals Logging
**Phase 2**: Smart Onboarding + Family Contacts + Basic Alerts
**Phase 3**: Hela AI Chat + RAG Search + Clinical Summaries
**Phase 4**: PDF Reports + Specialist Handovers
**Phase 5**: Advanced Customization Dashboard

---

## 📧 Backend Data Structure Example

```json
{
  "patient": {
    "id": "uuid",
    "name": "Khalti Zohra",
    "conditions": ["Hypertension", "Diabetes"],
    "risk_score": 7.2,
    "latest_vitals": {
      "bp": "155/95",
      "glucose": 185,
      "weight": 78,
      "timestamp": "2025-01-15T09:30:00Z"
    },
    "adherence": {
      "last_30_days": 0.65,
      "trend": "declining",
      "alert": "adherence_drop"
    },
    "family_contacts": [
      {
        "name": "Ahmed (Son)",
        "phone": "+213xxx",
        "language": "darija",
        "consent": true
      }
    ]
  }
}
```

---

**This specification ensures your dashboard is beautiful, functional, and ready for real-world clinical use.**
