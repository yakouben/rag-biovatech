# Supabase Environment Variables - Fixed ✅

## What Was Wrong
The project was using incorrect Supabase environment variable names:
- ❌ `SUPABASE_URL` → ✅ `NEXT_PUBLIC_SUPABASE_URL`
- ❌ `SUPABASE_KEY` → ✅ `NEXT_PUBLIC_SUPABASE_ANON_KEY`

The `NEXT_PUBLIC_` prefix is **required** for Next.js to expose variables to the browser.

---

## Changes Made

### 1. Created Supabase Client (`lib/supabase.ts`)
```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables...')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 2. Fixed API Routes
All three routes now import from the centralized client:

**app/api/rag/query/route.ts**
```typescript
import { supabase } from '@/lib/supabase'
// Now uses correct env vars
```

**app/api/glossary/search/route.ts**
```typescript
import { supabase } from '@/lib/supabase'
// Removed duplicate client initialization
```

**app/api/assessments/calculate/route.ts**
```typescript
import { supabase } from '@/lib/supabase'
// Uses centralized client
```

### 3. Updated `.env.example`
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 4. Created `ENV_SETUP.md`
- Complete setup instructions
- Common issues + fixes
- Deployment checklist

---

## Next Steps for You

1. **Local Development:**
   ```bash
   cp .env.example .env.local
   # Add your Supabase credentials
   npm run dev
   ```

2. **Verify It Works:**
   - Open browser console (F12)
   - Call API: `curl http://localhost:3000/api/glossary/search -X POST -d '{"query":"diabetes"}'`
   - Should return results from Supabase

3. **Deploy to Vercel:**
   - Go to Vercel Dashboard
   - Add same env variables
   - Redeploy

---

## Files Modified

✅ `lib/supabase.ts` - Created (new centralized client)
✅ `app/api/rag/query/route.ts` - Fixed imports
✅ `app/api/glossary/search/route.ts` - Fixed imports
✅ `app/api/assessments/calculate/route.ts` - Fixed imports
✅ `.env.example` - Updated variable names
✅ `ENV_SETUP.md` - Created (setup guide)

---

## Status

**Before**: ❌ Build would fail (missing env vars)
**After**: ✅ Ready to use (all env vars correct)

Your Next.js app will now properly connect to Supabase!
