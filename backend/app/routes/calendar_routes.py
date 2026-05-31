from fastapi import APIRouter, HTTPException

from app.services.kalender_service import (
    get_kalender_by_date,
    get_kalender_by_month,
)
from app.services.groq_service import generate_karakter_kelahiran_ai

router = APIRouter()


@router.get("/date/{tanggal}")
def calendar_by_date(tanggal: str):
    data = get_kalender_by_date(tanggal)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Data kalender tidak ditemukan"
        )

    return {
        "success": True,
        "data": data,
    }


@router.get("/month/{tahun}/{bulan}")
def calendar_by_month(tahun: int, bulan: int):
    data = get_kalender_by_month(tahun, bulan)

    return {
        "success": True,
        "total": len(data),
        "data": data,
    }


@router.post("/date/{tanggal}/character-ai")
def calendar_character_ai(tanggal: str):
    data = get_kalender_by_date(tanggal)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Data kalender tidak ditemukan"
        )

    try:
        character = generate_karakter_kelahiran_ai(data)
    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        ) from error

    return {
        "success": True,
        "data": {
            "tanggal_lengkap": data["tanggal_lengkap"],
            "model": "groq",
            "karakter_kelahiran_ai": character,
        },
    }
