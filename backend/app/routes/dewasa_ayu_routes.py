from fastapi import APIRouter, HTTPException, Query

from app.services.dewasa_ayu_service import get_dewasa_options, search_dewasa

router = APIRouter()


@router.get("/options")
def dewasa_options():
    return {
        "success": True,
        "data": get_dewasa_options(),
    }


@router.get("/search")
def dewasa_search(
    jenis_yadnya: str = Query(...),
    upacara: str = Query(...),
    tanggal: str | None = Query(None),
    bulan: int | None = Query(None),
    tahun: int | None = Query(None),
):
    try:
        data = search_dewasa(
            jenis_yadnya=jenis_yadnya,
            upacara=upacara,
            tanggal=tanggal,
            bulan=bulan,
            tahun=tahun,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "success": True,
        "filters": {
            "jenis_yadnya": jenis_yadnya,
            "upacara": upacara,
            "tanggal": tanggal,
            "bulan": bulan,
            "tahun": tahun,
        },
        "data": data,
    }
