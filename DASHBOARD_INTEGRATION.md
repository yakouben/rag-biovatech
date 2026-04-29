# 🚀 ChronicCare AI: Complete Platform & Dashboard Integration Guide

This document serves as the comprehensive technical manual for the **ChronicCare AI (Hela)** platform. It contains the feature overview, API documentation, and implementation details required for full dashboard integration.

---

## 📡 Backend Configuration
*   **Production Base URL**: `https://web-production-fadce.up.railway.app/api/v1`
*   **Content-Type**: `application/json`
*   **Authentication**: Include the following header for all secure requests:
    ```http
    X-Internal-Key: [YOUR_INTERNAL_API_KEY]
    ```

---

## 🌟 Platform AI Features
1.  **Hela AI Companion**: A multilingual assistant (Darija, French, English) specialized in Diabetes and Hypertension.
2.  **Proactive Drift Detection**: Monitors drops in medication adherence and triggers caring "nurture" interventions.
3.  **Clinical Risk Assessment**: Custom-trained ML models calibrated for the Algerian population health profile.
4.  **Smart Entity Extraction**: Automatically parses symptoms, vitals, and medications from unstructured patient chat.
5.  **Evidence-Based RAG**: Grounds all AI responses in a verified medical knowledge base and clinical guidelines.
6.  **Doctor Intelligence**: Allows providers to query patient history trends using natural language.

---

## 🛠 Complete API Reference

### 1. Unified AI Chat & Reasoning
*   **Endpoint**: `POST /chat`
*   **Description**: The primary entry point for patient conversations. Performs risk scoring, entity extraction, and reasoning in one call.
*   **Request Body (`NOURRequest`)**:
    ```json
    {
      "patient_id": "string",
      "patient_symptoms": "Text in Darija/French/English",
      "patient_data": {
        "age": 50, "systolic_bp": 140, "diastolic_bp": 90, "fasting_glucose": 150, "bmi": 28, "smoking": false, "family_history": true, "comorbidities": 1
      },
      "include_glossary": true
    }
    ```
*   **Response**: Returns the AI response, extracted vitals, risk category, and clinical recommendations.

### 2. High-Risk Patient Queue (Dashboard Priority)
*   **Endpoint**: `GET /patients/risk-queue`
*   **Description**: Retrieves a list of all patients prioritized by their clinical risk level.
*   **Response**: Array of objects containing `patient_id`, `risk_score` (HIGH/MODERATE/LOW), and `predicted_risk_level`.

### 3. Patient History & Trend Data
*   **Endpoint**: `GET /patient/{patient_id}/history`
*   **Query Params**: `days=30`
*   **Description**: Structured historical data (BP, Glucose, BMI) for rendering trend charts.
*   **Response**: Chronological array of vitals and risk scores.

### 4. Proactive Adherence Check
*   **Endpoint**: `GET /patient/{patient_id}/check-drift`
*   **Description**: Compares 3-day vs 30-day adherence to detect sharp drops.
*   **Response**: `trigger_notification` (boolean) and `nurture_message_darija` (string).

### 5. Doctor-History Chat (RAG Assistant)
*   **Endpoint**: `POST /doctor/chat`
*   **Description**: Natural language querying over a specific patient's historical medical records.
*   **Request Body**:
    ```json
    {
      "patient_id": "string",
      "question": "Has the patient's systolic BP improved since last month?",
      "include_raw_history": false
    }
    ```

### 6. Clinical PDF Report Generation
*   **Endpoint**: `POST /reports/generate`
*   **Method**: Binary Stream (`application/pdf`)
*   **Query Params**: `patient_id`, `patient_name`, `adherence_days`.
*   **Description**: Generates a professional clinical report with graphs and AI assessments.

### 7. Medical Glossary Search
*   **Endpoint**: `POST /glossary/search`
*   **Description**: Semantic search across our Algerian-French-English medical dictionary.
*   **Request Body**: `{"query": "string", "limit": 10, "language": "darija"}`

### 8. Clinical Entity Extraction (Standalone)
*   **Endpoint**: `POST /nour`
*   **Description**: Use this if you only need the reasoning and entity extraction without the unified chat flow.

### 9. System Monitoring (Drift Detection)
*   **Endpoint**: `GET /drift-detection`
*   **Description**: Returns a report on the AI model's performance accuracy and whether retraining is needed.

### 10. Health Check
*   **Endpoint**: `GET /health`
*   **Description**: Verifies status of Database, Gemini AI, and Model services.

---

## 🗂 Data Models (TypeScript)

```typescript
export interface ClinicalEntities {
  symptoms: string[];
  medications: string[];
  missed_medications: string[];
  vitals: {
    systolic_bp?: number;
    diastolic_bp?: number;
    glucose?: number;
    bmi?: number;
  };
  clinical_note: string;
}

export interface RiskAssessmentResponse {
  risk_level: number; // 0: Low, 1: Moderate, 2: High
  risk_score: number; // 0-10
  category: "LOW" | "MODERATE" | "HIGH";
  probabilities: { low: number; moderate: number; high: number };
  recommendations: string[];
  monitoring_frequency: string;
}
```

---

## 💡 Implementation Tips
*   **Loading States**: AI responses typically take **2-4 seconds**. Implement shimmer effects or spinners.
*   **Language Support**: The backend is language-agnostic; it will respond to Darija, French, or English based on the input text.
*   **Error Codes**:
    *   `VALIDATION_ERROR`: Input vitals out of range.
    *   `EMBEDDING_ERROR`: Issue with the vector search engine.
    *   `GEMINI_ERROR`: LLM generation failure.
