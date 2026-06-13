import json
import re
from datetime import datetime

from app.services.kalender_bali_service import get_kalender_bali_by_date
from app.services.kalender_service import get_kalender_by_date
from app.services.knowledge_service import build_knowledge_context


DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
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


def extract_latest_date(messages):
    for message in reversed(messages):
        if message["role"] != "user":
            continue

        match = DATE_PATTERN.search(message["content"])

        if match:
            return match.group(1)

    return None


def is_calendar_question(messages):
    latest_user_message = next(
        (
            message["content"].lower()
            for message in reversed(messages)
            if message["role"] == "user"
        ),
        "",
    )

    return bool(DATE_PATTERN.search(latest_user_message)) or any(
        keyword in latest_user_message
        for keyword in CALENDAR_KEYWORDS
    )


def build_chat_database_context(messages):
    latest_user_message = next(
        (
            message["content"]
            for message in reversed(messages)
            if message["role"] == "user"
        ),
        "",
    )
    tanggal = extract_latest_date(messages)
    knowledge_context = build_knowledge_context(latest_user_message)

    if not tanggal:
        return (
            "Tidak ada tanggal spesifik yang disebutkan pengguna. Jika jawaban "
            "membutuhkan data kalender, minta pengguna menulis tanggal dengan "
            "format YYYY-MM-DD.\n\n"
            f"KONTEKS KNOWLEDGE UPLOAD:\n{knowledge_context}"
        )

    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError:
        return f"Tanggal {tanggal} tidak valid."

    data_dawuh = get_kalender_by_date(tanggal)
    data_bali = get_kalender_bali_by_date(tanggal)

    if not data_dawuh and not data_bali:
        return (
            f"Database tidak memiliki data kalender untuk tanggal {tanggal}. "
            "Sampaikan hal ini dengan jelas dan jangan mengarang detail."
        )

    context = {
        "tanggal_diminta": tanggal,
        "sumber": {
            "kalender_dawuh": data_dawuh,
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
