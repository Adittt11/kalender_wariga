from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.kalender_service import generate_kalender_range

router = APIRouter()


class GenerateRequest(BaseModel):
    start_date: str
    end_date: str


@router.post("/kalender")
def generate_kalender(payload: GenerateRequest):
    try:
        data = generate_kalender_range(
            payload.start_date,
            payload.end_date
        )

        return {
            "success": True,
            "message": "Kalender berhasil digenerate",
            "total": len(data),
            "data": data,
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )