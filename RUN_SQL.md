# How to Run the SQL Code

## Step 1: Go to Supabase Dashboard
https://supabase.com/dashboard

## Step 2: Select Your Project
Click on your ChronicCare project

## Step 3: Open SQL Editor
Left sidebar → SQL Editor → New Query

## Step 4: Copy SQL Code
Open: database_setup_clean.sql
Copy all the code

## Step 5: Paste & Run
Paste into the SQL Editor
Click RUN

## Step 6: Wait for Completion
Should complete in 30 seconds

## Step 7: Verify Tables Created
Go to: Table Editor
You should see:
- patients
- medical_glossary
- patient_assessments
- model_metrics

## What This SQL Creates
1. patients table - Patient records
2. medical_glossary table - 150+ Algerian medical terms
3. patient_assessments table - Risk assessments
4. model_metrics table - Model performance tracking
5. Indexes - For fast queries
6. RPC functions - For semantic search and data retrieval

## Next: Seed the Glossary
After tables are created, run:
python setup_db.py

## Then: Start the Server
python -m uvicorn app.main:app --reload --port 8000

Done!
