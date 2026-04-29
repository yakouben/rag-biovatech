# ChronicCare Dashboard – Developer Specification

## Core Vision
An **Early Warning System** for chronic disease management, not a database. AI-powered triage, seamless patient handovers, cultural sensitivity (Darija), and family-integrated care.

---

## 5 Core Scenes (Product Requirements)

### Scene 1: Risk-Based Triage (Risk Queue)
- **Algerian-Calibrated Decision Tree** analyzes all patient vitals overnight
- Dashboard shows patients ranked by risk score (0-10)
- High-risk patients (Red) displayed first, Medium (Yellow), Low (Green)
- One-click access to full patient record

### Scene 2: Smart Onboarding (Seamless Handover)
- **Import History**: Enter previous clinic ID to auto-populate patient data (5-year history)
- **Family Access**: Add family member phone numbers for SMS notifications
- **Clinical Summary**: AI auto-generates 2-3 key insights from imported history
- Automatic Darija SMS to family: "Marhab bikom f Biovatech..."

### Scene 3: Clinical Drift Detection (Silent Crisis Alert)
- Monitor medication adherence trends (detect drops from 95% → 40% in 3 days)
- Trigger **Nurture Notifications** in Darija: "Ammi, labess? Sahtek hiya el sah..."
- Gentle nudge without requiring a full consultation

### Scene 4: Doctor-AI Chat (Hela Doctor Chat)
- **RAG Search** over entire clinical history + Algerian medical glossary
- Doctor queries: "How has Zohra's BP responded to Lisinopril over 6 months?"
- AI returns: Exact trends, medication response, clinical insights
- Sidebar chat panel, real-time responses

### Scene 5: Automated Reporting (Specialist Handover)
- One-click **[Generate Clinical Report]** button
- Auto-compiles: imported history, risk scores, adherence graphs, AI reasoning
- Output: Beautiful PDF ready for print or secure email
- No manual handwriting of referral letters

---

## Design Requirements

### Typography
- **Font**: Urbanist (all headers, body text)

### Color Scheme
- **Primary**: Sky Blue (#0EA5E9 or similar)
- **Secondary**: White/Off-White backgrounds
- **Accent**: Light blue glassmorphism overlays
- **Text**: Dark gray (#1F2937) on light backgrounds
- **NO**: Vibecoding effects, gradients, or overly decorative elements

### Aesthetic
- Clean, minimal glassmorphism (frosted glass effect on cards)
- Professional, trustworthy, medical-grade appearance
- Light spacing, high readability
- Intuitive navigation—no complex interactions

---

## Database Schema

### Core Tables

**users**
- user_id (UUID, PK)
- email, password_hash, full_name
- role ('doctor', 'patient', 'admin')
- clinic_id (FK)
- created_at

**patients**
- patient_id (UUID, PK)
- doctor_id (FK to users)
- full_name, date_of_birth, phone
- imported_history (JSON: from previous clinic)
- risk_score (0-10, updated daily)
- last_assessment_date
- created_at

**vitals**
- vital_id (UUID, PK)
- patient_id (FK)
- glucose, systolic_bp, diastolic_bp, weight, heart_rate
- recorded_at
- source ('manual', 'imported')

**family_contacts**
- contact_id (UUID, PK)
- patient_id (FK)
- phone_number, relationship, name
- opted_in_sms (boolean)

**adherence_history**
- adherence_id (UUID, PK)
- patient_id (FK)
- medication_name, adherence_percentage (0-100)
- date_week
- calculated_at

**alerts**
- alert_id (UUID, PK)
- patient_id (FK)
- alert_type ('high_risk', 'drift_detected', 'urgent')
- message, message_darija
- sent_at, acknowledged_at

**clinical_reports**
- report_id (UUID, PK)
- patient_id (FK), doctor_id (FK)
- report_type ('summary', 'specialist_handover')
- pdf_url, created_at

---

## API Endpoints

### Patients
- `GET /api/patients` – List all patients (risk-sorted)
- `GET /api/patients/:id` – Full patient record
- `POST /api/patients` – Create new patient
- `POST /api/patients/import` – Import history by clinic ID
- `PATCH /api/patients/:id` – Update patient info

### Vitals
- `GET /api/vitals/:patient_id` – Latest vitals
- `POST /api/vitals` – Record new vitals
- `GET /api/vitals/:patient_id/history` – Trend data (30/60/90 days)

### Adherence
- `GET /api/adherence/:patient_id` – Current adherence %
- `GET /api/adherence/:patient_id/trend` – Adherence trend (detect drift)

### Alerts
- `GET /api/alerts/pending` – Active alerts for doctor
- `POST /api/alerts/:id/acknowledge` – Mark alert as seen
- `POST /api/alerts/send-nurture` – Send Darija notification

### AI / Doctor Chat
- `POST /api/chat/ask` – RAG query to Hela AI
  - Payload: `{ patient_id, query, context }`
  - Returns: `{ answer, sources, confidence }`

### Family Access
- `POST /api/family/invite` – Add family contact
- `POST /api/family/send-sms` – Send Darija SMS notification

### Reports
- `POST /api/reports/generate` – Generate clinical PDF
  - Payload: `{ patient_id, report_type }`
  - Returns: `{ pdf_url, created_at }`

---

## Dashboard Pages & Components

### Main Layout
- **Header**: Logo, Doctor name, Quick search, Logout
- **Sidebar**: Nav (Patients, Reports, Settings)
- **Main Content**: Flexible grid layout

### Page: Risk Queue (Homepage)
- **Risk Triage Table**: Patient name, Risk score (0-10), Last vital, Status (Red/Yellow/Green)
- **Sort/Filter**: By risk, by condition, by date
- **Actions**: Click row → Go to patient detail

### Page: Patient Detail
- **Tabs**: Overview, Vitals History, Adherence, Family, Chat
- **Overview Tab**: 
  - Risk score badge
  - Latest vitals (glucose, BP, weight)
  - Clinical summary (if imported)
  - Quick actions: [Add Vital], [Import History], [Generate Report]
- **Vitals History Tab**: 
  - Line chart (glucose trend, BP trend)
  - Table with date/value/source
- **Adherence Tab**: 
  - Adherence % progress bar
  - Trend indicator (up/down/stable)
  - Drift alert (if applicable)
- **Family Tab**: 
  - List of family contacts
  - Add new contact button
  - SMS opt-in status
- **Chat Tab**: 
  - Hela Doctor Chat panel
  - Query input field
  - Conversation history

### Page: Add/Import Patient
- **Form**: Name, DOB, Phone, Condition
- **Import Section**: Previous clinic ID → Auto-populate
- **Family Access**: Add family phone numbers
- **Submit Button**: [Create Patient]

### Page: Reports
- **Table**: Patient, Report type, Date created, PDF link
- **Generate Report**: Button → Select patient → Select type → Download PDF

### Page: Settings (Doctor)
- **Profile**: Edit name, clinic
- **Preferences**: Notification settings, Darija SMS enabled
- **API Keys**: For clinic integrations (future)

---

## Implementation Priorities (5 Phases)

**Phase 1 (MVP)**: Risk Queue + Patient Detail + Vitals
**Phase 2**: Smart Onboarding + Family SMS
**Phase 3**: Clinical Drift Detection + Alerts
**Phase 4**: Hela Doctor Chat + RAG Integration
**Phase 5**: Automated Reporting + PDF Generation

---

## Tech Stack
- **Frontend**: Next.js 16, React 19, TailwindCSS
- **Fonts**: Urbanist (Google Fonts)
- **State**: SWR (client-side data caching)
- **Backend**: Next.js API Routes (or separate Node service)
- **Database**: PostgreSQL (Supabase/Neon)
- **PDF Generation**: jsPDF or ReportLab
- **SMS**: Twilio or local SMS provider
- **AI**: Hela API (RAG + Algerian medical glossary)

---

## Customization & Editability

### Doctor-Level Customization (Admin Panel)
- [ ] Adjust risk thresholds per condition
- [ ] Edit Darija SMS templates
- [ ] Set color schemes (future white-label)
- [ ] Configure adherence monitoring frequency
- [ ] Choose which vitals to track

### Data Editing
- Edit patient info (name, DOB, phone)
- Edit recorded vitals (with audit log)
- Delete family contacts
- Update medication list

---

## UX Principles
1. **One-Click Access**: Every critical action ≤ 2 clicks
2. **Cultural Warmth**: Darija messaging, family integration
3. **Simplicity Over Features**: No complexity—focus on core 5 scenes
4. **Trustworthy Aesthetic**: Medical-grade design, glassmorphism, sky blue
5. **Dark/Light Mode Ready**: (Future) Use CSS custom properties

---

## Success Metrics
- Dr. Yassine saves 1+ hour per morning on triage
- Family members receive SMS updates in Darija
- Clinical drift detected before it becomes an emergency
- Specialist handovers completed in <2 minutes
- Patient satisfaction score: >8/10
