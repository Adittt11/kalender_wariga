from fastapi import APIRouter, HTTPException

from app.services.pebayuhan_service import get_pebayuhan_by_lahir

router = APIRouter()


@router.get("/{tanggal}")
def get_pebayuhan(tanggal: str):
    """
    Get pebayuhan data based on a birth date (YYYY-MM-DD).
    Looks up saptawara and pancawara from kalender_bali,
    then returns matching pebayuhan entries.
    """
    try:
        data = get_pebayuhan_by_lahir(tanggal)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return {
        "success": True,
        "data": data,
    }
