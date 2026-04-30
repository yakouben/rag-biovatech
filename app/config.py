from dotenv import load_dotenv
import os
from functools import lru_cache

load_dotenv()

# Variables as requested
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST")
SUPABASE_DB_PORT = os.getenv("SUPABASE_DB_PORT")
SUPABASE_DB_NAME = os.getenv("SUPABASE_DB_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
ENABLE_DRIFT_DETECTION = os.getenv("ENABLE_DRIFT_DETECTION", "true").lower() == "true"
ENABLE_PDF_GENERATION = os.getenv("ENABLE_PDF_GENERATION", "true").lower() == "true"
DECISION_TREE_MAX_DEPTH = os.getenv("DECISION_TREE_MAX_DEPTH")
DECISION_TREE_MIN_SAMPLES_LEAF = os.getenv("DECISION_TREE_MIN_SAMPLES_LEAF")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")


# Settings class for compatibility with existing service logic
class Settings:
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_KEY
        self.supabase_db_user = SUPABASE_DB_USER
        self.supabase_db_password = SUPABASE_DB_PASSWORD
        self.supabase_db_host = SUPABASE_DB_HOST
        self.supabase_db_port = int(SUPABASE_DB_PORT) if SUPABASE_DB_PORT and SUPABASE_DB_PORT.isdigit() else 5432
        self.supabase_db_name = SUPABASE_DB_NAME or "postgres"
        self.gemini_api_key = GEMINI_API_KEY
        self.gemini_model = GEMINI_MODEL
        self.gemini_embedding_model = GEMINI_EMBEDDING_MODEL
        self.enable_drift_detection = ENABLE_DRIFT_DETECTION
        self.enable_pdf_generation = ENABLE_PDF_GENERATION
        self.decision_tree_max_depth = int(DECISION_TREE_MAX_DEPTH) if DECISION_TREE_MAX_DEPTH and DECISION_TREE_MAX_DEPTH.isdigit() else 10
        self.decision_tree_min_samples_leaf = int(DECISION_TREE_MIN_SAMPLES_LEAF) if DECISION_TREE_MIN_SAMPLES_LEAF and DECISION_TREE_MIN_SAMPLES_LEAF.isdigit() else 5
        self.groq_api_key = GROQ_API_KEY
        self.groq_model = GROQ_MODEL


        self.app_version = "1.0.0"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.debug = self.environment == "development"
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

@lru_cache
def get_settings():
    return Settings()
