# 📱 HELA AI: Mobile Patient App - Master Specification
> **Project:** ChronicCare AI (Hela)
> **Target:** Algerian Patients (Elderly focus)
> **Aesthetics:** Modern Glassmorphism | Sky Blue Palette | Urbanist Typography
> **Base URL:** `https://web-production-fadce.up.railway.app/api/v1`
> **Auth Header:** `X-Internal-Key: hela-secret-123`

---

## 🎨 1. Design System (The "Blue Sky" Aesthetic)
The app must feel **calm, premium, and trustworthy**. Avoid clinical whites; use soft sky gradients and glass effects.

- **Typography:** Primary font **'Urbanist'** (Google Fonts). Use **'Amiri'** or **'Lateef'** for RTL Darija text.
- **Palette:**
    - **Primary:** Sky Blue (`#00B4DB` to `#0083B0` gradient).
    - **Background:** Soft Blue Tint (`#F0F8FF`).
    - **Cards:** Glassmorphism (White with 20% opacity, Backdrop blur 15px, thin white border 1px).
- **Styles:** Rounded corners (24px+), soft shadows, micro-animations for every AI interaction.

---

## 🛠 2. Core Features & Screen Logic

### Screen 1: Smart Activation (No Login)
- **Concept:** Elderly patients hate passwords.
- **Action:** Scan QR Code (provided by doctor) OR enter 6-digit OTP.
- **Logic:** Calls `GET /patient/{id}/profile` to verify and store the `patient_id` locally using `shared_preferences`.

### Screen 2: Dashboard (The "Home")
- **Greeting:** "Marhba [Name] 👋" in Urbanist Bold.
- **Nurture Card:** Displays the AI Nurture message if `trigger_notification` is true from `GET /check-drift`. 
    - *Style:* Glass card with amber border.
- **Quick Vitals:** Last recorded BP and Glucose in large, readable bubbles.

### Screen 3: Hela AI Chat (The Core)
- **Thinking Bubble (CRITICAL):** While waiting for a response, display a pulsing glass bubble. 
    - **Requirement:** Loop through the `thinking_steps` array from the API response to show the AI's "internal work" (e.g., *"Searching glossary..."*, *"Analyzing your symptoms..."*).
- **Message Bubbles:** 
    - **Patient:** Right-aligned, Sky Blue.
    - **Hela:** Left-aligned, Glass/White. RTL support for Darija.
- **Risk Badge:** Color-coded chip (Low: Green, Moderate: Yellow, High: Red) appended to Hela's response.
- **Glossary Chips:** If `glossary_context` is returned, show tappable chips below the bubble. Tapping opens a "Glass Bottom Sheet" with the translation.

### Screen 4: Clinical History (The "Trends")
- **Charts:** Use `fl_chart`.
    - BP: Double line (Systolic/Diastolic).
    - Glucose: Single line with "Normal Zone" shading.
- **Logic:** Fetches data from `GET /history?days=30`.

---

## 🔌 3. API Integration Guide

### [POST] `/chat`
- **Body:** `{ "patient_id": "...", "patient_symptoms": "...", "include_glossary": true }`
- **Success Handling:** Map `hela_response` to UI. Loop `thinking_steps` for the loader. Show `risk_score` badges.

### [GET] `/patient/{id}/check-drift`
- **Purpose:** Proactive check-in.
- **Action:** If `trigger_notification` is true, pop up the Nurture Card immediately.

### [POST] `/glossary/search`
- **Body:** `{ "query": "...", "language": "darija" }`
- **UI:** A searchable dictionary screen with Urbanist font and RTL results.

### [POST] `/reports/generate`
- **Action:** Trigger PDF download. Show a glass progress bar.

---

## 🏗 4. Technical Requirements
- **Framework:** Flutter (Latest Stable).
- **State Management:** Riverpod or Bloc (must be robust).
- **Networking:** Dio with a base interceptor for the `X-Internal-Key`.
- **RTL:** Native support for Arabic/Darija layouts.
- **Accessibility:** Large touch targets, High contrast, Screen reader support for elderly users.

---

## 🎯 Developer Mission
Your goal is to build an app that feels like a **caring daughter/son** (Hela) living inside a **premium sky-blue interface**. Every time the patient talks to the app, they must see that Hela is "Thinking" (via `thinking_steps`) and feel reassured by the medical accuracy proven by the `glossary_context`.
