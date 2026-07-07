from datetime import datetime

from sqlalchemy import text

from app.services.database import engine


def parse_birth_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_pebayuhan_by_lahir(tanggal: str):
    target = parse_birth_date(tanggal)

    with engine.connect() as conn:
        # Step 1: Get Saptawara & Pancawara from kalender_bali for the birth date
        kb_row = conn.execute(
            text("""
                SELECT "Saptawara", "Pancawara"
                FROM kalender_bali
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

        if not kb_row:
            raise ValueError(
                f"Data kalender Bali tidak ditemukan untuk tanggal: {tanggal}"
            )

        saptawara = str(kb_row["Saptawara"]).strip()
        pancawara = str(kb_row["Pancawara"]).strip()

        # Step 2: Find matching pebayuhan entries
        pb_rows = conn.execute(
            text("""
                SELECT *
                FROM pebayuhan
                WHERE LOWER("Saptawara") = LOWER(:saptawara)
                  AND LOWER("Pancawara") = LOWER(:pancawara)
            """),
            {
                "saptawara": saptawara,
                "pancawara": pancawara,
            },
        ).mappings().all()

    return {
        "tanggal_lahir": tanggal,
        "saptawara": saptawara,
        "pancawara": pancawara,
        "pebayuhan": [dict(row) for row in pb_rows],
    }
