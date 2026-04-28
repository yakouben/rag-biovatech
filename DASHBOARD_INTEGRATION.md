# 💻 ChronicCare: Dashboard Integration Guide
**Target:** Doctor & Clinic Web Dashboard (Next.js)
**Backend URL:** `https://web-production-fadce.up.railway.app`

## 🧠 The Integration Prompt
*Copy and paste this into your AI coding assistant (Cursor/Gemini/Claude):*

> "You are a Lead Frontend Engineer specialized in Next.js, Tailwind CSS, and Shadcn/UI. We are building the **ChronicCare Doctor Dashboard**.
> 
> **Core Features to Implement:**
> 1. **Clinical AI Chat:** A sidebar component that uses `POST /doctor/chat`. It allows the doctor to ask clinical questions about a specific patient. The AI will perform RAG (Retrieval-Augmented Generation) over the patient's entire history.
> 2. **Patient Health Timeline:** Fetch historical assessments using `GET /api/v1/patient/{id}/history` and visualize trends in Blood Pressure and Glucose using `recharts`. Highlight data points where the `risk_score` was 'HIGH'.
> 3. **Report Generator:** A button that calls `POST /api/v1/reports/generate`. It must pass `patient_id`, `patient_name`, and `adherence_days` (default 30). Handle the binary response to allow the doctor to save/view the PDF.
> 4. **Risk Queue:** A main dashboard table that sorts patients by their latest `risk_score`. High-risk patients must have a 'Red' status indicator.
> 5. **Security:** Secure all requests with the `X-Internal-Key` header. Ensure the UI feels professional, clinical, and fast."

## 🔗 Required Endpoints

### 1. Doctor-Chat (RAG over History)
- **Endpoint:** `POST /doctor/chat`
- **Payload:**
  ```json
  {
    "patient_id": "p123",
    "question": "What has been the trend of her blood pressure over the last two weeks?"
  }
  ```

### 2. Patient Clinical History (for Trends)
- **Endpoint:** `GET /api/v1/patient/{id}/history?days=30`
- **Returns:** Chronological array of vitals, risk scores, and summaries for `recharts`.

### 3. Clinical PDF Report
- **Endpoint:** `POST /api/v1/reports/generate?patient_id=p123&patient_name=Fatma_B&adherence_days=30`
- **Payload:** (Standard patient health data)
- **Returns:** Binary PDF stream.

## 🎨 UI/UX Requirements
- **Command Center:** The doctor should see everything at a glance. Use a clean, "Apple-Health" style aesthetic.
- **Contextual Data:** When the doctor is chatting with the AI, show the relevant "extracted_entities" (symptoms/meds) for that patient in the same view.
