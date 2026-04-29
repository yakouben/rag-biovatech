# ChronicCare Dashboard: Complete Developer Specification
**Based on:** Hela AI Vision - The "Medecine Suive" Early Warning System  
**Production Backend:** `https://web-production-fadce.up.railway.app`  
**Status:** Ready for Frontend Development

---

## PART 1: VISION RECAP (5 CORE SCENES)

### 🟢 SCENE 1: The Morning "Pulse" (Risk-Based Triage)
- **What it does:** AI analyzes all patient vitals overnight. Dashboard shows "Risk Queue" at login.
- **Key feature:** Algerian-Calibrated Decision Tree ranks patients by clinical risk (e.g., Ammi Ahmed: 8.5/10 High Risk)
- **User action:** Doctor sees top 3-5 patients needing urgent attention immediately.
- **Outcome:** Replaces manual triage; saves hours per day.

### 🤝 SCENE 2: The "Seamless Handover" (Smart Onboarding)
- **What it does:** New patient (Khalti Zohra) arrives with history from another clinic.
- **Key features:**
  - [+ Add New Patient] → "Import History" from previous clinic
  - Family Access: Add son's phone for SMS notifications
  - Auto-population of clinical summary from historical data
- **Magic:** System auto-sends warm Darija SMS to family: *"Marhab bikom f Biovatech..."*
- **User action:** Hela AI instantly displays clinical trend summary.

### 🚨 SCENE 3: Spotting the "Silent Crisis" (Clinical Drift Detection)
- **What it does:** Monitor medication adherence patterns in real-time.
- **Key feature:** Alert fires if adherence drops (e.g., 95% → 40% in 3 days).
- **Nurture Notification:** System drafts warm Darija nudge: *"Ammi, labess? Maranich nchoufek..."*
- **User action:** Doctor clicks [Send] to engage patient without full consultation.

### 🤖 SCENE 4: Consulting the "Digital Colleague" (Doctor-AI Chat)
- **What it does:** RAG-powered chat panel for clinical queries.
- **Example query:** "How has Zohra's BP responded to Lisinopril over 6 months?"
- **Magic:** Hela retrieves historical data, cross-references Algerian medical glossary, provides insight.
- **Integration:** Chat panel on right sidebar, real-time RAG search.

### 📄 SCENE 5: The "One-Click" Specialist Handover (Automated Reporting)
- **What it does:** Generate PDF clinical reports for specialist referral.
- **Contents:**
  - Imported clinical history
  - Risk score visualization
  - Adherence graphs
  - Hela AI clinical reasoning
- **Outcome:** Beautiful, ready-to-print/email specialist referral in seconds.

---

## PART 2: DESIGN SPECIFICATIONS

### Typography & Font
- **Primary Font:** Urbanist (Google Fonts)
- **Heading:** Urbanist Bold (700)
- **Body:** Urbanist Regular (400) / Medium (500)
- **Code/Monospace:** JetBrains Mono

### Color Palette (Sky Blue Theme with Glassmorphism)
| Color | Hex | Usage |
|-------|-----|-------|
| Sky Blue (Primary) | #0EA5E9 | Buttons, links, accents |
| Light Sky | #E0F2FE | Cards, backgrounds |
| White/Glass | #FFFFFF (80% opacity) | Glassmorphism cards |
| Dark Navy | #1E293B | Text, headings |
| Soft Gray | #F1F5F9 | Dividers, secondary elements |
| Risk Red | #EF4444 | High-risk alerts |
| Warning Amber | #F59E0B | Medium-risk alerts |
| Safe Green | #10B981 | Low-risk, adherence good |

### Glassmorphism Elements
- **Card background:** `rgba(255, 255, 255, 0.8)` with `backdrop-filter: blur(10px)`
- **Border:** `1px solid rgba(15, 165, 233, 0.2)` (subtle sky blue border)
- **Shadow:** `0 8px 32px rgba(15, 165, 233, 0.1)`
- **No Vibecoding:** Avoid rainbow gradients, harsh shadows, oversaturated animations

### UX Principles
- **Simplicity first:** One-click actions, no nested menus
- **Elegance:** Whitespace, subtle transitions (200ms ease)
- **Accessibility:** WCAG AA minimum, clear focus states
- **Mobile-first:** Responsive down to 375px

---

## PART 3: DASHBOARD ARCHITECTURE

### Main Dashboard Pages

#### Page 1: Risk Queue (Homepage)
**Route:** `/dashboard`  
**Purpose:** Doctor sees all patients ranked by clinical risk.

**Components:**
- Header: Welcome message + Quick filters
- Risk Queue Table:
  - Patient name, age, primary condition
  - Risk score (0-10 with color coding)
  - Last vitals (BP, glucose, etc.)
  - Action buttons: View Details, Send Alert, Schedule
- Side Widget: Today's alerts, pending tasks

**API Calls:**
```
GET https://web-production-fadce.up.railway.app/api/patients/risk-queue
GET https://web-production-fadce.up.railway.app/api/alerts/pending
GET https://web-production-fadce.up.railway.app/api/tasks/today
```

---

#### Page 2: Patient Details
**Route:** `/dashboard/patients/:patientId`  
**Purpose:** Deep dive into single patient profile.

**Sections:**
- Patient Header: Name, age, conditions, photo
- Vitals Timeline: Interactive graph (BP, glucose, weight over 6 months)
- Medication Adherence: % chart with trend
- Family Contacts: Quick SMS/call options
- Clinical History: Imported records from other clinics
- Hela Chat Panel: Right sidebar for AI consultation
- Action buttons: Edit Profile, Add Vitals, Generate Report, Refer Specialist

**API Calls:**
```
GET https://web-production-fadce.up.railway.app/api/patients/:patientId
GET https://web-production-fadce.up.railway.app/api/vitals/:patientId/history
GET https://web-production-fadce.up.railway.app/api/adherence/:patientId
GET https://web-production-fadce.up.railway.app/api/family-contacts/:patientId
GET https://web-production-fadce.up.railway.app/api/clinical-history/:patientId
POST https://web-production-fadce.up.railway.app/api/chat/rag-query (Hela AI)
```

---

#### Page 3: Add/Import Patient
**Route:** `/dashboard/patients/new`  
**Purpose:** Onboard new patient with optional history import.

**Workflow:**
1. Basic info: Name, Age, Conditions, Contact
2. Import option: "Has history from another clinic?"
   - If YES: Clinic ID input → Auto-populate historical data
   - If NO: Start fresh
3. Family Access: Add family member phone numbers (Darija SMS enabled)
4. Confirmation: Show summary before save

**API Calls:**
```
POST https://web-production-fadce.up.railway.app/api/patients/create
GET https://web-production-fadce.up.railway.app/api/import/clinic/:clinicId/patient/:patientId
POST https://web-production-fadce.up.railway.app/api/family-contacts/add
POST https://web-production-fadce.up.railway.app/api/notifications/send-welcome-sms
```

---

#### Page 4: Reports & Analytics
**Route:** `/dashboard/reports`  
**Purpose:** Clinic-wide analytics + individual patient report generation.

**Sections:**
- Clinic Dashboard: Total patients, avg risk score, adherence rate, alerts today
- Patient Report Generator: Select patient → download/email clinical PDF
- Export Data: Monthly cohort analysis for research

**API Calls:**
```
GET https://web-production-fadce.up.railway.app/api/analytics/clinic-summary
GET https://web-production-fadce.up.railway.app/api/reports/patient/:patientId
POST https://web-production-fadce.up.railway.app/api/reports/generate-pdf
```

---

#### Page 5: Settings & Customization
**Route:** `/dashboard/settings`  
**Purpose:** Doctor-level customization for thresholds, SMS templates, themes.

**Sections:**
- Thresholds: Set custom BP, glucose, weight limits for risk calculation
- SMS Templates: Edit Darija notification messages
- Theme: Light/Dark mode (maintain sky blue regardless)
- Integrations: Lab API keys, insurance connections
- Team: Add other doctors/nurses to clinic

**API Calls:**
```
GET https://web-production-fadce.up.railway.app/api/settings/thresholds
POST https://web-production-fadce.up.railway.app/api/settings/update-thresholds
GET https://web-production-fadce.up.railway.app/api/settings/sms-templates
POST https://web-production-fadce.up.railway.app/api/settings/update-sms-template
```

---

## PART 4: BACKEND API ENDPOINTS (Complete Reference)

### Base URL
```
https://web-production-fadce.up.railway.app/api
```

### Authentication
```
GET /auth/me
POST /auth/login
POST /auth/logout
POST /auth/refresh-token
```

### Patients
```
GET /patients/risk-queue              # Risk-sorted list
GET /patients/:patientId               # Single patient details
POST /patients/create                  # Add new patient
PUT /patients/:patientId/update        # Edit patient
DELETE /patients/:patientId            # Remove patient
GET /patients/search?q=name            # Search patients
```

### Vitals
```
GET /vitals/:patientId/history         # 6-month history for graphs
POST /vitals/:patientId/log            # Record new vital reading
GET /vitals/:patientId/latest          # Most recent reading
PUT /vitals/:vitalId/update            # Correct reading
```

### Adherence
```
GET /adherence/:patientId              # % compliance data
GET /adherence/:patientId/trend        # 30-day trend
POST /adherence/:patientId/log         # Log medication taken
```

### Clinical History Import
```
GET /import/clinic/:clinicId/patient/:patientId  # Fetch from other clinic
POST /import/save                      # Save imported data to this clinic
```

### Family Contacts
```
GET /family-contacts/:patientId        # List family members
POST /family-contacts/add              # Add family member
DELETE /family-contacts/:contactId     # Remove contact
```

### Alerts & Clinical Drift
```
GET /alerts/pending                    # All pending alerts for doctor
GET /alerts/:patientId                 # Patient-specific alerts
POST /alerts/:patientId/acknowledge    # Mark alert as seen
GET /drift-detection/:patientId        # Clinical drift score
```

### Hela AI Chat (RAG)
```
POST /chat/rag-query                   # Send question, get AI response
  Payload: { patientId, question, context }
  Response: { answer, sources, confidence }
```

### SMS Notifications
```
POST /notifications/send-sms           # Send Darija SMS
POST /notifications/send-welcome-sms   # Onboarding SMS
GET /notifications/templates           # List available Darija templates
```

### Reports & PDF Generation
```
GET /reports/patient/:patientId        # Fetch report data
POST /reports/generate-pdf             # Create PDF file
GET /reports/:reportId/download        # Download as file
POST /reports/:reportId/email          # Email to specialist
```

### Analytics
```
GET /analytics/clinic-summary          # Clinic KPIs
GET /analytics/risk-distribution       # Chart data
GET /analytics/adherence-by-condition  # Adherence breakdown
```

### Settings
```
GET /settings/thresholds               # Current doctor's risk thresholds
POST /settings/update-thresholds       # Edit thresholds
GET /settings/sms-templates            # Darija message templates
POST /settings/update-sms-template     # Edit SMS template
```

---

## PART 5: DATA STRUCTURES & DATABASE SCHEMA

### Users (Doctors)
```json
{
  "id": "uuid",
  "email": "doctor@clinic.dz",
  "firstName": "Yassine",
  "lastName": "Bendjelloul",
  "clinicName": "Clinique Algiers",
  "language": "ar", // Darija preference
  "thresholds": {
    "bpSystolic_max": 140,
    "bpDiastolic_max": 90,
    "glucose_min": 80,
    "glucose_max": 200
  },
  "smsTemplates": { /* custom Darija messages */ },
  "createdAt": "2024-01-15",
  "updatedAt": "2024-04-29"
}
```

### Patients
```json
{
  "id": "uuid",
  "doctorId": "uuid",
  "firstName": "Ahmed",
  "lastName": "Benali",
  "age": 58,
  "conditions": ["Diabetes", "Hypertension"],
  "primaryCondition": "Diabetes",
  "importedFromClinic": "Clinic Oran ID",
  "clinicalSummary": "Stable BP, HbA1c trending upward",
  "riskScore": 8.5,
  "lastVitalUpdate": "2024-04-29T08:30:00Z",
  "createdAt": "2024-03-01",
  "updatedAt": "2024-04-29"
}
```

### Vitals
```json
{
  "id": "uuid",
  "patientId": "uuid",
  "timestamp": "2024-04-29T08:30:00Z",
  "readings": {
    "bpSystolic": 155,
    "bpDiastolic": 95,
    "glucose": 185,
    "weight": 72.5,
    "heartRate": 78
  },
  "notes": "Patient reports fatigue"
}
```

### Adherence
```json
{
  "id": "uuid",
  "patientId": "uuid",
  "medicationId": "uuid",
  "date": "2024-04-29",
  "taken": true,
  "adherencePercent": 95, // 30-day rolling average
  "trend": "down" // or "stable", "up"
}
```

### Family Contacts
```json
{
  "id": "uuid",
  "patientId": "uuid",
  "name": "Omar",
  "relation": "Son",
  "phoneNumber": "+213612345678",
  "smsEnabled": true,
  "createdAt": "2024-03-15"
}
```

### Alerts
```json
{
  "id": "uuid",
  "patientId": "uuid",
  "type": "HIGH_RISK | DRIFT_DETECTED | URGENT_VITALS",
  "severity": "high | medium | low",
  "message": "BP spiked to 155/95",
  "suggestedAction": "Review medication",
  "acknowledged": false,
  "createdAt": "2024-04-29T06:00:00Z"
}
```

---

## PART 6: DEVELOPMENT PHASES

### Phase 1: MVP (2 weeks)
- [ ] Auth: Doctor login/signup
- [ ] Risk Queue: Display sorted patients
- [ ] Patient Details: Basic profile + vitals graph
- [ ] Add Patient: Basic form

### Phase 2: Smart Features (2 weeks)
- [ ] Import History: Clinic data import
- [ ] Family Access: SMS notifications
- [ ] Adherence Tracking: Real-time %
- [ ] Clinical Drift Detection: Alert system

### Phase 3: AI Integration (2 weeks)
- [ ] Hela Chat: RAG-powered sidebar
- [ ] Clinical Summary: Auto-generated insights
- [ ] Nurture Notifications: Darija SMS drafting

### Phase 4: Reporting (1 week)
- [ ] PDF Generation: Complete clinical reports
- [ ] Export/Email: Share with specialists

### Phase 5: Customization (1 week)
- [ ] Settings: Thresholds, SMS templates
- [ ] Analytics Dashboard: Clinic KPIs

---

## PART 7: FRONTEND TECH STACK

- **Framework:** Next.js 16 (App Router)
- **UI Framework:** React 19 with TypeScript
- **Styling:** Tailwind CSS + custom glassmorphism
- **Font:** Urbanist (Google Fonts)
- **Charts:** Recharts (for vitals graphs)
- **State:** SWR (data fetching & caching)
- **Forms:** React Hook Form + Zod validation
- **Icons:** Lucide React
- **PDF:** PDFKit / jsPDF (for report generation)

---

## PART 8: KEY CUSTOMIZATION POINTS

### For Doctors to Control:
1. **Risk Thresholds:** BP max, glucose min/max, weight limits
2. **SMS Templates:** Edit Darija messages (warm, cultural tone)
3. **Family SMS List:** Who gets notifications
4. **Theme:** Light/Dark (sky blue adjusts automatically)
5. **Alerts:** Which events trigger notifications

### For Admins to Control:
1. **Clinic branding:** Logo, clinic name in reports
2. **User management:** Add/remove doctors
3. **Import sources:** Which clinics can export data
4. **Analytics filters:** Patient cohort analysis

---

## PART 9: QUALITY CHECKLIST

- [ ] All API calls use `https://web-production-fadce.up.railway.app/api`
- [ ] Glassmorphism cards: 80% opacity white + sky blue borders
- [ ] Urbanist font applied to all text
- [ ] No Vibecoding effects: clean, professional animations only
- [ ] Risk Queue loads in < 2 seconds
- [ ] Patient Details fully responsive (mobile-first)
- [ ] Darija SMS notifications send in real-time
- [ ] RAG chat responds within 3 seconds
- [ ] PDF reports generate in < 5 seconds
- [ ] All forms have Zod validation
- [ ] Dark mode toggles sky blue seamlessly
- [ ] Accessibility: Focus states, color contrast WCAG AA+

---

## PART 10: DEPLOYMENT

**Backend URL:** `https://web-production-fadce.up.railway.app`  
**Environment Variables (Frontend):**
```
NEXT_PUBLIC_API_URL=https://web-production-fadce.up.railway.app/api
NEXT_PUBLIC_APP_NAME=ChronicCare Dashboard
```

---

**Ready to build. Questions? Reference this spec.**
