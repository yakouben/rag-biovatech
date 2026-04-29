from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ai, patients, doctor, system
from app.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ChronicCare AI API",
        version="1.1.0",
        description="Refactored Modular API for ChronicCare AI"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclusion des nouveaux modules avec les bons préfixes
    app.include_router(ai.router, prefix="/api/v1")
    app.include_router(patients.router, prefix="/api/v1")
    app.include_router(doctor.router, prefix="/api/v1")
    app.include_router(system.router, prefix="/api/v1")

    @app.get("/")
    def root():
        return {"message": "ChronicCare AI API is running in modular mode"}

    return app

app = create_app()
