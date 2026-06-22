import json
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi

from app.config import OPENAI_API_KEY, OPENAI_MODEL

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"


def request_openai(messages, max_completion_tokens=500, temperature=0.4):
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY belum diisi di file .env")

    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_completion_tokens,
    }
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


def chat_wariga(messages, database_context):
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
                "menyebutkan tanggal atau membuka fitur kalender. Jangan "
                "mengarang fakta dan jangan menyatakan interpretasi tradisi "
                "sebagai kepastian mutlak.\n\n"
                f"KONTEKS DATABASE BACKEND:\n{database_context}"
            ),
        },
    ]
    safe_messages.extend(messages[-10:])

    return request_openai(
        safe_messages,
        max_completion_tokens=600,
        temperature=0.5,
    )
