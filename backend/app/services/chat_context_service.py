import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.services.kalender_service import get_kalender_by_date
from app.services.knowledge_service import build_knowledge_context


DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
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
    "wuku",
    "wewaran",
    "dewasa ayu",
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
)


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

    if not tanggal:
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
        f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
    )
