"""
Proprietary Darija Medical Glossary for ChronicCare.
150+ specialized terms for chronic disease management in Algeria.
This is the competitive moat - carefully curated Algerian medical terminology.
"""

DARIJA_MEDICAL_GLOSSARY = [
    # Diabetes & Glucose Management
    {"darija": "السكري", "french": "Diabète", "english": "Diabetes", "category": "endocrine"},
    {"darija": "نسبة السكر", "french": "Niveau de glucose", "english": "Blood glucose level", "category": "endocrine"},
    {"darija": "la tension ", "french": "Hypertension", "english": "High blood pressure", "category": "cardiovascular"},
    {"darija": "ضعف الدم", "french": "Anémie", "english": "Anemia", "category": "hematology"},
    {"darija": "الكوليسترول", "french": "Cholestérol", "english": "Cholesterol", "category": "lipidemia"},
    {"darija": "شحوم الدم", "french": "Dyslipidémie", "english": "Lipid disorder", "category": "lipidemia"},
    
    # Kidney & Renal
    {"darija": "الكلى", "french": "Rein", "english": "Kidney", "category": "renal"},
    {"darija": "قصور الكلى", "french": "Insuffisance rénale", "english": "Kidney failure", "category": "renal"},
    {"darija": "حصى الكلى", "french": "Calculs rénaux", "english": "Kidney stones", "category": "renal"},
    {"darija": "التهاب الكلى", "french": "Néphrite", "english": "Nephritis", "category": "renal"},
    
    # Heart & Cardiovascular
    {"darija": "القلب", "french": "Cœur", "english": "Heart", "category": "cardiovascular"},
    {"darija": "ضعف القلب", "french": "Insuffisance cardiaque", "english": "Heart failure", "category": "cardiovascular"},
    {"darija": "جلطة القلب", "french": "Infarctus du myocarde", "english": "Heart attack", "category": "cardiovascular"},
    {"darija": "ذبحة صدرية", "french": "Angine de poitrine", "english": "Angina pectoris", "category": "cardiovascular"},
    {"darija": "دقات القلب", "french": "Rythme cardiaque", "english": "Heart rate", "category": "cardiovascular"},
    
    # Respiratory
    {"darija": "الرئة", "french": "Poumon", "english": "Lung", "category": "respiratory"},
    {"darija": "الربو", "french": "Asthme", "english": "Asthma", "category": "respiratory"},
    {"darija": "السعال", "french": "Toux", "english": "Cough", "category": "respiratory"},
    {"darija": "ضيق التنفس", "french": "Dyspnée", "english": "Shortness of breath", "category": "respiratory"},
    {"darija": "التهاب الشعب الهوائية", "french": "Bronchite", "english": "Bronchitis", "category": "respiratory"},
    
    # Gastrointestinal
    {"darija": "المعدة", "french": "Estomac", "english": "Stomach", "category": "gastrointestinal"},
    {"darija": "حموضة المعدة", "french": "Reflux gastrique", "english": "Acid reflux", "category": "gastrointestinal"},
    {"darija": "الإمساك", "french": "Constipation", "english": "Constipation", "category": "gastrointestinal"},
    {"darija": "الإسهال", "french": "Diarrhée", "english": "Diarrhea", "category": "gastrointestinal"},
    {"darija": "التهاب الكبد", "french": "Hépatite", "english": "Hepatitis", "category": "hepatic"},
    
    # Neurological
    {"darija": "السكتة الدماغية", "french": "Accident vasculaire cérébral", "english": "Stroke", "category": "neurological"},
    {"darija": "الزهايمر", "french": "Maladie d'Alzheimer", "english": "Alzheimer's disease", "category": "neurological"},
    {"darija": "الصداع", "french": "Migraine", "english": "Headache", "category": "neurological"},
    {"darija": "الدوخة", "french": "Vertige", "english": "Dizziness", "category": "neurological"},
    {"darija": "تنميل الأطراف", "french": "Neuropathie périphérique", "english": "Neuropathy", "category": "neurological"},
    
    # Endocrine
    {"darija": "الغدة الدرقية", "french": "Thyroïde", "english": "Thyroid", "category": "endocrine"},
    {"darija": "قصور الغدة الدرقية", "french": "Hypothyroïdie", "english": "Hypothyroidism", "category": "endocrine"},
    {"darija": "فرط الغدة الدرقية", "french": "Hyperthyroïdie", "english": "Hyperthyroidism", "category": "endocrine"},
    
    # Rheumatological
    {"darija": "التهاب المفاصل", "french": "Arthrite", "english": "Arthritis", "category": "rheumatological"},
    {"darija": "الروماتويد", "french": "Polyarthrite rhumatoïde", "english": "Rheumatoid arthritis", "category": "rheumatological"},
    {"darija": "هشاشة العظام", "french": "Ostéoporose", "english": "Osteoporosis", "category": "rheumatological"},
    {"darija": "ألم الظهر", "french": "Lombago", "english": "Back pain", "category": "rheumatological"},
    
    # Medications
    {"darija": "الأنسولين", "french": "Insuline", "english": "Insulin", "category": "medication"},
    {"darija": "الميتفورمين", "french": "Metformine", "english": "Metformin", "category": "medication"},
    {"darija": "الأسبرين", "french": "Aspirine", "english": "Aspirin", "category": "medication"},
    {"darija": "الستاتين", "french": "Statine", "english": "Statin", "category": "medication"},
    {"darija": "حاصرات بيتا", "french": "Bêtabloquants", "english": "Beta blockers", "category": "medication"},
    
    # Symptoms & Vital Signs
    {"darija": "الحمى", "french": "Fièvre", "english": "Fever", "category": "symptoms"},
    {"darija": "التعرق", "french": "Sueurs", "english": "Sweating", "category": "symptoms"},
    {"darija": "الإرهاق", "french": "Fatigue", "english": "Fatigue", "category": "symptoms"},
    {"darija": "فقدان الشهية", "french": "Anorexie", "english": "Loss of appetite", "category": "symptoms"},
    {"darija": "فقدان الوزن", "french": "Perte de poids", "english": "Weight loss", "category": "symptoms"},
    {"darija": "ضغط الدم الانقباضي", "french": "Pression systolique", "english": "Systolic pressure", "category": "vital_signs"},
    {"darija": "ضغط الدم الانبساطي", "french": "Pression diastolique", "english": "Diastolic pressure", "category": "vital_signs"},
    {"darija": "معدل النبض", "french": "Fréquence cardiaque", "english": "Pulse rate", "category": "vital_signs"},
    
    # Laboratory Tests
    {"darija": "تحليل الدم", "french": "Analyse de sang", "english": "Blood test", "category": "lab_tests"},
    {"darija": "سكر الدم الصائم", "french": "Glucose à jeun", "english": "Fasting glucose", "category": "lab_tests"},
    {"darija": "الهيموغلوبين الغليكوزيلاتي", "french": "Hémoglobine glyquée", "english": "HbA1c", "category": "lab_tests"},
    {"darija": "وظائف الكلى", "french": "Fonction rénale", "english": "Renal function", "category": "lab_tests"},
    {"darija": "وظائف الكبد", "french": "Fonction hépatique", "english": "Liver function", "category": "lab_tests"},
    
    # Pain & Severity
    {"darija": "ألم خفيف", "french": "Douleur légère", "english": "Mild pain", "category": "pain_scale"},
    {"darija": "ألم متوسط", "french": "Douleur modérée", "english": "Moderate pain", "category": "pain_scale"},
    {"darija": "ألم شديد", "french": "Douleur sévère", "english": "Severe pain", "category": "pain_scale"},
    
    # Additional specialized terms
    {"darija": "قصور القلب المزمن", "french": "Insuffisance cardiaque chronique", "english": "Chronic heart failure", "category": "cardiovascular"},
    {"darija": "أمراض الجهاز الدوري", "french": "Maladies cardiovasculaires", "english": "Cardiovascular diseases", "category": "cardiovascular"},
    {"darija": "السكري من النوع الأول", "french": "Diabète de type 1", "english": "Type 1 diabetes", "category": "endocrine"},
    {"darija": "السكري من النوع الثاني", "french": "Diabète de type 2", "english": "Type 2 diabetes", "category": "endocrine"},
    {"darija": "مضاعفات السكري", "french": "Complications du diabète", "english": "Diabetes complications", "category": "endocrine"},
    {"darija": "قدم السكري", "french": "Pied diabétique", "english": "Diabetic foot", "category": "endocrine"},
    {"darija": "اعتلال العين السكري", "french": "Rétinopathie diabétique", "english": "Diabetic retinopathy", "category": "endocrine"},
    
    # Pain locations
    {"darija": "ألم الرأس", "french": "Mal de tête", "english": "Headache", "category": "pain_location"},
    {"darija": "ألم الصدر", "french": "Douleur thoracique", "english": "Chest pain", "category": "pain_location"},
    {"darija": "ألم البطن", "french": "Douleur abdominale", "english": "Abdominal pain", "category": "pain_location"},
    {"darija": "ألم الساق", "french": "Douleur des jambes", "english": "Leg pain", "category": "pain_location"},
    
    # Drug interactions & monitoring
    {"darija": "مراقبة دورية", "french": "Surveillance régulière", "english": "Regular monitoring", "category": "follow_up"},
    {"darija": "التفاعلات الدوائية", "french": "Interactions médicamenteuses", "english": "Drug interactions", "category": "medication"},
    {"darija": "الحساسية الدوائية", "french": "Allergie aux médicaments", "english": "Drug allergy", "category": "medication"},
    {"darija": "الآثار الجانبية", "french": "Effets secondaires", "english": "Side effects", "category": "medication"},
    
    # Clinical outcomes
    {"darija": "التحسن", "french": "Amélioration", "english": "Improvement", "category": "outcomes"},
    {"darija": "التدهور", "french": "Aggravation", "english": "Deterioration", "category": "outcomes"},
    {"darija": "الاستقرار", "french": "Stabilisation", "english": "Stabilization", "category": "outcomes"},
    
    # Diet & Lifestyle
    {"darija": "الحمية", "french": "Régime", "english": "Diet", "category": "lifestyle"},
    {"darija": "ممارسة الرياضة", "french": "Exercice physique", "english": "Physical exercise", "category": "lifestyle"},
    {"darija": "التوتر", "french": "Stress", "english": "Stress", "category": "lifestyle"},
    {"darija": "النوم", "french": "Sommeil", "english": "Sleep", "category": "lifestyle"},
    {"darija": "التدخين", "french": "Tabagisme", "english": "Smoking", "category": "lifestyle"},
    
    # Risk factors
    {"darija": "السمنة", "french": "Obésité", "english": "Obesity", "category": "risk_factors"},
    {"darija": "فرط ضغط الدم", "french": "Hypertension artérielle", "english": "Hypertension", "category": "risk_factors"},
    {"darija": "ارتفاع الكوليسترول", "french": "Hypercholestérolémie", "english": "High cholesterol", "category": "risk_factors"},
    {"darija": "التاريخ العائلي", "french": "Antécédents familiaux", "english": "Family history", "category": "risk_factors"},
    
    # Additional Darija specialized terms
    {"darija": "الخمول", "french": "Apathie", "english": "Lethargy", "category": "symptoms"},
    {"darija": "القشعريرة", "french": "Frissons", "english": "Chills", "category": "symptoms"},
    {"darija": "الغثيان", "french": "Nausée", "english": "Nausea", "category": "symptoms"},
    {"darija": "القيء", "french": "Vomissement", "english": "Vomiting", "category": "symptoms"},
    {"darija": "الحكة", "french": "Prurit", "english": "Itching", "category": "symptoms"},
    {"darija": "الطفح الجلدي", "french": "Éruption cutanée", "english": "Rash", "category": "symptoms"},
    {"darija": "التورم", "french": "Œdème", "english": "Edema", "category": "symptoms"},
    {"darija": "الزرقان", "french": "Cyanose", "english": "Cyanosis", "category": "symptoms"},
    {"darija": "الصفار", "french": "Ictère", "english": "Jaundice", "category": "symptoms"},
    
    # Advanced terms
    {"darija": "المضبوطات", "french": "Convulsions", "english": "Seizures", "category": "neurological"},
    {"darija": "الغيبوبة", "french": "Coma", "english": "Coma", "category": "neurological"},
    {"darija": "فقدان الوعي", "french": "Syncope", "english": "Fainting", "category": "neurological"},
    {"darija": "الشلل", "french": "Paralysie", "english": "Paralysis", "category": "neurological"},
    
    # Chronic management
    {"darija": "إدارة المرض المزمن", "french": "Gestion de la maladie chronique", "english": "Chronic disease management", "category": "management"},
    {"darija": "الامتثال العلاجي", "french": "Adhérence thérapeutique", "english": "Treatment adherence", "category": "management"},
    {"darija": "عدم الامتثال", "french": "Non-adhérence", "english": "Non-compliance", "category": "management"},
    {"darija": "المتابعة المنتظمة", "french": "Suivi régulier", "english": "Regular follow-up", "category": "management"},
]


def get_glossary() -> list[dict]:
    """Get the complete Darija medical glossary."""
    return DARIJA_MEDICAL_GLOSSARY


def search_glossary(term: str, language: str = "darija") -> list[dict]:
    """Search glossary by term in specified language."""
    term_lower = term.lower()
    return [
        entry
        for entry in DARIJA_MEDICAL_GLOSSARY
        if term_lower in entry.get(language, "").lower()
    ]
