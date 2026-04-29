# 📱 Hela AI: Complete Flutter Integration Guide

This document is the comprehensive manual for integrating the **Hela AI** patient companion into the Flutter mobile application.

## 🤖 AI Generator Prompt (Copy & Paste)
*Copy this prompt into Cursor, Gemini, or Claude to generate the service layer code instantly.*

> "You are a Senior Flutter Engineer. We are building a high-performance **`ApiService`** using the **`dio`** package to connect to our Hela AI Backend.
> 
> **Backend Specs:**
> - **Base URL**: `https://web-production-fadce.up.railway.app/api/v1`
> - **Auth**: None (Disabled for MVP)
> 
> **Endpoints to Implement:**
> 1. `POST /chat`: Main patient intake. Needs `patient_id`, `patient_symptoms`, and a `patient_data` object (age, bp, glucose, bmi, etc.). Returns `hela_response`, `risk_score`, and `extracted_entities`.
> 2. `GET /patient/{id}/check-drift`: Proactive adherence check. Returns `trigger_notification` and `nurture_message_darija`.
> 3. `POST /glossary/search`: Semantic search for medical terms.
> 4. `GET /health`: Basic health check for service status.
> 
> **Requirements:**
> 1. Use **`json_serializable`** or clean manual models for all Request/Response objects.
> 2. Implement a **`DioInterceptor`** to automatically add the `X-Internal-Key` and handle `401/500` errors globally.
> 3. Add robust **error handling** with custom Exception classes (e.g., `ClinicalValidationError`).
> 4. Ensure all calls are **asynchronous** and use the `Result` pattern (Success/Failure) for safe state management in the UI.
> 
> Please generate the full Dart code for the Models and the Service class. Do NOT include any UI code."

---

## 📡 Backend Configuration
*   **Production Base URL**: `https://web-production-fadce.up.railway.app/api/v1`
*   **Authentication**: None (Disabled for MVP Prototype)

---

## 🌟 Patient Features (Mobile)
1.  **Hela AI Companion**: A warm, empathetic voice/chat interface that understands Algerian Darija.
2.  **Voice-to-Vitals**: Patients can speak their symptoms, and the AI automatically extracts their Blood Pressure and Glucose levels.
3.  **Proactive Nurturing**: Background checks that detect if a patient has missed medications, triggering a "Nurture" notification in Darija.
4.  **Instant Risk Feedback**: Provides immediate visual feedback (Green/Yellow/Red) based on the patient's latest check-in.
5.  **Multilingual Support**: Seamlessly switches between Darija, French, and English based on the patient's preference.

---

## 🛠 Required API Endpoints

### 1. The Hela Chat (Main Intake)
*   **Endpoint**: `POST /chat`
*   **Use Case**: The core chat interface where patients describe how they feel.
*   **Request Body**:
    ```json
    {
      "patient_id": "p123",
      "patient_symptoms": "Rani nhas b dawkha w skhana", // Darija supported
      "patient_data": {
        "age": 65,
        "systolic_bp": 155,
        "diastolic_bp": 95,
        "fasting_glucose": 140,
        "bmi": 27,
        "smoking": false,
        "family_history": true,
        "comorbidities": 1
      },
      "include_glossary": true
    }
    ```
*   **Response Highlights**: Use `hela_response` for the text message and `risk_score` for the UI color.

### 2. Proactive Adherence Check (Nurture)
*   **Endpoint**: `GET /patient/{id}/check-drift`
*   **Use Case**: Run this in a background task or on app startup.
*   **Response**:
    ```json
    {
      "trigger_notification": true,
      "nurture_message_darija": "Ammi, labess? Matnsaych dwa dialek..."
    }
    ```

### 3. Medical Glossary (Education)
*   **Endpoint**: `POST /glossary/search`
*   **Use Case**: A "Medical Dictionary" feature where patients can search for terms they don't understand.
*   **Request**: `{"query": "السكري", "limit": 5, "language": "darija"}`

---

## 🗂 Dart Data Models

```dart
class PatientVitals {
  final int age;
  final int systolicBp;
  final int diastolicBp;
  final int fastingGlucose;
  final double bmi;
  final bool smoking;

  PatientVitals({
    required this.age,
    required this.systolicBp,
    required this.diastolicBp,
    required this.fastingGlucose,
    required this.bmi,
    this.smoking = false,
  });

  Map<String, dynamic> toJson() => {
    'age': age,
    'systolic_bp': systolicBp,
    'diastolic_bp': diastolicBp,
    'fasting_glucose': fastingGlucose,
    'bmi': bmi,
    'smoking': smoking,
  };
}
```

---

## 🎨 Flutter UX Guidelines (Elderly Patients)
1.  **Voice-First Interaction**: Use the `speech_to_text` package. The AI is optimized for transcribed Darija.
2.  **Visual Risk Indicators**:
    *   **HIGH**: Use `#EF4444` (Red) with an "Urgent" warning.
    *   **MODERATE**: Use `#F59E0B` (Amber).
    *   **LOW**: Use `#10B981` (Green).
3.  **Respectful Terms**: The AI uses "Khalti" (Auntie) and "Ammi" (Uncle). Ensure the UI reflects this warm, family-oriented tone.
4.  **Offline Grace**: Patients in Algeria may have spotty 4G. Implement `Dio` interceptors to handle timeouts and show a "Check connection" message.

---

## ⚠️ Important Note
The AI reasoning call (`/chat`) uses Gemini 1.5 Flash and performs RAG. It typically takes **2-4 seconds**. Always show a "Hela is thinking..." animation to manage user expectations.
