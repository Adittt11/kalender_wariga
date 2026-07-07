from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.kalender_service import generate_kalender_range

router = APIRouter()


class GenerateRequest(BaseModel):
    start_date: str
    end_date: str
    aspects: list[str] = None


@router.post("/kalender")
def generate_kalender(payload: GenerateRequest):
    try:
        data = generate_kalender_range(
            payload.start_date,
            payload.end_date,
            aspects=payload.aspects
        )
        return {
            "success": True,
            "message": "Kalender berhasil digenerate",
            "total": len(data),
            "data": data,
        }

    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=503 if isinstance(error, RuntimeError) else 400,
            detail=str(error)
        ) from error
