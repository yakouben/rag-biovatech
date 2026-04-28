-- =====================================================================
-- Migration: Fix schema inconsistencies + RAG / Supabase Auth integration
-- =====================================================================
-- Safe to run multiple times (idempotent where possible).
-- Run in Supabase SQL Editor (or via the v0 "Run script" button).
-- =====================================================================

-- 1. Required extensions ----------------------------------------------
create extension if not exists "pgcrypto";
create extension if not exists "vector";

-- =====================================================================
-- 2. Drop legacy columns / tables that had wrong types so we can recreate
--    them with correct uuid FKs. We keep the data tables themselves.
-- =====================================================================

-- Patients.id must be uuid and tied to auth.users.
-- If your existing patients table uses bigint, migrate it:
do $$
begin
  if exists (
    select 1 from information_schema.columns
    where table_name = 'patients' and column_name = 'id' and data_type = 'bigint'
  ) then
    -- Wipe FKs first so we can change the type cleanly
    alter table if exists consent_log                  drop column if exists patient_id;
    alter table if exists doctor_patient_relationships drop column if exists patient_id;
    alter table if exists family_members               drop column if exists patient_id;
    alter table if exists patient_assessments          drop column if exists patient_id;
    alter table if exists doctor_invite_codes          drop column if exists used_by_patient_id;

    alter table patients drop constraint if exists patients_pkey cascade;
    alter table patients alter column id drop default;
    alter table patients alter column id type uuid using gen_random_uuid();
    alter table patients add primary key (id);
  end if;
end$$;

-- =====================================================================
-- 3. Profiles (Supabase Auth bridge)
-- =====================================================================
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  role text not null default 'patient' check (role in ('patient','doctor','admin')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- =====================================================================
-- 4. Doctors / Patients core tables
-- =====================================================================
create table if not exists public.doctors (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  specialty text,
  license_number text unique,
  created_at timestamptz not null default now()
);

create table if not exists public.patients (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  date_of_birth date,
  sex text check (sex in ('male','female','other')),
  height_cm numeric,
  weight_kg numeric,
  -- BMI auto-updates whenever height/weight change
  bmi numeric generated always as (
    case when height_cm is null or height_cm = 0 or weight_kg is null
         then null
         else round((weight_kg / ((height_cm/100.0) * (height_cm/100.0)))::numeric, 2)
    end
  ) stored,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- =====================================================================
-- 5. Relational tables with proper uuid FKs
-- =====================================================================
create table if not exists public.doctor_patient_relationships (
  id uuid primary key default gen_random_uuid(),
  doctor_id  uuid not null references public.doctors(id)  on delete cascade,
  patient_id uuid not null references public.patients(id) on delete cascade,
  status text not null default 'active' check (status in ('active','pending','revoked')),
  created_at timestamptz not null default now(),
  unique (doctor_id, patient_id)
);

create table if not exists public.consent_log (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid not null references public.patients(id) on delete cascade,
  doctor_id  uuid          references public.doctors(id)  on delete set null,
  action text not null,
  details jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.family_members (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid not null references public.patients(id) on delete cascade,
  full_name text not null,
  relation text,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.patient_assessments (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid not null references public.patients(id) on delete cascade,
  doctor_id  uuid          references public.doctors(id)  on delete set null,
  summary text,
  data jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.doctor_invite_codes (
  id uuid primary key default gen_random_uuid(),
  doctor_id uuid not null references public.doctors(id) on delete cascade,
  code text not null unique,
  used_by_patient_id uuid references public.patients(id) on delete set null,
  used_at timestamptz,
  expires_at timestamptz,
  created_at timestamptz not null default now()
);

-- =====================================================================
-- 6. RAG: medical_glossary with proper vector + array types
--    Using 1536 dims (OpenAI text-embedding-3-small). Change if needed.
-- =====================================================================
create table if not exists public.medical_glossary (
  id uuid primary key default gen_random_uuid(),
  term text not null,
  definition text not null,
  related_terms text[] default '{}',
  embedding vector(1536),
  created_at timestamptz not null default now()
);

-- If the column already existed with a different type, normalize it
do $$
begin
  if exists (
    select 1 from information_schema.columns
    where table_name='medical_glossary' and column_name='related_terms' and data_type <> 'ARRAY'
  ) then
    alter table public.medical_glossary alter column related_terms type text[] using related_terms::text[];
  end if;
end$$;

create index if not exists medical_glossary_embedding_idx
  on public.medical_glossary
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists medical_glossary_term_idx
  on public.medical_glossary using gin (to_tsvector('simple', term));

-- =====================================================================
-- 7. RAG search function (cosine similarity)
-- =====================================================================
create or replace function public.match_medical_glossary(
  query_embedding vector(1536),
  match_threshold float default 0.78,
  match_count int default 5
)
returns table (
  id uuid,
  term text,
  definition text,
  related_terms text[],
  similarity float
)
language sql stable
as $$
  select g.id, g.term, g.definition, g.related_terms,
         1 - (g.embedding <=> query_embedding) as similarity
  from public.medical_glossary g
  where g.embedding is not null
    and 1 - (g.embedding <=> query_embedding) > match_threshold
  order by g.embedding <=> query_embedding
  limit match_count;
$$;

-- =====================================================================
-- 8. Auto-create profile on signup
-- =====================================================================
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, full_name, role)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'full_name', ''),
    coalesce(new.raw_user_meta_data->>'role', 'patient')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- =====================================================================
-- 9. Row Level Security
-- =====================================================================
alter table public.profiles                     enable row level security;
alter table public.doctors                      enable row level security;
alter table public.patients                     enable row level security;
alter table public.doctor_patient_relationships enable row level security;
alter table public.consent_log                  enable row level security;
alter table public.family_members               enable row level security;
alter table public.patient_assessments          enable row level security;
alter table public.doctor_invite_codes          enable row level security;
alter table public.medical_glossary             enable row level security;

-- Helper: is current user a doctor linked to this patient?
create or replace function public.is_doctor_of(p_patient uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.doctor_patient_relationships
    where doctor_id = auth.uid() and patient_id = p_patient and status = 'active'
  );
$$;

-- profiles: each user manages their own row
drop policy if exists "profiles self read"   on public.profiles;
drop policy if exists "profiles self write"  on public.profiles;
create policy "profiles self read"  on public.profiles for select using (id = auth.uid());
create policy "profiles self write" on public.profiles for update using (id = auth.uid());

-- patients: patient sees own row; linked doctor can read/update
drop policy if exists "patients self"           on public.patients;
drop policy if exists "patients doctor read"    on public.patients;
drop policy if exists "patients doctor update"  on public.patients;
create policy "patients self"          on public.patients for all    using (id = auth.uid()) with check (id = auth.uid());
create policy "patients doctor read"   on public.patients for select using (public.is_doctor_of(id));
create policy "patients doctor update" on public.patients for update using (public.is_doctor_of(id));

-- doctors: anyone authenticated can read; only self can update
drop policy if exists "doctors read"  on public.doctors;
drop policy if exists "doctors self"  on public.doctors;
create policy "doctors read" on public.doctors for select using (auth.role() = 'authenticated');
create policy "doctors self" on public.doctors for update using (id = auth.uid());

-- relationships: doctor or patient involved
drop policy if exists "rel read"   on public.doctor_patient_relationships;
drop policy if exists "rel insert" on public.doctor_patient_relationships;
create policy "rel read"   on public.doctor_patient_relationships for select using (doctor_id = auth.uid() or patient_id = auth.uid());
create policy "rel insert" on public.doctor_patient_relationships for insert with check (doctor_id = auth.uid() or patient_id = auth.uid());

-- consent / family / assessments: patient + linked doctor
drop policy if exists "consent rw"     on public.consent_log;
drop policy if exists "family rw"      on public.family_members;
drop policy if exists "assessment rw"  on public.patient_assessments;
create policy "consent rw"    on public.consent_log         for all using (patient_id = auth.uid() or public.is_doctor_of(patient_id));
create policy "family rw"     on public.family_members      for all using (patient_id = auth.uid() or public.is_doctor_of(patient_id));
create policy "assessment rw" on public.patient_assessments for all using (patient_id = auth.uid() or public.is_doctor_of(patient_id));

-- invite codes: doctor manages own; patient can read by code (handled via RPC ideally)
drop policy if exists "invite doctor"  on public.doctor_invite_codes;
create policy "invite doctor" on public.doctor_invite_codes for all using (doctor_id = auth.uid());

-- glossary: readable by any authenticated user; writes restricted to admins
drop policy if exists "glossary read"  on public.medical_glossary;
drop policy if exists "glossary admin" on public.medical_glossary;
create policy "glossary read"  on public.medical_glossary for select using (auth.role() = 'authenticated');
create policy "glossary admin" on public.medical_glossary for all
  using (exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'));
