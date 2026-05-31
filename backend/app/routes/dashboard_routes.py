from fastapi import APIRouter, HTTPException

from app.services.kalender_bali_service import (
    get_kalender_bali_by_date,
    get_kalender_bali_by_month,
)

router = APIRouter()


@router.get("/date/{tanggal}")
def dashboard_by_date(tanggal: str):
    data = get_kalender_bali_by_date(tanggal)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Data kalender Bali tidak ditemukan",
        )

    return {
        "success": True,
        "data": data,
    }


@router.get("/month/{tahun}/{bulan}")
def dashboard_by_month(tahun: int, bulan: int):
    data = get_kalender_bali_by_month(tahun, bulan)

    return {
        "success": True,
        "total": len(data),
        "data": data,
    }
