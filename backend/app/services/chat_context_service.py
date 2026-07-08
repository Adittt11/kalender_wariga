import json
import re
from datetime import datetime, timedelta
from difflib import get_close_matches
from zoneinfo import ZoneInfo

from sqlalchemy import text

from app.services.dewasa_ayu_service import MONTHS, get_dewasa_options, search_dewasa
from app.services.database import engine
from app.services.kalender_service import get_kalender_by_date, get_kalender_by_month
from app.services.knowledge_service import build_knowledge_context
from app.services.pebayuhan_service import get_pebayuhan_by_lahir, get_pebayuhan_by_wewaran
from app.services.pertemuan_service import calculate_pertemuan_lanang_istri


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
    "pebayuhan",
    "pebayuah",
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
    "pertemuan",
    "lanang istri",
    "laki perempuan",
    "laki-laki",
    "perempuan",
    "suami istri",
    "pasangan",
    "jodoh",
    "kecocokan",
)
DEWASA_QUERY_KEYWORDS = (
    "hari baik",
    "hari buruk",
    "hari biasa",
    "tanggal baik",
    "tanggal buruk",
    "tanggal ayu",
    "tanggal ala",
    "tanggal cocok",
    "hari cocok",
    "baik buruk",
    "baik dan buruk",
    "keduanya",
    "dewasa",
    "dewasa ayu",
    "ala ayu",
    "ala-ayu",
    "pawiwahan",
    "nikah",
    "nikahan",
    "pernikahan",
    "perkawinan",
    "metatah",
    "mepandes",
    "potong gigi",
    "potong rambut",
    "cukur rambut",
    "mepetik",
    "penyucian diri",
    "penyucian raga",
    "pelantikan",
    "pawintenan",
    "mawinten",
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
CEREMONY_SYNONYMS = {
    "pawiwahan": ("nikah", "menikah", "nikahan", "perkawinan", "pernikahan", "kawin"),
    "metatah": ("potong gigi", "mepandes", "mesangih"),
    "mepandes": ("potong gigi", "metatah", "mesangih"),
    "mepetik": ("potong rambut", "cukur rambut", "mecukur", "mepetik rambut"),
    "nelu bulanin": ("tiga bulanan", "nelubulanin", "bayi tiga bulan"),
    "melas rare": ("bayi", "anak bayi", "anak kecil", "rare", "upacara bayi"),
    "rare": ("bayi", "anak bayi", "anak kecil", "melas rare"),
    "penyucian raga": ("penyucian diri", "bersih diri", "pembersihan diri", "melukat", "penglukatan"),
    "pasawitrayan": ("pawintenan", "mawinten", "winten", "penyucian rohani"),
    "madwijati": ("dwijati", "sulinggih", "pedanda", "diksa"),
    "pelantikan pejabat": ("pelantikan", "dilantik", "jabatan", "pejabat"),
    "pesamuan desa": ("rapat desa", "paruman desa", "sangkep desa", "pesamuan"),
    "mekarya perkumpulan": ("membuat perkumpulan", "mendirikan organisasi", "membuat organisasi", "perkumpulan"),
    "mamula tebu miwah ketimun": ("menanam tebu", "menanam ketimun", "tebu", "ketimun"),
    "yadnya kawisesan": ("kawisesan", "yadnya khusus"),
    "salwiring manusa yadnya": ("manusa yadnya", "upacara manusia", "upacara manusa yadnya"),
    "melukat": ("penglukatan", "lukat", "pembersihan diri"),
    "penglukatan": ("melukat", "lukat", "pembersihan diri"),
    "pembayuhan": ("bayuh", "bayuhan", "bayuh oton"),
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


def get_previous_user_message(messages):
    seen_latest = False

    for message in reversed(messages):
        if message["role"] != "user":
            continue

        if not seen_latest:
            seen_latest = True
            continue

        return message["content"]

    return ""


def is_followup_instruction(text_value):
    normalized = normalize_search_text(text_value)

    if not normalized:
        return False

    followup_phrases = (
        "jawab lengkap",
        "jawab secara lengkap",
        "jelaskan lengkap",
        "lebih lengkap",
        "lengkapkan",
        "detailkan",
        "lebih detail",
        "jelaskan detail",
        "jawab singkat",
        "lebih singkat",
        "ringkas",
        "lanjut",
        "lanjutkan",
        "teruskan",
        "maksudnya",
        "jelaskan lagi",
    )

    return any(phrase in normalized for phrase in followup_phrases)


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

    for canonical, synonyms in CEREMONY_SYNONYMS.items():
        if canonical not in normalized_message and not any(
            synonym in normalized_message for synonym in synonyms
        ):
            continue

        for category, ceremony, normalized_ceremony in candidates:
            if canonical in normalized_ceremony or any(
                normalize_search_text(synonym) in normalized_ceremony
                for synonym in synonyms
            ):
                return category, ceremony

    candidate_names = [item[2] for item in candidates if item[2]]
    close_matches = get_close_matches(normalized_message, candidate_names, n=1, cutoff=0.72)

    if close_matches:
        matched_name = close_matches[0]

        for category, ceremony, normalized_ceremony in candidates:
            if normalized_ceremony == matched_name:
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


def build_monthly_calendar_context(query, month=None, year=None, field_name=None):
    field_name = field_name or resolve_monthly_calendar_field(query)

    if not field_name:
        return None

    parsed_month, parsed_year = get_month_year_from_text(query)
    month = month or parsed_month
    year = year or parsed_year

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
        "Wajib tampilkan semua item yang ada pada daftar, jangan hanya memberi satu contoh "
        "dan jangan mengurangi jumlah tanggal kecuali pengguna meminta ringkasan. "
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


def get_intent_value(intent_info, field, fallback=None):
    if not isinstance(intent_info, dict):
        return fallback

    value = intent_info.get(field)
    return value if value not in ("", None, []) else fallback


def build_intent_summary(intent_info):
    if not isinstance(intent_info, dict):
        return "Intent tidak tersedia; gunakan fallback rule backend."

    serializable = {
        "intent": intent_info.get("intent"),
        "date": intent_info.get("date"),
        "date_lanang": intent_info.get("date_lanang"),
        "date_istri": intent_info.get("date_istri"),
        "month": intent_info.get("month"),
        "year": intent_info.get("year"),
        "ceremony": intent_info.get("ceremony"),
        "topic": intent_info.get("topic"),
        "aspects": intent_info.get("aspects") or [],
        "requested_fields": intent_info.get("requested_fields") or [],
        "tables_needed": intent_info.get("tables_needed") or [],
        "missing_fields": intent_info.get("missing_fields") or [],
        "confidence": intent_info.get("confidence"),
    }

    return json.dumps(serializable, ensure_ascii=False)


def find_wuku_context(query):
    normalized = normalize_search_text(query)

    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT "Wuku", "Keterangan"
                FROM keterangan_wuku
                ORDER BY "Wuku"
            """)
        ).mappings().all()

    matches = []

    for row in rows:
        wuku = str(row.get("Wuku") or "").strip()

        if wuku and normalize_search_text(wuku) in normalized:
            matches.append(dict(row))

    if not matches:
        return None

    lines = [
        "KONTEKS MAKNA WUKU:",
        "Gunakan data dari tabel keterangan_wuku berikut sebagai sumber utama.",
    ]

    for item in matches:
        lines.append(f"- Wuku {item['Wuku']}: {item['Keterangan']}")

    return "\n".join(lines)


def find_wewaran_context(query):
    normalized = normalize_search_text(query)
    matches = []

    with engine.connect() as conn:
        ps_rows = conn.execute(
            text("""
                SELECT pancawara, keterangan_pancawara, saptawara, keterangan_saptawara
                FROM keterangan_pancawara_saptawara
            """)
        ).mappings().all()
        wariga_rows = conn.execute(
            text("""
                SELECT "Nama Wewaran", "Nama hari", "Urip", "Arah_wewaran",
                       "Dewa_wewaran", "Keterangan"
                FROM daftar_wariga
            """)
        ).mappings().all()

    for row in ps_rows:
        pancawara = str(row.get("pancawara") or "").strip()
        saptawara = str(row.get("saptawara") or "").strip()

        if pancawara and normalize_search_text(pancawara) in normalized:
            matches.append(
                f"Pancawara {pancawara}: {row.get('keterangan_pancawara') or '-'}"
            )

        if saptawara and normalize_search_text(saptawara) in normalized:
            matches.append(
                f"Saptawara {saptawara}: {row.get('keterangan_saptawara') or '-'}"
            )

    for row in wariga_rows:
        nama_hari = str(row.get("Nama hari") or "").strip()

        if nama_hari and normalize_search_text(nama_hari) in normalized:
            matches.append(
                " | ".join(
                    [
                        f"{row.get('Nama Wewaran') or 'Wewaran'} {nama_hari}",
                        f"Urip: {row.get('Urip') or '-'}",
                        f"Arah: {row.get('Arah_wewaran') or '-'}",
                        f"Dewa: {row.get('Dewa_wewaran') or '-'}",
                        f"Keterangan: {row.get('Keterangan') or '-'}",
                    ]
                )
            )

    if not matches:
        return None

    return (
        "KONTEKS MAKNA WEWARAN:\n"
        "Gunakan data dari tabel keterangan_pancawara_saptawara dan daftar_wariga berikut.\n"
        + "\n".join(f"- {item}" for item in matches[:12])
    )


def build_date_database_context(tanggal, intent_name=None, aspects=None):
    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except (TypeError, ValueError):
        return f"Tanggal {tanggal} tidak valid."

    data_bali = get_kalender_by_date(tanggal, aspects=aspects)

    if not data_bali:
        return (
            f"Database tidak memiliki data kalender untuk tanggal {tanggal}. "
            "Sampaikan hal ini dengan jelas dan jangan mengarang detail."
        )

    source_tables = ["kalender_bali"]

    if intent_name in ("karakter_kelahiran", "makna_wuku", "makna_wewaran"):
        source_tables.extend(
            [
                "makna_4aspek",
                "keterangan_wuku",
                "keterangan_pancawara_saptawara",
            ]
        )

    context = {
        "tanggal_diminta": tanggal,
        "intent": intent_name or "kalender_tanggal",
        "sumber_tabel": source_tables,
        "data": data_bali,
    }

    if intent_name == "karakter_kelahiran":
        instruction = (
            "PERTANYAAN KARAKTER KELAHIRAN TERDETEKSI:\n"
            "Gunakan data kalender_bali yang sudah diperkaya dengan makna_4aspek, "
            "keterangan_wuku, dan keterangan_pancawara_saptawara. Jelaskan sebagai "
            "tafsir tradisi, bukan kepastian mutlak."
        )
    elif intent_name in ("makna_wuku", "makna_wewaran"):
        instruction = (
            "PERTANYAAN MAKNA WARIGA TERDETEKSI:\n"
            "Gunakan nilai wuku/wewaran pada tanggal tersebut dan jelaskan maknanya "
            "berdasarkan konteks database."
        )
    else:
        instruction = (
            "Gunakan data database berikut sebagai sumber utama untuk menjawab "
            "pertanyaan tentang tanggal tersebut. Jika suatu informasi tidak ada, "
            "katakan bahwa datanya tidak tersedia. Jangan mengarang."
        )

    return f"{instruction}\n{json.dumps(context, ensure_ascii=False)}"


def safe_build_knowledge_context(query):
    try:
        return build_knowledge_context(query)
    except Exception as error:
        return (
            "Knowledge upload tidak dapat diambil saat ini. "
            f"Alasan teknis: {str(error)}"
        )


def asks_pebayuhan(text_value):
    normalized = normalize_search_text(text_value)

    return any(
        keyword in normalized
        for keyword in (
            "pembayuhan",
            "pebayuhan",
            "pebayuah",
            "bayuh",
            "bayuhan",
        )
    )


def extract_pebayuhan_wewaran(text_value):
    normalized = normalize_search_text(text_value)
    saptawara_aliases = {
        "redite": "Redite",
        "minggu": "Redite",
        "soma": "Soma",
        "senin": "Soma",
        "anggara": "Anggara",
        "selasa": "Anggara",
        "buda": "Buda",
        "rabu": "Buda",
        "wraspati": "Wraspati",
        "wrespati": "Wraspati",
        "wrhaspati": "Wraspati",
        "kamis": "Wraspati",
        "sukra": "Sukra",
        "jumat": "Sukra",
        "saniscara": "Saniscara",
        "sabtu": "Saniscara",
    }
    pancawara_aliases = {
        "umanis": "Umanis",
        "manis": "Umanis",
        "paing": "Paing",
        "pahing": "Paing",
        "pon": "Pon",
        "wage": "Wage",
        "kliwon": "Kliwon",
    }

    saptawara = next(
        (
            canonical
            for alias, canonical in saptawara_aliases.items()
            if re.search(rf"\b{re.escape(alias)}\b", normalized)
        ),
        None,
    )
    pancawara = next(
        (
            canonical
            for alias, canonical in pancawara_aliases.items()
            if re.search(rf"\b{re.escape(alias)}\b", normalized)
        ),
        None,
    )

    if saptawara and pancawara:
        return saptawara, pancawara

    return None, None


def build_pebayuhan_context(tanggal, query=None):
    if not tanggal:
        saptawara, pancawara = extract_pebayuhan_wewaran(query or "")

        if saptawara and pancawara:
            result = get_pebayuhan_by_wewaran(saptawara, pancawara)
            return format_pebayuhan_context(result, source_label="Saptawara/Pancawara dari input pengguna")

        return (
            "PERTANYAAN PEMBAYUHAN/PEBAYUHAN TERDETEKSI:\n"
            "Tanggal lahir atau kombinasi Saptawara-Pancawara belum ditemukan. "
            "Minta pengguna menyebutkan tanggal lahir jelas, misalnya 01 Januari 1900, "
            "atau menyebutkan kombinasi seperti Wrespati Pon."
        )

    try:
        result = get_pebayuhan_by_lahir(tanggal)
    except ValueError as error:
        return (
            "PERTANYAAN PEMBAYUHAN/PEBAYUHAN TERDETEKSI:\n"
            f"{str(error)}. Sampaikan bahwa data pembayuhan/pebayuhan untuk tanggal tersebut "
            "belum tersedia dan jangan mengambil data pakakalan sebagai pengganti."
        )

    return format_pebayuhan_context(result, source_label="Saptawara/Pancawara dari kalender_bali")


def format_pebayuhan_context(result, source_label):
    pebayuhan_rows = result.get("pebayuhan") or []
    lines = [
        "PERTANYAAN PEMBAYUHAN/PEBAYUHAN TERDETEKSI:",
        "Pembayuhan dan Pebayuhan pada konteks ini dianggap istilah yang sama.",
        "Gunakan alur data berikut sebagai sumber utama dan jangan menggantinya dengan pakakalan, dewasa, atau knowledge umum.",
        f"Sumber kombinasi: {source_label}.",
        f"Tanggal lahir: {result.get('tanggal_lahir') or '-'}",
        f"Saptawara: {result.get('saptawara')}",
        f"Pancawara: {result.get('pancawara')}",
        "Sumber tabel: pebayuhan.",
        "",
        "Hasil tabel pebayuhan untuk Pembayuhan/Pebayuhan:",
    ]

    if not pebayuhan_rows:
        lines.append("- Tidak ada data pembayuhan/pebayuhan yang cocok untuk kombinasi Saptawara dan Pancawara tersebut.")
        return "\n".join(lines)

    for index, item in enumerate(pebayuhan_rows, start=1):
        lines.extend(
            [
                f"{index}. Kombinasi: {item.get('Saptawara') or '-'} - {item.get('Pancawara') or '-'}",
                f"   Keterangan berdasarkan Saptawara: {item.get('Keterangan') or '-'}",
                f"   Keterangan berdasarkan Pancawara: {item.get('Keterangan_1') or '-'}",
                f"   Kweh toya pancoran: {item.get('kweh_toya_pancoran') or '-'}",
            ]
        )

    return "\n".join(lines)


def build_pertemuan_lanang_istri_context(date_lanang, date_istri):
    if not date_lanang or not date_istri:
        missing = []

        if not date_lanang:
            missing.append("tanggal lahir laki-laki/lanang")

        if not date_istri:
            missing.append("tanggal lahir perempuan/istri")

        return (
            "PERTANYAAN PERTEMUAN LANANG ISTRI TERDETEKSI:\n"
            f"Data belum lengkap: {', '.join(missing)}. "
            "Minta pengguna mengisi dua tanggal lahir, misalnya: "
            "laki-laki 02 Januari 1900 dan perempuan 05 Januari 1900."
        )

    try:
        result = calculate_pertemuan_lanang_istri(date_lanang, date_istri)
    except ValueError as error:
        return (
            "PERTANYAAN PERTEMUAN LANANG ISTRI TERDETEKSI:\n"
            f"{str(error)}. Sampaikan dengan jelas dan jangan mengarang hasil."
        )

    lines = [
        "PERTANYAAN PERTEMUAN LANANG ISTRI TERDETEKSI:",
        "Lanang berarti laki-laki dan istri berarti perempuan/pasangan istri.",
        "Gunakan hasil perhitungan dari fitur Pertemuan Lanang Istri berikut sebagai sumber utama.",
        "Sumber tabel: kalender_bali dan daftar_wariga.",
        "",
        "Data Lanang / Laki-laki:",
        f"- Tanggal lahir: {result['lanang'].get('tanggal_lahir')}",
        f"- Wuku: {result['lanang'].get('wuku')}",
        f"- Saptawara: {result['lanang'].get('saptawara')}",
        f"- Sadwara: {result['lanang'].get('sadwara')}",
        f"- Pancawara: {result['lanang'].get('pancawara')}",
        f"- Total urip: {result['lanang'].get('urip', {}).get('total')}",
        "",
        "Data Istri / Perempuan:",
        f"- Tanggal lahir: {result['istri'].get('tanggal_lahir')}",
        f"- Wuku: {result['istri'].get('wuku')}",
        f"- Saptawara: {result['istri'].get('saptawara')}",
        f"- Sadwara: {result['istri'].get('sadwara')}",
        f"- Pancawara: {result['istri'].get('pancawara')}",
        f"- Total urip: {result['istri'].get('urip', {}).get('total')}",
        "",
        f"Total urip pasangan: {result.get('total_urip')}",
        "",
        "Hasil tenung per umur pernikahan:",
    ]

    for item in result.get("hasil") or []:
        lines.append(
            "- "
            f"{item.get('umur_pernikahan')}: "
            f"{item.get('posisi')} - {item.get('artinya')} "
            f"(perhitungan: {item.get('perhitungan')}, sisa: {item.get('sisa')})"
        )

    return "\n".join(lines)


def merge_dewasa_results(base, addition):
    for key in ("ayu", "dipakai", "ala"):
        base[key].extend(addition.get(key, []))

    return base


def search_dewasa_for_period(jenis_yadnya, upacara, month=None, year=None, tanggal=None):
    if tanggal:
        return search_dewasa(jenis_yadnya, upacara, tanggal=tanggal)

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


def resolve_dewasa_ceremony_from_hint(ceremony_hint):
    normalized_hint = normalize_search_text(ceremony_hint)

    if not normalized_hint:
        return None, None

    options = get_dewasa_options()
    ceremonies_by_category = options.get("ceremonies_by_category") or {}
    candidates = []

    for category, ceremonies in ceremonies_by_category.items():
        for ceremony in ceremonies:
            candidates.append((category, ceremony, normalize_search_text(ceremony)))

    for category, ceremony, normalized_ceremony in candidates:
        if normalized_hint == normalized_ceremony or normalized_hint in normalized_ceremony:
            return category, ceremony

    close_matches = get_close_matches(
        normalized_hint,
        [item[2] for item in candidates if item[2]],
        n=1,
        cutoff=0.72,
    )

    if close_matches:
        for category, ceremony, normalized_ceremony in candidates:
            if normalized_ceremony == close_matches[0]:
                return category, ceremony

    return None, None


def build_dewasa_context(query, intent_info=None):
    if not is_dewasa_search_question(query) and get_intent_value(intent_info, "intent") != "dewasa_ayu":
        return None

    category, ceremony = resolve_dewasa_ceremony(query)

    if not ceremony:
        category, ceremony = resolve_dewasa_ceremony_from_hint(
            get_intent_value(intent_info, "ceremony", "")
        )

    tanggal = get_intent_value(intent_info, "date") or extract_date_from_text(query)
    month, year = get_month_year_from_text(query)
    month = month or get_intent_value(intent_info, "month")
    year = year or get_intent_value(intent_info, "year")

    if not tanggal and not year:
        return (
            "PERTANYAAN DEWASA AYU TERDETEKSI:\n"
            "Tanggal atau tahun belum disebutkan. Minta pengguna menyebutkan tanggal "
            "spesifik, bulan dan tahun, atau tahun saja, misalnya 2 Januari 1900, "
            "Juni 1900, atau tahun 1900."
        )

    groups = resolve_dewasa_groups(query)

    if not groups:
        groups = ["ayu", "dipakai", "ala"]

    results = search_dewasa_for_period(category, ceremony, month, year, tanggal=tanggal)
    period_label = tanggal or (f"{MONTHS[month - 1]} {year}" if month else f"tahun {year}")
    lines = [
        "PERTANYAAN DEWASA AYU TERDETEKSI:",
        f"Jenis Yadnya: {category or 'Semua Yadnya'}",
        f"Upacara/Kegiatan: {ceremony or 'Semua Upacara'}",
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


def build_chat_database_context(messages, ai_resolved_date=None, intent_info=None):
    latest_user_message = get_latest_user_message(messages)
    context_query_message = latest_user_message

    if isinstance(intent_info, dict) and intent_info.get("followup_from"):
        context_query_message = (
            f"{intent_info.get('followup_from')} "
            f"{intent_info.get('followup_request') or latest_user_message}"
        ).strip()

    intent_name = get_intent_value(intent_info, "intent")
    intent_date = get_intent_value(intent_info, "date")
    tanggal = intent_date or extract_latest_date(messages, ai_resolved_date)
    aspects = get_intent_value(intent_info, "aspects", None)
    knowledge_context = safe_build_knowledge_context(context_query_message)
    dewasa_context = build_dewasa_context(context_query_message, intent_info=intent_info)
    monthly_calendar_context = build_monthly_calendar_context(
        context_query_message,
        month=get_intent_value(intent_info, "month"),
        year=get_intent_value(intent_info, "year"),
    )
    intent_summary = build_intent_summary(intent_info)
    pebayuhan_context = (
        build_pebayuhan_context(tanggal, context_query_message)
        if intent_name != "pembayuhan" and asks_pebayuhan(context_query_message)
        else None
    )
    pebayuhan_context_block = (
        "PERTANYAAN GABUNGAN TERDETEKSI:\n"
        "Pengguna meminta karakter kelahiran dan Pembayuhan/Pebayuhan. "
        "Jawab kedua bagian tersebut; jangan berhenti hanya pada karakter kelahiran.\n\n"
        f"KONTEKS PEMBAYUHAN/PEBAYUHAN:\n{pebayuhan_context}\n\n"
        if pebayuhan_context
        else ""
    )
    combined_monthly_dewasa_notice = (
        "PERTANYAAN GABUNGAN TERDETEKSI:\n"
        "Pengguna meminta data kalender bulanan dan Dewasa Ayu sekaligus. "
        "Jawab kedua bagian tersebut. Data kalender bulanan bersumber dari "
        "kalender_bali, sedangkan Dewasa Ayu bersumber dari tabel dewasa. "
        "Jangan menyatakan salah satu data belum tersedia jika konteksnya ada di bawah.\n\n"
        if monthly_calendar_context and dewasa_context
        else ""
    )
    monthly_calendar_context_block = (
        f"KONTEKS KALENDER BULANAN:\n{monthly_calendar_context}\n\n"
        if monthly_calendar_context
        else ""
    )
    dewasa_context_block = (
        f"KONTEKS DEWASA AYU:\n{dewasa_context}\n\n"
        if dewasa_context
        else ""
    )

    if intent_name == "pembayuhan":
        return (
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            f"KONTEKS PEMBAYUHAN/PEBAYUHAN:\n{build_pebayuhan_context(tanggal, context_query_message)}\n\n"
            "KONTEKS KNOWLEDGE UPLOAD TAMBAHAN:\n"
            f"{knowledge_context}"
        )

    if intent_name == "pertemuan_lanang_istri":
        return (
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            "KONTEKS PERTEMUAN LANANG ISTRI:\n"
            f"{build_pertemuan_lanang_istri_context(get_intent_value(intent_info, 'date_lanang'), get_intent_value(intent_info, 'date_istri'))}\n\n"
            "KONTEKS KNOWLEDGE UPLOAD TAMBAHAN:\n"
            f"{knowledge_context}"
        )

    if intent_name in ("penglukatan", "knowledge_umum"):
        return (
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            "KONTEKS KNOWLEDGE UPLOAD:\n"
            f"{knowledge_context}"
        )

    if intent_name == "hari_raya_bulanan" and monthly_calendar_context:
        return (
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            f"{combined_monthly_dewasa_notice}"
            f"{monthly_calendar_context_block}"
            f"{dewasa_context_block}"
            f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
        )

    if intent_name == "tidak_relevan" and monthly_calendar_context:
        return (
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            "Intent awal tidak relevan, tetapi parser kalender bulanan menemukan "
            "permintaan yang valid. Gunakan konteks kalender bulanan berikut sebagai sumber utama.\n\n"
            f"{combined_monthly_dewasa_notice}"
            f"{monthly_calendar_context_block}"
            f"{dewasa_context_block}"
            f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
        )

    if intent_name == "tidak_relevan" and dewasa_context:
        return (
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            "Intent awal tidak relevan, tetapi parser Dewasa Ayu menemukan "
            "permintaan yang valid. Gunakan konteks Dewasa Ayu berikut sebagai sumber utama.\n\n"
            f"KONTEKS DEWASA AYU:\n{dewasa_context}\n\n"
            f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
        )

    if intent_name == "tidak_relevan":
        return (
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            "Pertanyaan terdeteksi di luar ruang lingkup kalender Bali dan Wariga. "
            "Tolak dengan singkat dan arahkan pengguna menanyakan topik Wariga."
        )

    if intent_name == "dewasa_ayu":
        return (
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            f"{combined_monthly_dewasa_notice}"
            f"{monthly_calendar_context_block}"
            f"KONTEKS DEWASA AYU:\n{dewasa_context or 'Data Dewasa Ayu belum cukup untuk pertanyaan ini.'}\n\n"
            f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
        )

    if intent_name == "makna_wuku" and not tanggal:
        wuku_context = find_wuku_context(context_query_message)

        if wuku_context:
            return (
                "INTENT SEPARATOR:\n"
                f"{intent_summary}\n\n"
                f"{wuku_context}\n\n"
                f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
            )

    if intent_name == "makna_wewaran" and not tanggal:
        wewaran_context = find_wewaran_context(context_query_message)

        if wewaran_context:
            return (
                "INTENT SEPARATOR:\n"
                f"{intent_summary}\n\n"
                f"{wewaran_context}\n\n"
                f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
            )

    if not tanggal:
        if monthly_calendar_context:
            return (
                "INTENT SEPARATOR:\n"
                f"{intent_summary}\n\n"
                f"{combined_monthly_dewasa_notice}"
                f"{monthly_calendar_context_block}"
                f"{dewasa_context_block}"
                f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
            )

        if dewasa_context:
            return (
                "INTENT SEPARATOR:\n"
                f"{intent_summary}\n\n"
                f"KONTEKS DEWASA AYU:\n{dewasa_context}\n\n"
                f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
            )

        return (
            "Tidak ada tanggal spesifik yang disebutkan pengguna. Jika jawaban "
            "membutuhkan data kalender, minta pengguna menyebutkan tanggal "
            "dengan cara yang jelas, misalnya 22 Juni 2026, besok, atau 22/06/2026.\n\n"
            "INTENT SEPARATOR:\n"
            f"{intent_summary}\n\n"
            f"{pebayuhan_context_block}"
            f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
        )

    return (
        "INTENT SEPARATOR:\n"
        f"{intent_summary}\n\n"
        f"{pebayuhan_context_block}"
        f"{build_date_database_context(tanggal, intent_name, aspects)}\n\n"
        f"KONTEKS DEWASA AYU:\n{dewasa_context or 'Tidak ada pencarian Dewasa Ayu khusus.'}\n\n"
        f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
    )
