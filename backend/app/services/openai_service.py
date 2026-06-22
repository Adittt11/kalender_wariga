import json
import ssl
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import certifi

from app.config import OPENAI_API_KEY, OPENAI_MODEL

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"


def supports_custom_temperature(model_name):
    return not str(model_name or "").startswith("gpt-5")


def request_openai(messages, max_completion_tokens=500, temperature=0.4, model=None):
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY belum diisi di file .env")

    selected_model = model or OPENAI_MODEL
    payload = {
        "model": selected_model,
        "messages": messages,
        "max_completion_tokens": max_completion_tokens,
    }

    if temperature is not None and supports_custom_temperature(selected_model):
        payload["temperature"] = temperature

    request = Request(
        OPENAI_CHAT_COMPLETIONS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "kalender-wariga/1.0",
        },
        method="POST",
    )

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        with urlopen(request, timeout=30, context=ssl_context) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API gagal ({error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Tidak dapat terhubung ke OpenAI API: {error.reason}") from error

    try:
        return result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, AttributeError) as error:
        raise RuntimeError("Respons OpenAI API tidak memiliki teks hasil") from error


def parse_json_response(raw_text):
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()

        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    return json.loads(cleaned)


def interpret_calendar_date(user_text):
    reference_date = datetime.now(ZoneInfo("Asia/Makassar")).date().isoformat()
    raw_result = request_openai(
        [
            {
                "role": "system",
                "content": (
                    "Ubah tanggal yang disebutkan pengguna menjadi JSON valid. "
                    "Gunakan tanggal referensi Asia/Makassar: "
                    f"{reference_date}. "
                    "Jika ada tanggal jelas, balas hanya JSON seperti "
                    '{"date":"YYYY-MM-DD"}. Jika tidak ada tanggal jelas, balas '
                    '{"date":null}. Jangan menambah teks lain.'
                ),
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
        max_completion_tokens=80,
        temperature=0,
    )

    try:
        parsed = parse_json_response(raw_result)
        date_value = parsed.get("date")

        if not date_value:
            return None

        datetime.strptime(date_value, "%Y-%m-%d")
        return date_value
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
        return None


def chat_wariga(messages, database_context, model=None):
    safe_messages = [
        {
            "role": "system",
            "content": (
                "Anda adalah asisten Tanya Wariga AI. Jawab dalam bahasa "
                "Indonesia dengan ramah, ringkas, dan mudah dipahami. Anda "
                "hanya boleh menjawab topik kalender Bali dan Wariga, seperti "
                "wewaran, dewasa ayu, pakakalan, dawuh, sasih, purnama, tilem, "
                "karakter kelahiran berdasarkan Wariga, serta pengetahuan yang "
                "di-upload admin seperti Penglukatan, Pembayuhan, Tenung, "
                "Permata, Lontar, dan pengetahuan tradisi Bali lain. Tolak secara "
                "singkat pertanyaan di luar ruang lingkup tersebut. Jika "
                "pertanyaan membutuhkan data kalender "
                "spesifik yang tidak diberikan, jelaskan bahwa pengguna perlu "
                "menyebutkan tanggal dengan jelas, misalnya 22 Juni 2026 atau "
                "besok, atau membuka fitur kalender. Jangan "
                "mengarang fakta dan jangan menyatakan interpretasi tradisi "
                "sebagai kepastian mutlak. Jangan gunakan format Markdown, "
                "jangan gunakan tanda bintang, dan jangan menebalkan teks. "
                "Jika membuat daftar, gunakan baris biasa dengan angka atau "
                "tanda hubung tanpa simbol bintang. Untuk pertanyaan Dewasa, "
                "gunakan istilah Ayu untuk baik, Ala-Ayu untuk biasa saja atau "
                "campuran, dan Ala untuk buruk.\n\n"
                f"KONTEKS DATABASE BACKEND:\n{database_context}"
            ),
        },
    ]
    safe_messages.extend(messages[-10:])

    return request_openai(
        safe_messages,
        max_completion_tokens=1400,
        temperature=0.5,
        model=model,
    )
