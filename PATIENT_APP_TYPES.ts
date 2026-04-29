/**
 * ChronicCare Patient App - TypeScript Type Definitions
 * Copy this file directly into your project at: lib/types/index.ts
 * Production API: https://web-production-fadce.up.railway.app/api/v1
 */

// ============================================================================
// Patient & Profile Types
// ============================================================================

export interface PatientProfile {
  id: string; // UUID
  name: string;
  age: number; // 0-150
  gender: "M" | "F" | "Other";
  phone?: string;
  address?: string;
  date_of_birth?: string; // ISO format: YYYY-MM-DD
  family_contact_name?: string;
  family_contact_phone?: string;
  family_access_granted?: boolean;
  previous_clinic_id?: string; // For migration tracking
  medical_history_summary?: string;
  created_at: string; // ISO8601
  updated_at: string; // ISO8601
}

export interface PatientOnboardingRequest {
  is_import: boolean;
  profile: Omit<PatientProfile, "id" | "created_at" | "updated_at">;
  initial_vitals?: PatientVitals;
}

export interface PatientOnboardingResponse {
  patient_id: string;
  status: "success" | "error";
  message: string;
  initial_risk?: RiskAssessmentResponse;
  ai_analysis?: string;
}

// ============================================================================
// Vitals & Health Metrics
// ============================================================================

export interface PatientVitals {
  age: number; // 0-150 years
  systolic_bp: number; // 60-250 mmHg
  diastolic_bp: number; // 30-150 mmHg
  fasting_glucose: number; // 40-500 mg/dL
  bmi: number; // 10-60 kg/m²
  weight?: number; // kg
  height?: number; // cm
  smoking: boolean;
  family_history: boolean;
  comorbidities: number; // 0-10 conditions
}

export interface VitalsRecord extends PatientVitals {
  id: string;
  patient_id: string;
  recorded_at: string; // ISO8601
  created_at: string; // ISO8601
}

export interface HealthTrendDataPoint {
  date: string; // ISO8601
  risk: number; // Risk score 0-10
  systolic?: number; // mmHg
  diastolic?: number; // mmHg
  glucose?: number; // mg/dL
  summary?: string;
}

export interface PatientHistoryResponse {
  patient_id: string;
  count: number;
  history: HealthTrendDataPoint[];
}

// ============================================================================
// Clinical Assessment & Risk
// ============================================================================

export interface ClinicalEntities {
  symptoms: string[];
  medications: string[];
  missed_medications: string[];
  vitals: Record<string, number | undefined>;
  severity_hints: string[];
  clinical_note: string;
}

export interface PatientAssessment {
  id: string;
  patient_id: string;
  assessment_date: string; // ISO8601
  symptoms: string;
  predicted_risk_level: 0 | 1 | 2; // 0=LOW, 1=MODERATE, 2=HIGH
  actual_risk_level?: 0 | 1 | 2;
  risk_score: number; // 0-10
  confidence: number; // 0-1
  is_correct?: boolean;
  glossary_terms_used: string[];
  clinical_entities: ClinicalEntities;
  created_at: string; // ISO8601
}

export interface RiskAssessmentRequest {
  patient_data: PatientVitals;
  patient_symptoms?: string;
}

export interface RiskAssessmentResponse {
  risk_level: 0 | 1 | 2; // 0=LOW, 1=MODERATE, 2=HIGH
  risk_score: number; // 0-10
  category: "LOW" | "MODERATE" | "HIGH";
  probabilities: {
    low: number; // 0-1
    moderate: number; // 0-1
    high: number; // 0-1
  };
  recommendations: string[];
  monitoring_frequency: string; // e.g., "Every 3-6 months"
}

// ============================================================================
// AI Chat & NOUR Response
// ============================================================================

export interface AIChartRequest {
  patient_id: string;
  patient_symptoms: string; // Can be in Darija, French, or English
  include_glossary?: boolean; // Default: true
  patient_data?: PatientVitals;
}

export interface AIChartResponse {
  hela_response: string; // Clinical response (may be in Darija)
  extracted_entities: ClinicalEntities;
  risk_score: "LOW" | "MODERATE" | "HIGH";
  confidence: number; // 0-1
  factors: string[];
  monitoring_frequency: string;
  glossary_context: GlossaryEntry[];
}

export interface NOURRequest extends AIChartRequest {}

export interface NOURResponse {
  clinical_assessment: string;
  risk_assessment: RiskAssessmentResponse;
  recommendations: string[];
  extracted_entities: ClinicalEntities;
  glossary_context: GlossaryEntry[];
}

// ============================================================================
// Medical Glossary
// ============================================================================

export interface GlossaryEntry {
  id?: number;
  darija: string; // Arabic/Darija term
  french: string; // French translation
  english: string; // English translation
  category: string; // e.g., "endocrine", "cardiovascular", "respiratory"
  embedding?: number[]; // 768-dimensional vector (backend only)
}

export interface GlossarySearchRequest {
  query: string; // Search term (min 1, max 200 chars)
  limit?: number; // 1-100, default 10
  language?: "french" | "english" | "darija"; // Default "french"
}

export interface GlossarySearchResponse extends Array<GlossaryEntry> {}

// ============================================================================
// Doctor Communication & Monitoring
// ============================================================================

export interface DoctorChatRequest {
  patient_id: string;
  question: string; // Doctor's clinical question
  include_raw_history?: boolean; // Default false
}

export interface DoctorChatResponse {
  answer: string;
  patient_id: string;
  history_analyzed: number; // Number of records reviewed
  raw_history?: PatientAssessment[];
}

export interface AdherenceDriftResponse {
  patient_id: string;
  adherence_drop_detected: boolean;
  adherence_score_previous: number; // 0-1
  adherence_score_current: number; // 0-1
  nurture_message: string;
  recommendations: string[];
}

// ============================================================================
// Reports
// ============================================================================

export interface ReportGenerationRequest {
  patient_id: string;
  patient_name: string;
  adherence_days?: number; // 7-90, default 30
}

// Response is a PDF file (binary Blob)
export type ReportGenerationResponse = Blob;

// ============================================================================
// API Responses
// ============================================================================

export interface HealthCheckResponse {
  status: "healthy" | "degraded" | "unhealthy";
  version: string; // e.g., "1.0.0"
  timestamp: string; // ISO8601
  services: {
    database: string;
    gemini: string;
    model: string;
    environment: "development" | "staging" | "production";
  };
}

export interface ErrorResponse {
  status_code: number; // HTTP status
  error_code: string; // e.g., "VALIDATION_ERROR"
  message: string;
  details?: Record<string, any>;
  timestamp: string; // ISO8601
}

// ============================================================================
// Authentication
// ============================================================================

export interface AuthToken {
  access_token: string;
  token_type: "bearer";
  expires_in?: number; // Seconds
}

export interface LoginRequest {
  phone: string; // +212...
  password: string;
}

export interface RegisterRequest {
  phone: string;
  password: string;
  name: string;
  age: number;
}

// ============================================================================
// Form Input Types (Client-side Validation)
// ============================================================================

export interface VitalsFormInput {
  systolic_bp: number;
  diastolic_bp: number;
  fasting_glucose: number;
  weight?: number;
  height?: number;
  symptoms: string; // Free-form text
}

export interface ProfileFormInput {
  name: string;
  age: number;
  gender: "M" | "F" | "Other";
  phone: string;
  address: string;
  date_of_birth: string; // YYYY-MM-DD
  family_contact_name?: string;
  family_contact_phone?: string;
}

// ============================================================================
// Chart & Visualization Data
// ============================================================================

export interface GlucoseTrendData {
  date: string;
  glucose: number; // mg/dL
  is_fasting: boolean;
  notes?: string;
}

export interface BPTrendData {
  date: string;
  systolic: number; // mmHg
  diastolic: number; // mmHg
  notes?: string;
}

export interface RiskScoreTrendData {
  date: string;
  score: number; // 0-10
  category: "LOW" | "MODERATE" | "HIGH";
}

export interface AdherenceTrendData {
  week: string; // ISO week
  adherence_rate: number; // 0-1 (0% to 100%)
  days_logged: number;
  days_expected: number;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface DashboardProps {
  patient: PatientProfile;
  latestVitals: HealthTrendDataPoint | null;
  latestAssessment: PatientAssessment | null;
}

export interface VitalsCardProps {
  vitals: HealthTrendDataPoint;
  previous_vitals?: HealthTrendDataPoint;
}

export interface RiskGaugeProps {
  risk_score: number; // 0-10
  risk_category: "LOW" | "MODERATE" | "HIGH";
  confidence: number; // 0-1
}

export interface AIInsightsCardProps {
  assessment: PatientAssessment;
  glossary: GlossaryEntry[];
}

// ============================================================================
// State Management Types
// ============================================================================

export interface AuthContextState {
  isAuthenticated: boolean;
  patient: PatientProfile | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

export interface PatientContextState {
  patient: PatientProfile | null;
  vitals: HealthTrendDataPoint[];
  assessments: PatientAssessment[];
  loading: boolean;
  error: string | null;
}

// ============================================================================
// Hook Return Types (SWR)
// ============================================================================

export interface UsePatientReturn {
  patient: PatientProfile | undefined;
  isLoading: boolean;
  isError: boolean;
  mutate: () => void;
}

export interface UseVitalsReturn {
  vitals: HealthTrendDataPoint[];
  history: HealthTrendDataPoint[];
  isLoading: boolean;
  isError: boolean;
  submit: (vitals: VitalsFormInput) => Promise<AIChartResponse>;
  mutate: () => void;
}

export interface UseAIChatReturn {
  response: AIChartResponse | null;
  isLoading: boolean;
  error: string | null;
  submit: (symptoms: string, vitals: PatientVitals) => Promise<AIChartResponse>;
}

// ============================================================================
// Utility Types
// ============================================================================

export type RiskLevel = "LOW" | "MODERATE" | "HIGH";
export type RiskCategory = 0 | 1 | 2;

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface DateRangeFilter {
  start_date?: string; // ISO8601
  end_date?: string; // ISO8601
  days?: number; // Alternative: 7, 30, 60, 90
}

// ============================================================================
// Zod Validation Schemas (for client-side validation)
// ============================================================================

import { z } from "zod";

export const PatientVitalsSchema = z.object({
  age: z.number().min(0).max(150),
  systolic_bp: z.number().min(60).max(250),
  diastolic_bp: z.number().min(30).max(150),
  fasting_glucose: z.number().min(40).max(500),
  bmi: z.number().min(10).max(60),
  weight: z.number().optional(),
  height: z.number().optional(),
  smoking: z.boolean(),
  family_history: z.boolean(),
  comorbidities: z.number().min(0).max(10),
});

export const VitalsFormSchema = z.object({
  systolic_bp: z.number().min(60).max(250, "Systolic BP must be 60-250"),
  diastolic_bp: z.number().min(30).max(150, "Diastolic BP must be 30-150"),
  fasting_glucose: z.number().min(40).max(500, "Glucose must be 40-500"),
  weight: z.number().optional(),
  height: z.number().optional(),
  symptoms: z.string().min(5, "Please describe symptoms (min 5 chars)"),
});

export const ProfileFormSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  age: z.number().min(0).max(150),
  gender: z.enum(["M", "F", "Other"]),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, "Invalid phone number"),
  address: z.string().min(5),
  date_of_birth: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Format: YYYY-MM-DD"),
  family_contact_name: z.string().optional(),
  family_contact_phone: z.string().optional(),
});

// ============================================================================
// API Client Types
// ============================================================================

export interface APIClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface APIResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedAPIResponse<T> extends APIResponse<T[]> {
  total: number;
  skip: number;
  limit: number;
}
