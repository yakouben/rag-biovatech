# Environment Variables Setup

## Quick Start

1. Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```

2. Add your Supabase credentials from https://supabase.com:
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

3. Done! App will work immediately.

---

## Required Variables

### `NEXT_PUBLIC_SUPABASE_URL`
- **Required**: YES
- **Scope**: Frontend + API Routes
- **From**: Supabase Project Settings → API
- **Format**: `https://your-project.supabase.co`
- **Notes**: `NEXT_PUBLIC_` prefix makes it accessible in browser

### `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **Required**: YES
- **Scope**: Frontend + API Routes
- **From**: Supabase Project Settings → API
- **Format**: Long string (usually 100+ chars)
- **Security**: Public key, safe in frontend

---

## Optional Variables

### `SUPABASE_SERVICE_ROLE_KEY`
- **Required**: NO (only for admin operations)
- **Scope**: Backend/Server-side only
- **From**: Supabase Project Settings → API
- **Notes**: Keep secret, never expose in frontend

### `OPENAI_API_KEY`
- **Required**: NO
- **Format**: `sk-...`
- **Purpose**: AI responses (if using OpenAI)

### `ANTHROPIC_API_KEY`
- **Required**: NO
- **Format**: `sk-ant-...`
- **Purpose**: AI responses (if using Claude)

---

## Common Issues

### ❌ Error: "NEXT_PUBLIC_SUPABASE_URL is not defined"
**Fix**: Make sure `.env.local` exists and has `NEXT_PUBLIC_SUPABASE_URL` (with `NEXT_PUBLIC_` prefix)

### ❌ Error: "Failed to create Supabase client"
**Fix**: Check both variables are set:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### ❌ API calls fail with 401 errors
**Fix**: Verify the ANON_KEY is correct from Supabase dashboard

---

## Deployment to Vercel

1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add each variable:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. Redeploy

**Note**: Variables with `NEXT_PUBLIC_` prefix are visible in production (this is expected and safe).
