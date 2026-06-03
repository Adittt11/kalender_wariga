from datetime import datetime

from sqlalchemy import text

from app.services.database import engine
from app.services.kalender_service import (
    URIP_PANCAWARA,
    URIP_SADWARA,
    URIP_SAPTAWARA,
    fmt_urip,
    gv,
    title_value,
)


def parse_row(row):
    panglong = gv(row, "Panglong")
    status_purnama = gv(row, "Status_Purnama")
    status_mala = gv(row, "Status_Mala")
    sasih = title_value(gv(row, "Sasih"))

    if status_mala != "-":
        sasih = f"{sasih} - {status_mala}"

    if panglong == "-":
        label_lunar = "Penanggal"
        nilai_lunar = gv(row, "Penanggal")
    else:
        label_lunar = "Panglong"
        nilai_lunar = panglong

    if status_purnama != "-":
        nilai_lunar = f"{nilai_lunar} - {status_purnama}"

    return {
        "tanggal": int(row["Tanggal"]),
        "bulan": int(row["Bulan"]),
        "tahun": int(row["Tahun"]),
        "tanggal_lengkap": f"{int(row['Tahun'])}-{int(row['Bulan']):02d}-{int(row['Tanggal']):02d}",
        "wuku": title_value(gv(row, "Wuku")),
        "ingkel": title_value(gv(row, "Ingkel")),
        "sasih": sasih,
        "label_lunar": label_lunar,
        "nilai_lunar": nilai_lunar,
        "status_purnama": status_purnama,
        "ekawara": title_value(gv(row, "Ekawara")),
        "dwiwara": title_value(gv(row, "Dwiwara")),
        "triwara": title_value(gv(row, "Triwara")),
        "caturwara": title_value(gv(row, "Caturwara")),
        "pancawara": fmt_urip(gv(row, "Pancawara"), URIP_PANCAWARA),
        "sadwara": fmt_urip(gv(row, "Sadwara"), URIP_SADWARA),
        "saptawara": fmt_urip(gv(row, "Saptawara"), URIP_SAPTAWARA),
        "astawara": title_value(gv(row, "Astawara")),
        "sangawara": title_value(gv(row, "Sangawara")),
        "dasawara": title_value(gv(row, "Dasawara")),
    }


def get_kalender_bali_by_month(tahun, bulan):
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT *, "Pengelong" AS "Panglong"
                FROM kalender_dawuh
                WHERE "Tahun" = :tahun AND "Bulan" = :bulan
                ORDER BY "Tanggal"
            """),
            {"tahun": tahun, "bulan": bulan},
        )

        return [parse_row(dict(row._mapping)) for row in rows]


def get_kalender_bali_by_date(tanggal):
    target = datetime.strptime(tanggal, "%Y-%m-%d").date()

    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT *, "Pengelong" AS "Panglong"
                FROM kalender_dawuh
                WHERE "Tahun" = :tahun
                  AND "Bulan" = :bulan
                  AND "Tanggal" = :tanggal
            """),
            {
                "tahun": target.year,
                "bulan": target.month,
                "tanggal": target.day,
            },
        ).mappings().first()

        return parse_row(dict(row)) if row else None
