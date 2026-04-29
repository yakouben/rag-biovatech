# ChronicCare Patient App - Implementation Quick Start Guide

## 📁 Documentation Files Generated

Your frontend developer has **3 comprehensive documents** to work from:

### 1. **PATIENT_APP_DEVELOPER_SPECIFICATION.md** (825 lines)
   - Complete vision & user journeys
   - Technology stack (Next.js 16, TypeScript, Tailwind, Recharts)
   - Full database schema documentation
   - All 9 API endpoints with request/response examples
   - 5+ key component specifications (Dashboard, Vitals Form, Charts, etc.)
   - Design system (Urbanist font, sky blue, glassmorphism)
   - Complete 6-phase implementation roadmap
   - Testing checklist & deployment guide

### 2. **PATIENT_APP_API_CHEATSHEET.md** (392 lines)
   - Quick curl examples for all API endpoints
   - Production URL: `https://web-production-fadce.up.railway.app/api/v1`
   - Real request/response payloads for copy-paste
   - TypeScript API client example code
   - SWR hook patterns
   - Error handling reference
   - Notes on units (mg/dL, mmHg, kg/m², etc.)

### 3. **PATIENT_APP_TYPES.ts** (470 lines)
   - Ready-to-copy TypeScript interfaces
   - Complete type definitions for all API responses
   - React component prop types
   - Form input types with Zod validation schemas
   - State management types
   - Copy directly into `lib/types/index.ts`

---

## 🚀 Quick Start: 5 Steps to Begin

### Step 1: Create Next.js 16 Project
```bash
npx create-next-app@latest patient-app --typescript --tailwind
cd patient-app
npm install axios swr react-hook-form zod recharts
```

### Step 2: Copy Types File
- Copy `PATIENT_APP_TYPES.ts` → `lib/types/index.ts`
- Setup file structure matching the spec

### Step 3: Create API Client
```typescript
// lib/api-client.ts
import axios from 'axios';

const API_BASE_URL = 'https://web-production-fadce.up.railway.app/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Add JWT token interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Step 4: Create Auth Context
```typescript
// contexts/AuthContext.tsx
import { createContext, useContext, useState, ReactNode } from 'react';
import { PatientProfile } from '@/lib/types';

interface AuthContextType {
  patient: PatientProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (phone: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [patient, setPatient] = useState<PatientProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);

  return (
    <AuthContext.Provider value={{ patient, token, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

### Step 5: Build First Component
```typescript
// components/dashboard/VitalsCard.tsx
import { HealthTrendDataPoint, VitalsCardProps } from '@/lib/types';

export default function VitalsCard({ vitals, previous_vitals }: VitalsCardProps) {
  return (
    <div className="rounded-xl bg-gradient-to-br from-sky-100 to-white 
                    backdrop-blur-xl border border-sky-200 p-6 shadow-lg">
      <h3 className="text-lg font-bold text-gray-800 mb-4 font-urbanist">
        Blood Pressure
      </h3>
      
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-sky-600">
          {vitals.systolic}/{vitals.diastolic}
        </span>
        <span className="text-sm text-gray-600">mmHg</span>
      </div>

      {previous_vitals && (
        <p className="text-sm text-gray-500 mt-2">
          Previous: {previous_vitals.systolic}/{previous_vitals.diastolic}
        </p>
      )}
    </div>
  );
}
```

---

## 🎨 Design System Quick Reference

### Glassmorphism Template
```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.glass-card-primary {
  background: rgba(14, 165, 233, 0.1); /* Sky blue tint */
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.2);
}
```

### Colors
- **Primary**: `#0ea5e9` (sky-500)
- **Background**: `#ffffff` (white)
- **Surface**: `#f1f5f9` (slate-100)
- **Text**: `#0f172a` (slate-900)

### Font
```typescript
// next.config.js
const { withUmami } = require('@umami/next');

module.exports = withUmami({
  webpack(config) {
    config.module.rules.push({
      test: /\.(woff|woff2|eot|ttf|otf)$/,
      use: [
        {
          loader: 'file-loader',
          options: {
            publicPath: '/_next/static/fonts/',
            outputPath: `${isServer ? '../' : ''}static/fonts/`,
            name: '[name].[hash].[ext]',
          },
        },
      ],
    });
    return config;
  },
});

// tailwind.config.js
module.exports = {
  theme: {
    fontFamily: {
      urbanist: ['Urbanist', 'sans-serif'],
    },
  },
};
```

---

## 📊 API Integration Patterns

### SWR Hook for Patient Data
```typescript
// hooks/usePatient.ts
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import { PatientProfile } from '@/lib/types';

export function usePatient(patientId: string) {
  const { data, error, isLoading, mutate } = useSWR<PatientProfile>(
    patientId ? `/patient/${patientId}/profile` : null,
    (url) => apiClient.get(url).then((res) => res.data),
    {
      revalidateOnFocus: false,
      revalidateInterval: 60000, // Refetch every 60 seconds
    }
  );

  return {
    patient: data,
    isLoading,
    isError: !!error,
    mutate,
  };
}
```

### Submitting Vitals + AI Chat
```typescript
// hooks/useAIChat.ts
import { useState } from 'react';
import apiClient from '@/lib/api-client';
import { AIChartRequest, AIChartResponse, PatientVitals } from '@/lib/types';

export function useAIChat() {
  const [response, setResponse] = useState<AIChartResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (patientId: string, symptoms: string, vitals: PatientVitals) => {
    setIsLoading(true);
    setError(null);

    try {
      const payload: AIChartRequest = {
        patient_id: patientId,
        patient_symptoms: symptoms,
        include_glossary: true,
        patient_data: vitals,
      };

      const res = await apiClient.post<AIChartResponse>('/chat', payload);
      setResponse(res.data);
      return res.data;
    } catch (err: any) {
      const message = err.response?.data?.message || 'Failed to get AI response';
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return { response, isLoading, error, submit };
}
```

### Fetching History for Charts
```typescript
// hooks/usePatientHistory.ts
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import { PatientHistoryResponse } from '@/lib/types';

export function usePatientHistory(patientId: string, days: number = 30) {
  const { data, error, isLoading, mutate } = useSWR<PatientHistoryResponse>(
    patientId ? `/patient/${patientId}/history?days=${days}` : null,
    (url) => apiClient.get(url).then((res) => res.data),
    { revalidateInterval: 30000 }
  );

  return {
    history: data?.history || [],
    count: data?.count || 0,
    isLoading,
    isError: !!error,
    mutate,
  };
}
```

---

## 🔐 Environment Setup

Create `.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=https://web-production-fadce.up.railway.app/api/v1
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_APP_VERSION=1.0.0
```

---

## 📱 Page Structure

```
/                          → Redirect to /auth/login
/auth/login                → Patient login form
/auth/register             → Patient registration
/auth/onboard              → Health profile setup
/dashboard                 → Main dashboard
/dashboard/vitals-input    → Log daily vitals
/dashboard/history         → View trend graphs
/dashboard/reports         → Generate/view reports
/glossary                  → Medical dictionary search
/settings                  → Patient account settings
```

---

## ✅ Implementation Checklist

### Phase 1 (Week 1): Setup
- [ ] Create Next.js 16 project with TypeScript
- [ ] Copy types file to `lib/types/index.ts`
- [ ] Setup Tailwind CSS + Urbanist font
- [ ] Create API client with JWT interceptor
- [ ] Create AuthContext + authentication flow
- [ ] Build login/register/onboard pages

### Phase 2 (Week 2): Dashboard
- [ ] Create dashboard page layout
- [ ] Build VitalsCard, RiskGauge, AIInsights components
- [ ] Setup SWR hooks for data fetching
- [ ] Create Navigation & Header components
- [ ] Mobile responsive design

### Phase 3 (Week 2-3): Vitals Tracking
- [ ] Create VitalsForm with validation (Zod)
- [ ] Integrate `/chat` endpoint
- [ ] Display AI response in modal
- [ ] Save form data + refresh UI
- [ ] Error handling & loading states

### Phase 4 (Week 3): Charts
- [ ] Install & integrate Recharts
- [ ] Create GlucoseTrendChart
- [ ] Create BPTrendChart
- [ ] Create RiskScoreTrendChart
- [ ] Date range filter
- [ ] CSV export

### Phase 5 (Week 4): Advanced
- [ ] Glossary search page
- [ ] PDF report generation/download
- [ ] Doctor message history (if available)
- [ ] Family access features
- [ ] Settings/profile page

### Phase 6 (Week 4-5): Testing & Deploy
- [ ] Unit tests (Jest)
- [ ] E2E tests (Cypress)
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] Production build & deployment

---

## 🐛 Common Issues & Solutions

### Issue: "401 Unauthorized on API calls"
**Solution**: Check JWT token in localStorage, re-login if expired

### Issue: "CORS errors"
**Solution**: Already handled by backend, ensure correct base URL

### Issue: "Chart not showing data"
**Solution**: Verify API response format matches `HealthTrendDataPoint[]`

### Issue: "Form submission fails"
**Solution**: Check Zod validation schema matches form fields

---

## 📚 Additional Resources

- **Next.js 16 Docs**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Recharts**: https://recharts.org/
- **SWR**: https://swr.vercel.app/
- **Zod Validation**: https://zod.dev/

---

## 🤝 Support

**API Questions**: Refer to `PATIENT_APP_API_CHEATSHEET.md`  
**Type Definitions**: Refer to `PATIENT_APP_TYPES.ts`  
**Architecture**: Refer to `PATIENT_APP_DEVELOPER_SPECIFICATION.md`

---

**Status**: Ready for Development  
**API Base URL**: `https://web-production-fadce.up.railway.app/api/v1`  
**Last Updated**: January 2024
