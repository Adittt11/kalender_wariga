import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.config import OPENAI_MINI_MODEL
from app.services.openai_service import parse_json_response, request_openai


ALLOWED_INTENTS = {
    "kalender_tanggal",
    "karakter_kelahiran",
    "dewasa_ayu",
    "hari_raya_bulanan",
    "pertemuan_lanang_istri",
    "makna_wuku",
    "makna_wewaran",
    "penglukatan",
    "pembayuhan",
    "pebayuhan",
    "knowledge_umum",
    "tidak_relevan",
}

MONTHS = {
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

DATE_PATTERN = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
LOCAL_DATE_PATTERN = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b")
MONTH_NAME_PATTERN = re.compile(
    r"\b(\d{1,2})\s+"
    r"(januari|jan|februari|feb|maret|mar|april|apr|mei|juni|jun|juli|jul|"
    r"agustus|agu|agt|september|sep|oktober|okt|november|nov|desember|des)"
    r"\s+(\d{4})\b",
    re.IGNORECASE,
)
YEAR_PATTERN = re.compile(r"\b(18\d{2}|19\d{2}|20\d{2}|21\d{2})\b")


def normalize_search_text(value):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(value).lower())).strip()


def format_valid_date(year, month, day):
    try:
        return datetime(int(year), int(month), int(day)).date().isoformat()
    except (TypeError, ValueError):
        return None


def extract_date_from_text(text_value):
    match = DATE_PATTERN.search(text_value)

    if match:
        year, month, day = match.groups()
        return format_valid_date(year, month, day)

    match = LOCAL_DATE_PATTERN.search(text_value)

    if match:
        day, month, year = match.groups()
        return format_valid_date(year, month, day)

    match = MONTH_NAME_PATTERN.search(text_value)

    if match:
        day, month_name, year = match.groups()
        return format_valid_date(year, MONTHS.get(month_name.lower()), day)

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


def extract_dates_from_text(text_value):
    matches = []

    for match in DATE_PATTERN.finditer(text_value):
        year, month, day = match.groups()
        date_value = format_valid_date(year, month, day)

        if date_value:
            matches.append((match.start(), date_value))

    for match in LOCAL_DATE_PATTERN.finditer(text_value):
        day, month, year = match.groups()
        date_value = format_valid_date(year, month, day)

        if date_value:
            matches.append((match.start(), date_value))

    for match in MONTH_NAME_PATTERN.finditer(text_value):
        day, month_name, year = match.groups()
        date_value = format_valid_date(year, MONTHS.get(month_name.lower()), day)

        if date_value:
            matches.append((match.start(), date_value))

    ordered_dates = []

    for _, date_value in sorted(matches, key=lambda item: item[0]):
        if date_value not in ordered_dates:
            ordered_dates.append(date_value)

    relative_date = extract_date_from_text(text_value)

    if relative_date and relative_date not in ordered_dates:
        ordered_dates.append(relative_date)

    return ordered_dates


def extract_month_year_from_text(text_value):
    lowered = text_value.lower()
    year_match = YEAR_PATTERN.search(lowered)

    if not year_match:
        return None, None

    year = int(year_match.group(1))

    for month_name, month_number in sorted(
        MONTHS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if re.search(rf"\b{re.escape(month_name)}\b", lowered):
            return month_number, year

    return None, year


def normalize_intent_payload(payload, user_text):
    if not isinstance(payload, dict):
        payload = {}

    intent = str(payload.get("intent") or "").strip().lower()

    if intent == "pebayuhan":
        intent = "pembayuhan"

    if intent not in ALLOWED_INTENTS:
        intent = fallback_intent(user_text)["intent"]

    date_value = payload.get("date")
    if date_value:
        date_parts = str(date_value).split("-")
        date_value = format_valid_date(*date_parts) if len(date_parts) == 3 else None

    if not date_value:
        date_value = extract_date_from_text(user_text)

    date_lanang = (
        payload.get("date_lanang")
        or payload.get("tanggal_lanang")
        or payload.get("lanang_date")
        or payload.get("male_date")
    )
    date_istri = (
        payload.get("date_istri")
        or payload.get("tanggal_istri")
        or payload.get("istri_date")
        or payload.get("female_date")
    )

    for local_name in ("date_lanang", "date_istri"):
        local_value = date_lanang if local_name == "date_lanang" else date_istri

        if local_value:
            date_parts = str(local_value).split("-")
            local_value = format_valid_date(*date_parts) if len(date_parts) == 3 else None

        if local_name == "date_lanang":
            date_lanang = local_value
        else:
            date_istri = local_value

    extracted_dates = extract_dates_from_text(user_text)

    if not date_lanang and extracted_dates:
        date_lanang = extracted_dates[0]

    if not date_istri and len(extracted_dates) > 1:
        date_istri = extracted_dates[1]

    month = payload.get("month")
    year = payload.get("year")

    try:
        month = int(month) if month is not None else None
    except (TypeError, ValueError):
        month = None

    try:
        year = int(year) if year is not None else None
    except (TypeError, ValueError):
        year = None

    if not month or not year:
        fallback_month, fallback_year = extract_month_year_from_text(user_text)
        month = month or fallback_month
        year = year or fallback_year

    if month is not None and (month < 1 or month > 12):
        month = None

    list_fields = {}
    for field in ("aspects", "requested_fields", "tables_needed", "missing_fields"):
        value = payload.get(field)
        if isinstance(value, list):
            list_fields[field] = [str(item).strip() for item in value if str(item).strip()]
        else:
            list_fields[field] = []

    try:
        confidence = float(payload.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0

    return {
        "intent": intent,
        "date": date_value,
        "date_lanang": date_lanang,
        "date_istri": date_istri,
        "month": month,
        "year": year,
        "ceremony": str(payload.get("ceremony") or "").strip() or None,
        "topic": str(payload.get("topic") or "").strip() or None,
        "aspects": list_fields["aspects"],
        "requested_fields": list_fields["requested_fields"],
        "tables_needed": list_fields["tables_needed"],
        "missing_fields": list_fields["missing_fields"],
        "confidence": max(0.0, min(confidence, 1.0)),
        "normalized_question": str(payload.get("normalized_question") or user_text).strip(),
    }


def fallback_intent(user_text):
    normalized = normalize_search_text(user_text)
    date_value = extract_date_from_text(user_text)
    extracted_dates = extract_dates_from_text(user_text)
    month, year = extract_month_year_from_text(user_text)

    if any(
        word in normalized
        for word in (
            "pertemuan lanang istri",
            "lanang istri",
            "lanang lan istri",
            "laki perempuan",
            "laki laki perempuan",
            "suami istri",
            "pasangan",
            "jodoh",
            "kecocokan",
        )
    ):
        intent = "pertemuan_lanang_istri"
    elif (
        any(
            word in normalized
            for word in (
                "pembayuhan",
                "pebayuhan",
                "pebayuah",
                "bayuh",
                "bayuhan",
            )
        )
        and not any(word in normalized for word in ("karakter", "sifat", "watak"))
    ):
        intent = "pembayuhan"
    elif any(word in normalized for word in ("lahir", "kelahiran", "sifat", "karakter", "watak")):
        intent = "karakter_kelahiran"
    elif any(
        word in normalized
        for word in (
            "dewasa",
            "hari baik",
            "hari buruk",
            "tanggal baik",
            "tanggal buruk",
            "tanggal ayu",
            "tanggal ala",
            "hari cocok",
            "tanggal cocok",
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
            "bersih diri",
            "pelantikan",
            "pawintenan",
            "mawinten",
        )
    ):
        intent = "dewasa_ayu"
    elif any(
        word in normalized
        for word in (
            "hari raya",
            "hari raya hindu",
            "rahinan",
            "purnama",
            "tilem",
            "odalan",
            "piodalan",
            "hari nasional",
            "hari non bali",
            "libur nasional",
            "nasional",
        )
    ) and month and year:
        intent = "hari_raya_bulanan"
    elif "wuku" in normalized:
        intent = "makna_wuku"
    elif any(word in normalized for word in ("wewaran", "pancawara", "saptawara")):
        intent = "makna_wewaran"
    elif any(word in normalized for word in ("penglukatan", "melukat", "lukat")):
        intent = "penglukatan"
    elif any(
        word in normalized
        for word in (
            "pembayuhan",
            "pebayuhan",
            "pebayuah",
            "bayuh",
            "bayuhan",
        )
    ):
        intent = "pembayuhan"
    elif date_value:
        intent = "kalender_tanggal"
    elif any(word in normalized for word in ("wariga", "kalender bali", "lontar", "tenung", "permata")):
        intent = "knowledge_umum"
    else:
        intent = "tidak_relevan"

    return normalize_intent_payload(
        {
            "intent": intent,
            "date": date_value,
            "date_lanang": extracted_dates[0] if extracted_dates else None,
            "date_istri": extracted_dates[1] if len(extracted_dates) > 1 else None,
            "month": month,
            "year": year,
            "confidence": 0.45,
            "normalized_question": user_text,
        },
        user_text,
    )


def classify_chat_intent(user_text, model=None):
    normalized_user_text = str(user_text or "").strip()

    if not normalized_user_text:
        return fallback_intent(normalized_user_text)

    reference_date = datetime.now(ZoneInfo("Asia/Makassar")).date().isoformat()
    schema_hint = {
        "intent": "kalender_tanggal | karakter_kelahiran | dewasa_ayu | hari_raya_bulanan | pertemuan_lanang_istri | makna_wuku | makna_wewaran | penglukatan | pembayuhan | knowledge_umum | tidak_relevan",
        "date": "YYYY-MM-DD atau null",
        "date_lanang": "YYYY-MM-DD tanggal lahir laki-laki/lanang atau null",
        "date_istri": "YYYY-MM-DD tanggal lahir perempuan/istri atau null",
        "month": "1-12 atau null",
        "year": "YYYY atau null",
        "ceremony": "nama upacara/kegiatan atau null",
        "topic": "topik utama atau null",
        "aspects": ["wuku", "pancawara", "saptawara", "palalintangan"],
        "requested_fields": ["field database yang diminta"],
        "tables_needed": ["kalender_bali", "dewasa", "makna_4aspek"],
        "missing_fields": ["date", "month", "year", "ceremony"],
        "confidence": 0.0,
        "normalized_question": "versi pertanyaan yang dirapikan",
    }

    try:
        raw_result = request_openai(
            [
                {
                    "role": "system",
                    "content": (
                        "Anda adalah Intent Separator untuk chatbot Kalender Bali dan Wariga. "
                        "Tugas Anda hanya mengubah pertanyaan bebas pengguna menjadi JSON valid. "
                        "Pahami bahasa Indonesia santai, typo ringan, sinonim, dan istilah Bali. "
                        "Jangan menjawab pertanyaan pengguna. Jangan memakai Markdown. "
                        f"Tanggal referensi Asia/Makassar: {reference_date}. "
                        "Gunakan intent 'tidak_relevan' untuk topik di luar kalender Bali, Wariga, "
                        "Dewasa Ayu, kelahiran, pembayuhan atau pebayuhan, penglukatan, lontar, permata, tenung, "
                        "atau knowledge tradisi Bali. "
                        "Untuk pertanyaan lahir/sifat/watak, gunakan intent karakter_kelahiran. "
                        "Untuk pertanyaan pertemuan lanang istri, kecocokan pasangan, "
                        "laki-laki dan perempuan, suami istri, atau jodoh yang memuat dua "
                        "tanggal lahir, gunakan intent pertemuan_lanang_istri. "
                        "Tanggal laki-laki/lanang masukkan ke date_lanang dan tanggal "
                        "perempuan/istri masukkan ke date_istri. "
                        "Untuk cari hari baik/buruk upacara, gunakan intent dewasa_ayu. "
                        "Untuk pertanyaan pembayuhan, pebayuhan, bayuh, atau bayuhan, gunakan intent pembayuhan. "
                        "Untuk daftar rahinan/hari raya/libur dalam bulan tertentu, gunakan hari_raya_bulanan. "
                        "Untuk pertanyaan hari nasional, hari non Bali, libur nasional, "
                        "hari raya Hindu, rahinan, purnama, tilem, kajeng kliwon, atau "
                        "piodalan pada bulan tertentu, gunakan intent hari_raya_bulanan. "
                        "Balas hanya JSON dengan bentuk berikut: "
                        f"{json.dumps(schema_hint, ensure_ascii=False)}"
                    ),
                },
                {
                    "role": "user",
                    "content": normalized_user_text,
                },
            ],
            max_completion_tokens=500,
            temperature=0,
            model=model or OPENAI_MINI_MODEL,
        )
        return normalize_intent_payload(parse_json_response(raw_result), normalized_user_text)
    except Exception:
        return fallback_intent(normalized_user_text)
