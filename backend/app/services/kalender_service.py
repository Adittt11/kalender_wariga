from datetime import datetime
from sqlalchemy import text
from app.services.database import engine


URIP_SADWARA = {
    "Tungleh": 7,
    "Aryang": 6,
    "Urukung": 5,
    "Paniron": 8,
    "Was": 9,
    "Maulu": 3,
}

URIP_SAPTAWARA = {
    "Redite": 5,
    "Soma": 4,
    "Anggara": 3,
    "Buda": 7,
    "Wraspati": 8,
    "Sukra": 6,
    "Saniscara": 9,
}

URIP_PANCAWARA = {
    "Umanis": 5,
    "Paing": 9,
    "Pon": 7,
    "Wage": 4,
    "Kliwon": 8,
}


def gv(row, col, default="-"):
    value = row.get(col, default)

    if value is None:
        return default

    value = str(value).strip()

    if value.lower() in ("nan", "", "none", "0"):
        return default

    return value


def title_value(value):
    if value == "-":
        return value

    return str(value).strip().capitalize()


def fmt_urip(value, urip_dict):
    key = title_value(value)

    if key in urip_dict:
        return f"{key} ({urip_dict[key]})"

    return key


def get_all_kalender():
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT *
                FROM kalender_bali
            """)
        )

        return [dict(row._mapping) for row in result]


def get_all_makna():
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT *
                FROM tambahan
            """)
        )

        return [dict(row._mapping) for row in result]


def get_kalender_rows_by_range(start, end, conn=None):
    def execute(connection):
        return connection.execute(
            text("""
                SELECT *
                FROM kalender_bali
                WHERE ("Tahun", "Bulan", "Tanggal")
                      BETWEEN (:start_year, :start_month, :start_day)
                          AND (:end_year, :end_month, :end_day)
                ORDER BY "Tahun", "Bulan", "Tanggal"
            """),
            {
                "start_year": start.year,
                "start_month": start.month,
                "start_day": start.day,
                "end_year": end.year,
                "end_month": end.month,
                "end_day": end.day,
            },
        )

    if conn is not None:
        return [dict(row._mapping) for row in execute(conn)]

    with engine.connect() as conn:
        return [dict(row._mapping) for row in execute(conn)]


def get_kalender_row_by_date(target, conn=None):
    def execute(connection):
        return connection.execute(
            text("""
                SELECT *
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

    if conn is not None:
        row = execute(conn)
        return dict(row) if row else None

    with engine.connect() as conn:
        row = execute(conn)

        return dict(row) if row else None


def get_kalender_rows_by_month(tahun, bulan, conn=None):
    def execute(connection):
        return connection.execute(
            text("""
                SELECT *
                FROM kalender_bali
                WHERE "Tahun" = :tahun
                  AND "Bulan" = :bulan
                ORDER BY "Tanggal"
            """),
            {
                "tahun": tahun,
                "bulan": bulan,
            },
        )

    if conn is not None:
        return [dict(row._mapping) for row in execute(conn)]

    with engine.connect() as conn:
        return [dict(row._mapping) for row in execute(conn)]


def get_makna_rows(conn):
    result = conn.execute(
        text("""
            SELECT *
            FROM tambahan
        """)
    )

    return [dict(row._mapping) for row in result]


def get_deskripsi(makna_rows, col_nama, col_makna, target_val):
    if target_val == "-":
        return "-"

    target = str(target_val).strip().lower()

    for row in makna_rows:
        nama = str(row.get(col_nama, "")).strip().lower()

        if nama == target:
            makna = row.get(col_makna, "-")

            if makna is None:
                return "-"

            makna = str(makna).strip()
            return makna if makna else "-"

    return "-"


def build_karakter_kelahiran(row, makna_rows):
    n_pal = gv(row, "Palalintangan")
    n_par = gv(row, "Pararasan")
    n_pra = gv(row, "PratitiSamutpada")
    n_eka = gv(row, "Ekajalarsi")

    m_pal = get_deskripsi(
        makna_rows,
        "Palalintangan",
        "Makna_Palalintangan",
        n_pal
    )

    m_par = get_deskripsi(
        makna_rows,
        "Pararasan",
        "Makna_Pararasan",
        n_par
    )

    m_pra = get_deskripsi(
        makna_rows,
        "PratitiSamutpada",
        "Makna_PratitiSamutpada",
        n_pra
    )

    m_eka = get_deskripsi(
        makna_rows,
        "Ekajalarsi",
        "Makna_Ekajalarsi",
        n_eka
    )

    return (
        f"Palalintangan {n_pal}: {m_pal}. "
        f"Ekajalarsi {n_eka}: {m_eka}. "
        f"Pratiti Samutpada {n_pra}: {m_pra}. "
        f"Pararasan {n_par}: {m_par}."
    )


def parse_row(row, makna_rows):
    pengelong = gv(row, "Pengelong")
    status_mala = gv(row, "Status_Mala")
    status_purnama = gv(row, "Status_Purnama")

    sasih = title_value(gv(row, "Sasih"))

    if status_mala != "-":
        sasih = f"{sasih} - {status_mala}"

    if pengelong == "-":
        label_lunar = "Penanggal"
        nilai_lunar = gv(row, "Penanggal")
    else:
        label_lunar = "Pengelong"
        nilai_lunar = pengelong

    if status_purnama != "-":
        nilai_lunar = f"{nilai_lunar} - {status_purnama}"

    return {
        "tanggal": int(row["Tanggal"]),
        "bulan": int(row["Bulan"]),
        "tahun": int(row["Tahun"]),
        "tanggal_lengkap": f"{int(row['Tahun'])}-{int(row['Bulan']):02d}-{int(row['Tanggal']):02d}",

        "ingkel": title_value(gv(row, "Ingkel")),
        "wuku": title_value(gv(row, "Wuku")),
        "sasih": sasih,

        "label_lunar": label_lunar,
        "nilai_lunar": nilai_lunar,

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

        "ekajalarsi": title_value(gv(row, "Ekajalarsi")),
        "palalintangan": title_value(gv(row, "Palalintangan")),
        "pararasan": title_value(gv(row, "Pararasan")),
        "pratiti_samutpada": title_value(gv(row, "PratitiSamutpada")),

        "pakakalan": gv(row, "Pakakalan"),
        "baik_buruk_hari": gv(row, "InformasiPakakalan"),
        "dawuh": gv(row, "dawuh", gv(row, "Dawuh")),

        "kajengkliwon": gv(row, "kajengkliwon"),
        "harikeagamaan": gv(row, "harikeagamaan"),
        "nyepi": gv(row, "Nyepi"),
        "harinonbali": gv(row, "harinonbali"),
        "piodalan": gv(row, "piodalan"),

        "status_purnama": status_purnama,
        "karakter_kelahiran": build_karakter_kelahiran(row, makna_rows),
    }


def generate_kalender_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        raise ValueError("Tanggal akhir tidak boleh lebih kecil dari tanggal awal")

    with engine.connect() as conn:
        kalender_rows = get_kalender_rows_by_range(start, end, conn)
        makna_rows = get_makna_rows(conn)

    hasil = []

    for row in kalender_rows:
        hasil.append(parse_row(row, makna_rows))

    hasil.sort(key=lambda item: (item["tahun"], item["bulan"], item["tanggal"]))

    return hasil


def get_kalender_by_date(tanggal):
    target = datetime.strptime(tanggal, "%Y-%m-%d").date()

    with engine.connect() as conn:
        row = get_kalender_row_by_date(target, conn)
        makna_rows = get_makna_rows(conn)

    return parse_row(row, makna_rows) if row else None


def get_kalender_by_month(tahun, bulan):
    with engine.connect() as conn:
        kalender_rows = get_kalender_rows_by_month(tahun, bulan, conn)
        makna_rows = get_makna_rows(conn)

    hasil = [parse_row(row, makna_rows) for row in kalender_rows]
    hasil.sort(key=lambda item: item["tanggal"])

    return hasil
