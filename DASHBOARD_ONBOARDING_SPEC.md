# 🖥️ Dashboard Frontend: Onboarding Integration Spec
> **Target:** Frontend Developer (React/Next.js)
> **Goal:** Implement the 2-path onboarding flow (New vs. Existing Patient)

---

## 🏗️ Screen 1: The Choice
When clicking "Add New Patient", show two large action cards:
1. **[Card A] New Hela User:** "Create a fresh medical profile for a new patient."
2. **[Card B] Existing Hela User:** "Import an existing patient via QR Scan."

---

## 📝 Path A: New Hela User (Full Form)

### 1. The Form (Fields)
Group these fields into logical sections (Tabs or Stepper):

**Section 1: Identity**
- `name` (String) - Full Name
- `age` (Int)
- `gender` (Dropdown: Male/Female)
- `phone` (String)
- `address` (String)

**Section 2: Medical Background**
- `medical_history_summary` (Textarea) - "Enter maladies, allergies, or previous conditions."
- `current_medications` (Textarea) - "List of current drugs and dosages."

**Section 3: Family Context (Crucial)**
- `family_contact_name` (String) - "Emergency Contact Name"
- `family_contact_phone` (String) - "Emergency Contact Phone"
- `family_access_granted` (Toggle) - "Allow family to receive alerts?"

**Section 4: Initial Vitals**
- `systolic_bp` (Int)
- `diastolic_bp` (Int)
- `fasting_glucose` (Int)
- `bmi` (Float)

### 2. The API Call
**Endpoint:** `POST /api/v1/onboard`
**Header:** `X-Internal-Key: hela-secret-123`
**Body:**
```json
{
  "profile": {
    "name": "Khalti Zohra",
    "age": 65,
    "gender": "Female",
    "phone": "0550123456",
    "family_contact_name": "Ahmed (Son)",
    "family_contact_phone": "0660112233",
    "medical_history_summary": "Hypertension for 10 years, Metformin for Diabetes."
  },
  "initial_vitals": {
    "systolic_bp": 145,
    "diastolic_bp": 90,
    "fasting_glucose": 160,
    "bmi": 28.5
  },
  "is_import": false
}
```

### 3. Success State (The "Pass")
Once saved, display a success modal with:
- **AI Summary:** Show `ai_analysis.clinical_summary` (Professional tone).
- **Patient Welcome:** Show `ai_analysis.welcome_message_darija` (Warm Darija).
- **QR CODE:** Generate a QR code containing the `patient_id`.
- **OTP:** Show a 6-digit code (e.g., `123 456`).
- **Instruction:** "Ask the patient to scan this QR or enter the OTP in their Hela Mobile App."

---

## 📲 Path B: Existing Hela User (Import)

### 1. The Scan
1. Open the device camera (use `react-qr-reader` or similar).
2. Scan the QR code from the patient's phone.
3. Extract the `patient_id` from the QR.

### 2. Verification
1. Ask the patient for the **Verification OTP** shown on their Hela app.
2. Enter the OTP on the Dashboard.

### 3. The API Call
**Endpoint:** `POST /api/v1/onboard`
**Body:**
```json
{
  "profile": {
    "id": "SCANNED_ID_HERE"
  },
  "is_import": true,
  "verification_otp": "123456"
}
```

### 4. Success State
- Show the patient's full history (fetched from backend).
- Notification: "Patient profile successfully linked to your clinic."

---

## 🎨 UI/UX Guidelines
- **RTL Support:** Ensure the Darija welcome message is displayed Right-to-Left in a beautiful Arabic font (e.g., 'Amiri').
- **Status Indicators:** Use a loading spinner while the AI is generating the summary (expect 2-3 seconds).
- **QR Code:** Ensure the QR code is high-resolution for easy scanning by old phones.
