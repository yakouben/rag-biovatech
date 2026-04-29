# 🚀 HELA AI: React Native Master Specification (From Scratch)
> **Stack:** React Native (Expo or CLI) + Zustand + Axios + React Navigation + Expo Blur
> **Design Theme:** Blue Sky Glassmorphism (Premium UI)
> **Typography:** Urbanist (Main) | Amiri (Arabic/Darija)
> **Base URL:** `https://web-production-fadce.up.railway.app/api/v1`
> **Auth:** Header `X-Internal-Key: hela-secret-123`

---

## 🎨 1. THE VISION: "Blue Sky & Glass"
The UI must feel like a premium medical companion, not a cold hospital app. Every element should feel light, airy, and modern.

- **Design System:**
    - **Background:** Soft Sky Gradient (`#E0F7FA` to `#FFFFFF`).
    - **Glass Cards:** `BlurView` with 20% opacity.
    - **Typography:** Use **Urbanist** for all UI elements. Use **Amiri** for Darija/Arabic text with RTL support.
    - **Buttons:** Sky Blue gradients with sosoft shadows , and may be will the best one ever why noy

---

## 🏗️ 2. PROJECT STRUCTURE & STATE
- **Navigation:** `Stack.Navigator` for Auth/Activation flow, `BottomTab.Navigator` for main app (Home, Chat, History, Dictionary).
- **State Management:** Use **Zustand** for global state (Patient Profile, Chat History, Settings).
- **Storage:** Use `expo-secure-store` to persist the `patient_id` after activation.

---

## 🔌 3. API ENDPOINT MAPPING (Linking the AI)

### A. Activation Flow
- **Endpoint:** `GET /patient/{id}/profile`
- **Logic:** Patient scans QR code (extracts ID) or enters OTP. App fetches profile. If successful, save ID and redirect to Home.

### B. The Hela AI Chat (The "Brain")
- **Endpoint:** `POST /chat`
- **Body:** `{ "patient_id": "...", "patient_symptoms": "...", "include_glossary": true }`
- **UI Logic:**
    1. Show a pulsing glass bubble while `isLoading`.
    2. **The Thinker:** Map the `thinking_steps` array to a sequence of animated text messages (e.g., "Consulting medical database...", "Analyzing symptoms...").
    3. Display `hela_response` with RTL support.
    4. Append a `Risk Badge` (Red/Yellow/Green) based on `risk_score`.
    5. Show `glossary_context` as horizontal scrollable chips.

### C. Proactive Monitoring (The "Nurture")
- **Endpoint:** `GET /patient/{id}/check-drift`
- **Logic:** Call on app foreground. If `trigger_notification` is true, show the **Nurture Glass Card** on Home with the `nurture_message_darija`.

### D. Clinical History (Charts)
- **Endpoint:** `GET /patient/{id}/history?days=30`
- **UI:** Use `react-native-wagmi-charts` or `react-native-gifted-charts`.
    - Render BP (Systolic/Diastolic) and Glucose trends.
    - Glass-themed cards for each summary entry.

### E. Medical Dictionary
- **Endpoint:** `POST /glossary/search`
- **Logic:** Real-time search in Darija/French/English. Display results in RTL cards.

---

## 📱 4. SCREEN-BY-SCREEN REQUIREMENTS

### Screen 1: Activation
- Minimalist sky background. Large "Scan Doctor's QR" button with glass effect.

### Screen 2: Home (Dashboard)
- Greeting: "Marhba, [Name]!" (Urbanist Bold).
- **Nurture Alert:** Floating glass card for AI check-ins.
- **Quick Metrics:** BP and Glucose summary tiles.

### Screen 3: Chat with Hela
- Full-screen chat interface.
- **The Thinking Bubble:** Pulsing animation with real-time `thinking_steps` text.
- Voice-to-Text: Integration for patients who prefer speaking Darija.

### Screen 4: Medical History
- Interactive charts. Filter for 7/14/30/90 days.
- List of previous clinical assessments.

### Screen 5: Profile & Reports
- Button: "Download PDF Report" -> Calls `POST /reports/generate`.
- Patient metadata display.

---

## 🛠️ 5. DEVELOPER INSTRUCTIONS
1. **Style with Emotion:** Every transition should be smooth (300ms).
2. **Prouve le RAG:** N'oublie jamais d'afficher les `thinking_steps`. C'est ce qui prouve à l'utilisateur que l'IA travaille vraiment sur ses données médicales.
3. **Accessibilité :** Taille de police minimum 18px pour les patients âgés.
4. **RTL Native :** Assure-toi que les textes en Darija s'affichent correctement de droite à gauche.
