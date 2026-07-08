import json
import ssl
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import certifi

from app.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDING_MODEL

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"


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
                "Indonesia dengan ramah, natural, tidak kaku, ringkas, dan mudah dipahami. Anda "
                "hanya boleh menjawab topik kalender Bali dan Wariga, seperti "
                "wewaran, dewasa ayu, pakakalan, dawuh, sasih, purnama, tilem, "
                "karakter kelahiran berdasarkan Wariga, serta pengetahuan yang "
                "di-upload admin seperti Penglukatan, Pembayuhan/Pebayuhan, Tenung, "
                "Permata, Lontar, dan pengetahuan tradisi Bali lain. Tolak secara "
                "singkat pertanyaan di luar ruang lingkup tersebut. Jika "
                "konteks memuat INTENT SEPARATOR, gunakan intent tersebut untuk "
                "memahami maksud pertanyaan pengguna dan memilih bagian konteks "
                "yang paling relevan. Jika konteks berisi hasil database, jadikan "
                "data itu sebagai sumber utama. "
                "Jika pertanyaan pengguna meminta lebih dari satu hal dan konteks "
                "memuat beberapa bagian, jawab semua bagian yang diminta secara "
                "terpisah dan ringkas. "
                "Jika pesan terakhir pengguna hanya meminta jawaban lebih lengkap, "
                "lebih detail, lebih singkat, kesimpulan, bentuk paragraf, "
                "penjabaran, pengembangan, penyesuaian gaya, atau lanjutan, "
                "gunakan konteks percakapan sebelumnya dan jangan menolaknya "
                "sebagai topik di luar Wariga. Ikuti gaya yang diminta pengguna, "
                "misalnya diringkas, disimpulkan, dibuat paragraf, atau dijabarkan. "
                "Boleh merapikan jawaban agar terdengar seperti percakapan, tetapi "
                "jangan mengubah fakta, tanggal, nama wuku, wewaran, atau status "
                "Dewasa dari database. Jika data belum cukup, minta pengguna "
                "melengkapi informasi yang kurang secara singkat. Jika "
                "pengguna menyebut pembayuhan atau pebayuhan, pahami keduanya "
                "sebagai istilah yang sama dan gunakan konteks Pembayuhan/Pebayuhan "
                "bila tersedia. Jika "
                "pengguna menanyakan pertemuan lanang istri, pahami lanang sebagai "
                "laki-laki dan istri sebagai perempuan/pasangan istri; gunakan "
                "tanggal lahir masing-masing dan konteks Pertemuan Lanang Istri "
                "bila tersedia. Jika "
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
        max_completion_tokens=4000,
        temperature=0.5,
        model=model,
    )


def request_openai_embeddings(text_value, model=None):
    selected_model = model or OPENAI_EMBEDDING_MODEL
    payload = {
        "model": selected_model,
        "input": text_value,
    }

    request = Request(
        OPENAI_EMBEDDINGS_URL,
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
        raise RuntimeError(f"OpenAI Embeddings API gagal ({error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Tidak dapat terhubung ke OpenAI API: {error.reason}") from error

    try:
        return result["data"][0]["embedding"]
    except (KeyError, IndexError, AttributeError, TypeError) as error:
        raise RuntimeError("Respons OpenAI Embeddings API tidak memiliki data embedding") from error
