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
                FROM makna_4aspek
            """)
        )

        return [dict(row._mapping) for row in result]


def get_kalender_rows_by_range(start, end, conn=None):
    def execute(connection):
        return connection.execute(
            text("""
                SELECT *
                FROM kalender_bali
                WHERE date BETWEEN :start AND :end
                ORDER BY date
            """),
            {
                "start": start,
                "end": end,
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
                WHERE date = :target
            """),
            {
                "target": target,
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
            FROM makna_4aspek
        """)
    )

    return [dict(row._mapping) for row in result]


def get_keterangan_wuku_rows(conn):
    result = conn.execute(
        text("""
            SELECT *
            FROM keterangan_wuku
        """)
    )

    return [dict(row._mapping) for row in result]


def get_keterangan_pancawara_saptawara_rows(conn):
    result = conn.execute(
        text("""
            SELECT *
            FROM keterangan_pancawara_saptawara
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


def build_karakter_kelahiran(row, makna_rows, wuku_rows, ps_rows, aspects=None):
    if aspects is not None:
        aspects = [a.lower().strip() for a in aspects]

    def is_enabled(name):
        if not aspects:
            return True
        return name in aspects

    parts = []

    # 1. Palalintangan
    if is_enabled("palalintangan"):
        n_pal = gv(row, "Palalintangan")
        m_pal = get_deskripsi(makna_rows, "Palalintangan", "Makna_Palalintangan", n_pal)
        parts.append(f"Palalintangan {n_pal}: {m_pal}")

    # 2. Ekajalarsi
    if is_enabled("ekajalarsi"):
        n_eka = gv(row, "Ekajalarsi")
        m_eka = get_deskripsi(makna_rows, "Ekajalarsi", "Makna_Ekajalarsi", n_eka)
        parts.append(f"Ekajalarsi {n_eka}: {m_eka}")

    # 3. Pratiti Samutpada
    if is_enabled("pratiti_samutpada") or is_enabled("pratiti"):
        n_pra = gv(row, "PratitiSamutpada")
        m_pra = get_deskripsi(makna_rows, "PratitiSamutpada", "Makna_PratitiSamutpada", n_pra)
        parts.append(f"Pratiti Samutpada {n_pra}: {m_pra}")

    # 4. Pararasan
    if is_enabled("pararasan"):
        n_par = gv(row, "Pararasan")
        m_par = get_deskripsi(makna_rows, "Pararasan", "Makna_Pararasan", n_par)
        parts.append(f"Pararasan {n_par}: {m_par}")

    # 5. Wuku
    if is_enabled("wuku"):
        n_wuku = gv(row, "Wuku")
        m_wuku = "-"
        wuku_clean = str(n_wuku).strip().lower()
        for r in wuku_rows:
            if str(r.get("Wuku", "")).strip().lower() == wuku_clean:
                m_wuku = str(r.get("Keterangan", "-")).strip()
                break
        parts.append(f"Wuku {n_wuku}: {m_wuku}")

    # 6. Pancawara
    if is_enabled("pancawara"):
        n_pan = gv(row, "Pancawara")
        m_pan = "-"
        pan_clean = str(n_pan).strip().lower()
        for r in ps_rows:
            p_val = r.get("pancawara")
            if p_val and str(p_val).strip().lower() == pan_clean:
                m_pan = str(r.get("keterangan_pancawara", "-")).strip()
                break
        parts.append(f"Pancawara {n_pan}: {m_pan}")

    # 7. Saptawara
    if is_enabled("saptawara"):
        n_sap = gv(row, "Saptawara")
        m_sap = "-"
        sap_clean = str(n_sap).strip().lower()
        if sap_clean == "wraspati":
            sap_clean = "wrespati"
        for r in ps_rows:
            s_val = r.get("saptawara")
            if s_val and str(s_val).strip().lower() == sap_clean:
                m_sap = str(r.get("keterangan_saptawara", "-")).strip()
                break
        parts.append(f"Saptawara {n_sap}: {m_sap}")

    return ". ".join(parts) + "." if parts else ""


def parse_row(row, makna_rows, wuku_rows=None, ps_rows=None, aspects=None):
    if wuku_rows is None:
        wuku_rows = []
    if ps_rows is None:
        ps_rows = []

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
        "karakter_kelahiran": build_karakter_kelahiran(row, makna_rows, wuku_rows, ps_rows, aspects),
    }


def generate_kalender_range(start_date, end_date, aspects=None):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        raise ValueError("Tanggal akhir tidak boleh lebih kecil dari tanggal awal")

    with engine.connect() as conn:
        kalender_rows = get_kalender_rows_by_range(start, end, conn)
        makna_rows = get_makna_rows(conn)
        wuku_rows = get_keterangan_wuku_rows(conn)
        ps_rows = get_keterangan_pancawara_saptawara_rows(conn)

    hasil = []

    for row in kalender_rows:
        hasil.append(parse_row(row, makna_rows, wuku_rows, ps_rows, aspects))

    hasil.sort(key=lambda item: (item["tahun"], item["bulan"], item["tanggal"]))

    return hasil


def get_kalender_by_date(tanggal, aspects=None):
    target = datetime.strptime(tanggal, "%Y-%m-%d").date()

    with engine.connect() as conn:
        row = get_kalender_row_by_date(target, conn)
        makna_rows = get_makna_rows(conn)
        wuku_rows = get_keterangan_wuku_rows(conn)
        ps_rows = get_keterangan_pancawara_saptawara_rows(conn)

    return parse_row(row, makna_rows, wuku_rows, ps_rows, aspects) if row else None


def get_kalender_by_month(tahun, bulan, aspects=None):
    with engine.connect() as conn:
        kalender_rows = get_kalender_rows_by_month(tahun, bulan, conn)
        makna_rows = get_makna_rows(conn)
        wuku_rows = get_keterangan_wuku_rows(conn)
        ps_rows = get_keterangan_pancawara_saptawara_rows(conn)

    hasil = [parse_row(row, makna_rows, wuku_rows, ps_rows, aspects) for row in kalender_rows]
    hasil.sort(key=lambda item: item["tanggal"])

    return hasil
