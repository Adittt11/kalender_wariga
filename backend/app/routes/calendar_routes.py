from fastapi import APIRouter, HTTPException

from app.services.kalender_service import (
    get_kalender_by_date,
    get_kalender_by_month,
)
from app.services.groq_service import (
    generate_cetak_kalender_ai,
    generate_karakter_kelahiran_ai,
)

router = APIRouter()


@router.get("/date/{tanggal}")
def calendar_by_date(tanggal: str, aspects: str = None):
    aspect_list = None
    if aspects:
        aspect_list = [a.strip().lower() for a in aspects.split(",") if a.strip()]

    data = get_kalender_by_date(tanggal, aspects=aspect_list)

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
def calendar_by_month(tahun: int, bulan: int, aspects: str = None):
    aspect_list = None
    if aspects:
        aspect_list = [a.strip().lower() for a in aspects.split(",") if a.strip()]

    data = get_kalender_by_month(tahun, bulan, aspects=aspect_list)

    return {
        "success": True,
        "total": len(data),
        "data": data,
    }


@router.post("/date/{tanggal}/character-ai")
def calendar_character_ai(tanggal: str, aspects: str = None):
    aspect_list = None
    if aspects:
        aspect_list = [a.strip().lower() for a in aspects.split(",") if a.strip()]

    data = get_kalender_by_date(tanggal, aspects=aspect_list)

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


@router.post("/date/{tanggal}/print-ai")
def calendar_print_ai(tanggal: str, aspects: str = None):
    aspect_list = None
    if aspects:
        aspect_list = [a.strip().lower() for a in aspects.split(",") if a.strip()]

    data = get_kalender_by_date(tanggal, aspects=aspect_list)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Data kalender tidak ditemukan"
        )

    try:
        summary = generate_cetak_kalender_ai(data)
    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        ) from error

    return {
        "success": True,
        "data": summary,
    }
