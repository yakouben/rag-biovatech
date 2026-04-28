# 📱 ChronicCare: Flutter Integration Guide
**Target:** Patient & Family Mobile App
**Backend URL:** `https://web-production-fadce.up.railway.app`

## 🧠 The Integration Prompt
*Copy and paste this into your AI coding assistant (Cursor/Gemini/Claude):*

> "You are a Senior Flutter Developer. We are integrating an AI Brain (FastAPI) into the ChronicCare mobile app.
> 
> **Architecture Goal:**
> 1. Create an `AIService` using `dio` to communicate with `https://web-production-fadce.up.railway.app`.
> 2. **Main Feature:** A 'Talk to Nour' screen. It needs a high-fidelity 'Mic' button. Use the `speech_to_text` package to capture Algerian Darija voice.
> 3. Send the transcribed text to `POST /api/v1/chat`. Include `patient_id` and a `patient_data` object with vitals (blood pressure, glucose).
> 4. Handle the response: Display `nour_reasoning` (warm Darija text) and visualize the `risk_score` (low/moderate/high).
> 5. **Proactive Feature:** Create a background worker that calls `GET /patient/{id}/check-drift`. If `trigger_notification` is true, trigger a local push notification using the `nurture_message_darija`.
> 6. Use the `X-Internal-Key` header for authentication. Implement robust error handling for poor connectivity (common in Algeria)."

## 🔗 Required Endpoints

### 1. Nour Clinical Chat
- **Endpoint:** `POST /api/v1/chat`
- **Payload:**
  ```json
  {
    "patient_id": "p123",
    "patient_symptoms": "Rani nhas b dawkha w rasi rah ywaj3ni bezaf",
    "patient_data": {
      "systolic_bp": 150,
      "diastolic_bp": 95,
      "fasting_glucose": 110
    }
  }
  ```

### 2. Proactive Drift Check
- **Endpoint:** `GET /patient/{patient_id}/check-drift`
- **Usage:** Call this once daily or on app open. It detects if the patient has missed meds recently and generates a warm "Nurture" message in Darija.

## 🎨 UI/UX Requirements
- **Simplicity:** The app is for elderly patients. Use big buttons, high contrast, and minimal text.
- **Voice-First:** Nour should feel alive. Show a waveform animation when the user is speaking.
- **Respect:** Use the Darija terms provided by the AI (Khalti/Ammi).
