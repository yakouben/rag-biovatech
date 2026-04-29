from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import ai, patients, doctor, system
from app.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ChronicCare AI API",
        version="1.1.0",
        description="Refactored Modular API for ChronicCare AI"
    )

    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "*"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    @app.middleware("http")
    async def add_cors_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal Server Error: {str(exc)}"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
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
