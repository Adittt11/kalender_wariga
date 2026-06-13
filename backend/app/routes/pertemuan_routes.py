from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.pertemuan_service import calculate_pertemuan_lanang_istri

router = APIRouter()


class PertemuanRequest(BaseModel):
    tanggal_lanang: str
    tanggal_istri: str


@router.post("/lanang-istri")
def pertemuan_lanang_istri(payload: PertemuanRequest):
    try:
        data = calculate_pertemuan_lanang_istri(
            payload.tanggal_lanang,
            payload.tanggal_istri,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return {
        "success": True,
        "data": data,
    }
