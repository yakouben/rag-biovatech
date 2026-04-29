import os
from fastapi import Header, HTTPException, status

def verify_internal_api_key(x_internal_key: str = Header(None)) -> None:
    """Dépendance de sécurité partagée pour tous les routers."""
    expected_key = os.getenv("INTERNAL_API_KEY")
    if expected_key and x_internal_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing INTERNAL_API_KEY header"
        )
