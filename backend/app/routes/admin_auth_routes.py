from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.admin_auth_service import (
    TOKEN_TTL_SECONDS,
    create_admin_token,
    verify_admin_credentials,
)


router = APIRouter()


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


@router.post("/login")
def admin_login(payload: AdminLoginRequest):
    if not verify_admin_credentials(payload.username, payload.password):
        raise HTTPException(
            status_code=401,
            detail="Username atau password admin salah.",
        )

    return {
        "success": True,
        "data": {
            "token": create_admin_token(payload.username),
            "token_type": "bearer",
            "expires_in": TOKEN_TTL_SECONDS,
        },
    }
