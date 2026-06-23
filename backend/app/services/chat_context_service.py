import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.services.dewasa_ayu_service import MONTHS, get_dewasa_options, search_dewasa
from app.services.kalender_service import get_kalender_by_date, get_kalender_by_month
from app.services.knowledge_service import build_knowledge_context


DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
YEAR_PATTERN = re.compile(r"\b(18\d{2}|19\d{2}|20\d{2}|21\d{2})\b")
LOCAL_DATE_PATTERN = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b")
MONTH_NAME_PATTERN = re.compile(
    r"\b(\d{1,2})\s+"
    r"(januari|jan|februari|feb|maret|mar|april|apr|mei|juni|jun|juli|jul|"
    r"agustus|agu|agt|september|sep|oktober|okt|november|nov|desember|des)"
    r"\s+(\d{4})\b",
    re.IGNORECASE,
)
INDONESIAN_MONTHS = {
    "januari": 1,
    "jan": 1,
    "februari": 2,
    "feb": 2,
    "maret": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "mei": 5,
    "juni": 6,
    "jun": 6,
    "juli": 7,
    "jul": 7,
    "agustus": 8,
    "agu": 8,
    "agt": 8,
    "september": 9,
    "sep": 9,
    "oktober": 10,
    "okt": 10,
    "november": 11,
    "nov": 11,
    "desember": 12,
    "des": 12,
}
CALENDAR_KEYWORDS = (
    "kalender",
    "wariga",
    "tanggal",
    "hari",
    "hari non bali",
    "non bali",
    "harinonbali",
    "wuku",
    "wewaran",
    "dewasa",
    "dewasa ayu",
    "upacara",
    "pakakalan",
    "dawuh",
    "sasih",
    "purnama",
    "tilem",
    "penanggal",
    "panglong",
    "pengelong",
    "ingkel",
    "ekawara",
    "dwiwara",
    "triwara",
    "caturwara",
    "pancawara",
    "sadwara",
    "saptawara",
    "astawara",
    "sangawara",
    "dasawara",
    "kelahiran",
    "palalintangan",
    "pararasan",
    "ekajalarsi",
    "pratiti",
    "penglukatan",
    "melukat",
    "pembayuhan",
    "bayuh",
    "tenung",
    "permata",
    "lontar",
    "pengetahuan",
    "knowledge",
    "odalan",
    "hari raya",
    "hari raya hindu",
    "rahinan",
    "kajeng kliwon",
    "kajengkliwon",
    "hari nasional",
    "libur nasional",
    "nasional",
)
DEWASA_QUERY_KEYWORDS = (
    "hari baik",
    "hari buruk",
    "hari biasa",
    "baik buruk",
    "baik dan buruk",
    "keduanya",
    "dewasa",
    "dewasa ayu",
    "ala ayu",
    "ala-ayu",
)
DEWASA_GROUP_LABELS = {
    "ayu": "Dewasa Ayu / baik",
    "dipakai": "Dewasa Ala-Ayu / biasa saja",
    "ala": "Dewasa Ala / buruk",
}
MONTHLY_CALENDAR_FIELDS = {
    "harinonbali": {
        "label": "Hari Nasional",
        "keywords": ("hari non bali", "non bali", "harinonbali", "hari nasional", "libur nasional", "nasional"),
    },
    "harikeagamaan": {
        "label": "Hari Raya Hindu / Rahinan",
        "keywords": (
            "hari keagamaan",
            "rahinan",
            "hari raya",
            "hari raya hindu",
            "hindu",
            "purnama",
            "tilem",
            "kajeng kliwon",
            "kajengkliwon",
            "nyepi",
        ),
    },
    "piodalan": {
        "label": "Piodalan / Odalan Pura",
        "keywords": ("piodalan", "odalan", "piodalan pura", "odalan pura", "odalan-pura"),
    },
}



def get_latest_user_message(messages):
    return next(
        (
            message["content"]
            for message in reversed(messages)
            if message["role"] == "user"
        ),
        "",
    )


def format_valid_date(year, month, day):
    try:
        return datetime(int(year), int(month), int(day)).date().isoformat()
    except (TypeError, ValueError):
        return None


def get_relative_date(text_value):
    lowered = text_value.lower()
    today = datetime.now(ZoneInfo("Asia/Makassar")).date()

    if "lusa" in lowered:
        return (today + timedelta(days=2)).isoformat()

    if "besok" in lowered:
        return (today + timedelta(days=1)).isoformat()

    if "kemarin" in lowered:
        return (today - timedelta(days=1)).isoformat()

    if "hari ini" in lowered or "sekarang" in lowered:
        return today.isoformat()

    return None


def extract_date_from_text(text_value):
    match = DATE_PATTERN.search(text_value)

    if match:
        return format_valid_date(*match.group(1).split("-"))

    match = LOCAL_DATE_PATTERN.search(text_value)

    if match:
        day, month, year = match.groups()
        return format_valid_date(year, month, day)

    match = MONTH_NAME_PATTERN.search(text_value)

    if match:
        day, month_name, year = match.groups()
        month = INDONESIAN_MONTHS.get(month_name.lower())
        return format_valid_date(year, month, day)

    return get_relative_date(text_value)


def normalize_search_text(value):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(value).lower())).strip()


def get_month_year_from_text(text_value):
    lowered = text_value.lower()
    year_match = YEAR_PATTERN.search(lowered)

    if not year_match:
        return None, None

    year = int(year_match.group(1))

    for month_name, month_number in sorted(
        INDONESIAN_MONTHS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if re.search(rf"\b{re.escape(month_name)}\b", lowered):
            return month_number, year

    return None, year


def resolve_dewasa_ceremony(text_value):
    normalized_message = normalize_search_text(text_value)
    options = get_dewasa_options()
    ceremonies_by_category = options.get("ceremonies_by_category") or {}

    candidates = []

    for category, ceremonies in ceremonies_by_category.items():
        for ceremony in ceremonies:
            candidates.append((category, ceremony, normalize_search_text(ceremony)))

    candidates.sort(key=lambda item: len(item[2]), reverse=True)

    for category, ceremony, normalized_ceremony in candidates:
        if normalized_ceremony and re.search(
            rf"\b{re.escape(normalized_ceremony)}\b",
            normalized_message,
        ):
            return category, ceremony

    return None, None


def resolve_dewasa_groups(text_value):
    normalized = normalize_search_text(text_value)
    without_ala_ayu = re.sub(r"\bala\s+ayu\b", " ", normalized)
    groups = []

    if "keduanya" in normalized or "baik buruk" in normalized or "baik dan buruk" in normalized:
        groups.extend(["ayu", "ala"])

    if "ala ayu" in normalized or "biasa" in normalized or "netral" in normalized:
        groups.append("dipakai")

    if "hari baik" in normalized or re.search(r"\bayu\b", without_ala_ayu):
        groups.append("ayu")

    if "hari buruk" in normalized or re.search(r"\bala\b", without_ala_ayu):
        groups.append("ala")

    if not groups and "dewasa" in normalized:
        groups.extend(["ayu", "dipakai", "ala"])

    ordered_groups = []

    for group in groups:
        if group not in ordered_groups:
            ordered_groups.append(group)

    return ordered_groups


def is_dewasa_search_question(text_value):
    normalized = normalize_search_text(text_value)

    return any(keyword in normalized for keyword in DEWASA_QUERY_KEYWORDS)


def resolve_monthly_calendar_field(text_value):
    normalized = normalize_search_text(text_value)

    for field_name, config in MONTHLY_CALENDAR_FIELDS.items():
        for keyword in config["keywords"]:
            if keyword in normalized:
                return field_name

    return None


def is_monthly_calendar_question(text_value):
    month, year = get_month_year_from_text(text_value)

    return bool(resolve_monthly_calendar_field(text_value) and month and year)


def build_monthly_calendar_context(query):
    field_name = resolve_monthly_calendar_field(query)

    if not field_name:
        return None

    month, year = get_month_year_from_text(query)

    if not month or not year:
        return (
            "PERTANYAAN KALENDER BULANAN TERDETEKSI:\n"
            "Bulan dan tahun belum lengkap. Minta pengguna menyebutkan bulan "
            "dan tahun, misalnya Januari 1900."
        )

    rows = get_kalender_by_month(year, month)
    label = MONTHLY_CALENDAR_FIELDS[field_name]["label"]
    period_label = f"{MONTHS[month - 1]} {year}"
    items = []

    for row in rows:
        if field_name == "harikeagamaan":
            # Gabungkan status_purnama, kajengkliwon, nyepi, dan harikeagamaan
            parts = []

            # 1. Hari Keagamaan
            val_keagamaan = row.get("harikeagamaan")
            if val_keagamaan and str(val_keagamaan).strip() != "-":
                parts.append(str(val_keagamaan).strip())

            # 2. Status Purnama/Tilem
            val_purnama = row.get("status_purnama")
            if val_purnama and str(val_purnama).strip() != "-":
                parts.append(str(val_purnama).strip())

            # 3. Kajeng Kliwon
            val_kajeng = row.get("kajengkliwon")
            if val_kajeng and str(val_kajeng).strip() != "-":
                parts.append(f"Kajeng Kliwon ({str(val_kajeng).strip()})")

            # 4. Nyepi
            val_nyepi = row.get("nyepi")
            if val_nyepi and str(val_nyepi).strip() != "-":
                parts.append(f"Nyepi ({str(val_nyepi).strip()})")

            if parts:
                items.append(
                    {
                        "tanggal": row.get("tanggal_lengkap"),
                        "nilai": ", ".join(parts),
                    }
                )
        else:
            value = row.get(field_name)

            if not value or str(value).strip() == "-":
                continue

            items.append(
                {
                    "tanggal": row.get("tanggal_lengkap"),
                    "nilai": str(value).strip(),
                }
            )

    lines = [
        "PERTANYAAN KALENDER BULANAN TERDETEKSI:",
        f"Jenis data: {label}",
        f"Periode: {period_label}",
        "Gunakan hasil database berikut sebagai sumber utama. "
        "Daftar ini hanya menampilkan tanggal yang memiliki event/hari raya. "
        "Jika suatu tanggal tidak ada dalam daftar di bawah, artinya pada tanggal tersebut "
        "memang TIDAK ADA hari raya atau hari nasional (bukan datanya yang tidak lengkap atau hilang).",
        "",
        f"Daftar {label}:",
    ]

    if not items:
        lines.append("- Tidak ada data.")
    else:
        for index, item in enumerate(items, start=1):
            lines.append(f"{index}. {item['tanggal']} - {item['nilai']}")

    return "\n".join(lines)


def merge_dewasa_results(base, addition):
    for key in ("ayu", "dipakai", "ala"):
        base[key].extend(addition.get(key, []))

    return base


def search_dewasa_for_period(jenis_yadnya, upacara, month, year):
    if month:
        return search_dewasa(jenis_yadnya, upacara, bulan=month, tahun=year)

    grouped = {
        "ayu": [],
        "dipakai": [],
        "ala": [],
    }

    for month_number in range(1, 13):
        merge_dewasa_results(
            grouped,
            search_dewasa(jenis_yadnya, upacara, bulan=month_number, tahun=year),
        )

    return grouped


def build_dewasa_context(query):
    if not is_dewasa_search_question(query):
        return None

    category, ceremony = resolve_dewasa_ceremony(query)

    if not ceremony:
        return (
            "PERTANYAAN DEWASA AYU TERDETEKSI:\n"
            "Nama upacara/kegiatan belum ditemukan pada data Dewasa Ayu. "
            "Minta pengguna menulis nama upacara yang tersedia di fitur Dewasa Ayu."
        )

    month, year = get_month_year_from_text(query)

    if not year:
        return (
            "PERTANYAAN DEWASA AYU TERDETEKSI:\n"
            "Tahun belum disebutkan. Minta pengguna menyebutkan bulan dan tahun, "
            "atau tahun saja, misalnya Juni 1900 atau tahun 1900."
        )

    groups = resolve_dewasa_groups(query)

    if not groups:
        groups = ["ayu", "dipakai", "ala"]

    results = search_dewasa_for_period(category, ceremony, month, year)
    period_label = f"{MONTHS[month - 1]} {year}" if month else f"tahun {year}"
    lines = [
        "PERTANYAAN DEWASA AYU TERDETEKSI:",
        f"Jenis Yadnya: {category}",
        f"Upacara/Kegiatan: {ceremony}",
        f"Periode: {period_label}",
        "Gunakan hasil database berikut sebagai sumber utama. "
        "Ayu berarti baik, Ala-Ayu berarti biasa saja/campuran, dan Ala berarti buruk. "
        "Jika daftar kosong, katakan tidak ada data untuk kategori tersebut.",
    ]

    for group in groups:
        lines.append("")
        lines.append(f"{DEWASA_GROUP_LABELS[group]}:")

        items = results.get(group, [])

        if not items:
            lines.append("- Tidak ada data.")
            continue

        for index, item in enumerate(items[:40], start=1):
            lines.append(
                f"{index}. {item['date']} - {item['title']}: {item['note']}"
            )

        if len(items) > 40:
            lines.append(f"... dan {len(items) - 40} data lainnya.")

    return "\n".join(lines)


def build_dewasa_direct_answer(query):
    if not is_dewasa_search_question(query):
        return None

    category, ceremony = resolve_dewasa_ceremony(query)

    if not ceremony:
        return (
            "Nama upacara/kegiatan belum ditemukan pada data Dewasa Ayu. "
            "Coba tulis nama upacara sesuai pilihan di fitur Dewasa Ayu."
        )

    month, year = get_month_year_from_text(query)

    if not year:
        return (
            "Tahun belum disebutkan. Tulis bulan dan tahun, atau tahun saja, "
            "misalnya Juni 1900 atau tahun 1900."
        )

    groups = resolve_dewasa_groups(query) or ["ayu", "dipakai", "ala"]
    results = search_dewasa_for_period(category, ceremony, month, year)
    period_label = f"{MONTHS[month - 1]} {year}" if month else f"tahun {year}"
    lines = [
        f"Hasil Dewasa untuk {ceremony} pada {period_label}:",
        f"Jenis Yadnya: {category}",
        "",
    ]

    for group in groups:
        lines.append(f"{DEWASA_GROUP_LABELS[group]}:")
        items = results.get(group, [])

        if not items:
            lines.append("- Tidak ada data.")
            lines.append("")
            continue

        for index, item in enumerate(items, start=1):
            lines.append(f"{index}. {item['date']} - {item['title']}")

            if item.get("note"):
                lines.append(f"   {item['note']}")

        lines.append("")

    lines.append(
        "Keterangan: Ayu berarti baik, Ala-Ayu berarti biasa saja/campuran, "
        "dan Ala berarti buruk."
    )

    return "\n".join(lines).strip()


def extract_latest_date(messages, ai_resolved_date=None):
    if ai_resolved_date:
        return ai_resolved_date

    for message in reversed(messages):
        if message["role"] != "user":
            continue

        date_value = extract_date_from_text(message["content"])

        if date_value:
            return date_value

    return None


def is_calendar_question(messages):
    latest_user_message = get_latest_user_message(messages).lower()

    return bool(extract_date_from_text(latest_user_message)) or any(
        keyword in latest_user_message
        for keyword in CALENDAR_KEYWORDS
    )


def build_chat_database_context(messages, ai_resolved_date=None):
    latest_user_message = get_latest_user_message(messages)
    tanggal = extract_latest_date(messages, ai_resolved_date)
    knowledge_context = build_knowledge_context(latest_user_message)
    dewasa_context = build_dewasa_context(latest_user_message)
    monthly_calendar_context = build_monthly_calendar_context(latest_user_message)

    if not tanggal:
        if monthly_calendar_context:
            return (
                f"KONTEKS KALENDER BULANAN:\n{monthly_calendar_context}\n\n"
                f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
            )

        if dewasa_context:
            return (
                f"KONTEKS DEWASA AYU:\n{dewasa_context}\n\n"
                f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
            )

        return (
            "Tidak ada tanggal spesifik yang disebutkan pengguna. Jika jawaban "
            "membutuhkan data kalender, minta pengguna menyebutkan tanggal "
            "dengan cara yang jelas, misalnya 22 Juni 2026, besok, atau 22/06/2026.\n\n"
            f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
        )

    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError:
        return f"Tanggal {tanggal} tidak valid."

    data_bali = get_kalender_by_date(tanggal)

    if not data_bali:
        return (
            f"Database tidak memiliki data kalender untuk tanggal {tanggal}. "
            "Sampaikan hal ini dengan jelas dan jangan mengarang detail."
        )

    context = {
        "tanggal_diminta": tanggal,
        "sumber": {
            "kalender_bali": data_bali,
        },
    }

    return (
        "Gunakan data database berikut sebagai sumber utama untuk menjawab "
        "pertanyaan tentang tanggal tersebut. Jika suatu informasi tidak ada, "
        "katakan bahwa datanya tidak tersedia. Jangan mengarang.\n"
        f"{json.dumps(context, ensure_ascii=False)}\n\n"
        f"KONTEKS DEWASA AYU:\n{dewasa_context or 'Tidak ada pencarian Dewasa Ayu khusus.'}\n\n"
        f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
    )
