# CHAKER — Next.js Dashboard Checklist

## PHASE 1: Environment Setup
- [ ] Create `.env.local` with:
  - `OPENAI_API_KEY=...` (NO `NEXT_PUBLIC_` prefix)
  - `NEXT_PUBLIC_SUPABASE_URL=...`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY=...`
- [ ] Install dependencies:
  ```bash
  npm install @supabase/supabase-js @supabase/ssr openai recharts
  ```
- [ ] Get Supabase credentials from Seghir

---

## PHASE 2: Authentication
- [ ] Create `app/pages/login.tsx` or `app/login/page.tsx`:
  - [ ] Email + password form
  - [ ] Call `supabase.auth.signInWithPassword()`
  - [ ] After login: check `users.role`:
    - [ ] "doctor" → redirect to `/doctor/dashboard`
    - [ ] "family" → redirect to `/family/dashboard`
- [ ] Protect all `/doctor/*` routes:
  - [ ] Redirect to login if no session
  - [ ] Create middleware or layout check

---

## PHASE 3: Doctor Dashboard
- [ ] Create `app/doctor/dashboard/page.tsx`:
  - [ ] Fetch `GET /doctor/:id/patients` from Seghir's backend
  - [ ] Display patient cards in grid
  - [ ] Each card shows:
    - [ ] Patient name + age
    - [ ] Risk badge: GREEN (LOW) | ORANGE (MODERATE) | RED (HIGH)
    - [ ] Last check-in time
    - [ ] Unread alert count badge
  - [ ] Click card → navigate to `/doctor/patient/[id]`

---

## PHASE 4: Realtime Risk Badge
- [ ] On doctor dashboard, add Supabase Realtime subscription:
  ```typescript
  supabase
    .channel('risk-updates')
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'risk_scores',
      filter: `patient_id=in.(${patientIds.join(',')})`
    }, (payload) => {
      // Update patient's badge color live
    })
    .subscribe()
  ```
- [ ] When new risk_score inserted → patient badge updates live
- [ ] No polling — Realtime only

---

## PHASE 5: Patient Detail Page
- [ ] Create `app/doctor/patient/[id]/page.tsx`:

### Section 1: Patient Info
- [ ] Name, age, conditions, medications list

### Section 2: Risk Timeline
- [ ] Last 7 risk scores as colored blocks (GREEN/ORANGE/RED)
- [ ] Fetch from `GET /patient/:id/full`

### Section 3: Medication Adherence
- [ ] Show adherence % (number)
- [ ] Recharts bar chart (7-day history)

### Section 4: Conversations
- [ ] Last 5 Nour conversations (Darija text + timestamp)
- [ ] Displayed in list format

---

## PHASE 6: OpenAI Clinical Summary Button
- [ ] Add button on patient detail page: "Generate AI Summary"
- [ ] Create `app/api/summary/route.ts` (Next.js API route — server-side only):
  ```typescript
  // NEVER client-side
  import { openai } from '@/lib/openai'
  
  export async function POST(req: Request) {
    const { patient } = await req.json()
    
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{
        role: "user",
        content: `Patient: ${patient.name}, age ${patient.age}...
                  Write 3-sentence clinical summary in French.`
      }]
    })
    
    return Response.json({ summary: response.choices[0].message.content })
  }
  ```
- [ ] Button calls API endpoint
- [ ] Display summary in styled box
- [ ] Loading spinner while generating
- [ ] OPENAI_API_KEY never in client bundle

---

## PHASE 7: PDF Download
- [ ] Add button on patient detail page: "Download 30-day Report"
- [ ] Button calls: `POST /pdf/:patient_id` (Seghir's endpoint)
- [ ] Receives signed Supabase Storage URL
- [ ] Opens URL in new tab: `window.open(url)`
- [ ] Loading state on button while generating

---

## PHASE 8: Family Dashboard
- [ ] Create `app/family/dashboard/page.tsx`:
  - [ ] Show single patient (family's linked patient)
  - [ ] Large risk circle: GREEN / ORANGE / RED
  - [ ] Last check-in summary:
    - [ ] BP reading
    - [ ] Blood sugar
    - [ ] Wellbeing score
  - [ ] Live updates via Supabase Realtime on `risk_scores` table

---

## PHASE 9: Family Alerts Page
- [ ] Create `app/family/alerts/page.tsx`:
  - [ ] Fetch `GET /alerts/:patient_id` from backend
  - [ ] List alerts sorted by timestamp (newest first)
  - [ ] Each alert shows:
    - [ ] Message (in Darija)
    - [ ] Timestamp
    - [ ] Acknowledged status
  - [ ] "Mark as seen" button → `PATCH /alerts/:id/acknowledge`
  - [ ] Unread count badge in navigation

---

## PHASE 10: Test & Handoff
- [ ] Login works for doctor role → redirects to `/doctor/dashboard` ✅
- [ ] Dashboard loads patient list with correct risk badge colors ✅
- [ ] Risk badge updates live when new risk_score inserted ✅
- [ ] Patient detail page loads all 4 sections with data ✅
- [ ] OpenAI summary generates and displays in French ✅
- [ ] PDF download triggers (no error) ✅
- [ ] Family dashboard shows live risk circle ✅
- [ ] No OPENAI_API_KEY in browser network tab ✅
- [ ] No OPENAI_API_KEY in client bundle (check build output) ✅
- [ ] All pages protected (redirect to login if no auth) ✅

---

## Critical: Integration Loop
When complete, here's the full flow Seghir will test:
1. Doctor logs in → sees patient list
2. Risk badge shows initial risk
3. Seghir calls `/ai/chat` with patient data
4. System saves risk_score to DB
5. Chaker's dashboard badge turns RED live
6. Doctor clicks patient → sees full detail + summary
7. Doctor clicks "Download" → PDF downloads

If entire loop works: you're done.
