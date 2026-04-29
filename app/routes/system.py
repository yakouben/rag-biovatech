from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(prefix="/system", tags=["System & Glossary"])

@router.get("/health")
async def health_check():
    settings = get_settings()
    return {"status": "healthy", "version": settings.app_version}

@router.get("/glossary")
async def get_glossary():
    from data.darija_medical_glossary import get_glossary
    return get_glossary()
