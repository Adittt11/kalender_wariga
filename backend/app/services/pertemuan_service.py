from datetime import datetime

from sqlalchemy import text

from app.services.database import engine


POSITION_MEANINGS = {
    1: ("Sri", "Selalu sejahtera dan bahagia"),
    2: ("Gedong", "Tidak kurang sandang pangan"),
    3: ("Pete", "Selalu bertengkar dan ribut, sengsara"),
    4: ("Pati", "Mlarat dan banyak masalah"),
    0: ("Lungguh", "Sama dengan keadaan sebelumnya bahkan akan mendapatkan kedudukan yang lebih baik"),
}


def clean_value(value, default="-"):
    if value is None:
        return default

    value = str(value).strip()

    if value.lower() in ("", "none", "nan", "0"):
        return default

    return value


def normalize_key(value):
    return str(value).strip().lower().replace("_", " ")


def get_column(row, candidates, default="-"):
    normalized = {
        normalize_key(key): value
        for key, value in row.items()
    }

    for candidate in candidates:
        key = normalize_key(candidate)
        if key in normalized:
            return clean_value(normalized[key], default)

    return default


def parse_birth_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_kalender_bali_birth_data(target, conn):
    row = conn.execute(
        text("""
            SELECT *
            FROM kalender_bali
            WHERE date = :target
        """),
        {"target": target},
    ).mappings().first()

    if not row:
        return None

    row = dict(row)

    return {
        "tanggal_lahir": f"{target.year}-{target.month:02d}-{target.day:02d}",
        "wuku": get_column(row, ["Wuku"]),
        "saptawara": get_column(row, ["Saptawara"]),
        "pancawara": get_column(row, ["Pancawara"]),
        "sadwara": get_column(row, ["Sadwara"]),
    }


def build_urip_mapping(conn):
    rows = conn.execute(
        text("""
            SELECT *
            FROM daftar_wariga
        """)
    )

    mapping = {}

    for row in rows:
        row = dict(row._mapping)
        nama_hari = get_column(row, ["Nama hari", "Nama Hari", "nama_hari", "hari", "nama"], "")
        urip = get_column(row, ["Urip", "urip"], "")

        if not nama_hari or not urip:
            continue

        try:
            mapping[nama_hari.strip().lower()] = int(float(urip))
        except ValueError:
            continue

    return mapping


def get_urip_value(mapping, name):
    return mapping.get(str(name).strip().lower(), 0)


def calculate_person_urip(data, mapping):
    parts = {
        "saptawara": get_urip_value(mapping, data["saptawara"]),
        "sadwara": get_urip_value(mapping, data["sadwara"]),
        "pancawara": get_urip_value(mapping, data["pancawara"]),
    }

    return {
        "detail": parts,
        "total": sum(parts.values()),
    }


def build_tenung_rows(total):
    rows = []
    current = total
    previous_total = None
    previous_division = None
    index = 0

    while current >= 5:
        start_year = index * 5
        end_year = (index + 1) * 5
        division = current // 5
        remainder = current % 5
        position, meaning = POSITION_MEANINGS[remainder]

        if index == 0:
            calculation = f"{current} : 5 = {division}"
        else:
            calculation = (
                f"{previous_total} - {previous_division} = {current} | "
                f"{current} : 5 = {division}"
            )

        rows.append({
            "umur_pernikahan": f"{start_year}-{end_year} tahun",
            "perhitungan": calculation,
            "sisa": remainder,
            "posisi": position,
            "artinya": meaning,
        })

        previous_total = current
        previous_division = division
        current -= division
        index += 1

    return rows


def calculate_pertemuan_lanang_istri(tanggal_lanang, tanggal_istri):
    lanang_date = parse_birth_date(tanggal_lanang)
    istri_date = parse_birth_date(tanggal_istri)

    with engine.connect() as conn:
        lanang = get_kalender_bali_birth_data(lanang_date, conn)
        istri = get_kalender_bali_birth_data(istri_date, conn)

        if not lanang or not istri:
            missing = []

            if not lanang:
                missing.append("lanang")

            if not istri:
                missing.append("istri")

            raise ValueError(f"Data kalender_bali tidak ditemukan untuk: {', '.join(missing)}")

        mapping = build_urip_mapping(conn)

    urip_lanang = calculate_person_urip(lanang, mapping)
    urip_istri = calculate_person_urip(istri, mapping)
    total_urip = urip_lanang["total"] + urip_istri["total"]

    return {
        "lanang": {
            **lanang,
            "urip": urip_lanang,
        },
        "istri": {
            **istri,
            "urip": urip_istri,
        },
        "total_urip": total_urip,
        "hasil": build_tenung_rows(total_urip),
    }
