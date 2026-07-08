import json
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi

from app.config import GROQ_API_KEY, GROQ_MODEL


GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"

def request_groq(messages, max_completion_tokens=500, temperature=0.4, model=None):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY belum diisi di file .env")

    payload = {
        "model": model or GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_completion_tokens,
    }
    request = Request(
        GROQ_CHAT_COMPLETIONS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
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
        raise RuntimeError(f"Groq API gagal ({error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Tidak dapat terhubung ke Groq API: {error.reason}") from error

    try:
        return result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, AttributeError) as error:
        raise RuntimeError("Respons Groq API tidak memiliki teks hasil") from error


def generate_karakter_kelahiran_ai(calendar_data):
    teks = calendar_data["karakter_kelahiran"]
    makna_karakter = f"Detail makna karakter dari database: {teks}"
    prompt = (
        "Ringkas dan parafrase teks karakter kelahiran Bali berikut menjadi "
        "satu paragraf yang mengalir. Jangan menghilangkan makna pentingnya "
        "dan buatkan yang sangat masuk akal tanpa mengarang. Wajib gunakan "
        "makna aspek-aspek yang tersedia pada data. Kalimat awalnya "
        "mulai dengan: Seorang dengan kelahiran tersebut memiliki karakter berikut. "
        "Jangan tulis frasa 'menurut dataset'. "
        "TULIS LANGSUNG HASILNYA, dilarang menggunakan kata pengantar seperti "
        "'Berikut adalah', 'Hasilnya adalah', dan sebagainya. "
        f"{makna_karakter}"
    )

    return request_groq(
        [
            {
                "role": "system",
                "content": (
                    "Anda membantu menjelaskan tradisi Wariga Bali secara "
                    "informatif, hati-hati, dan tidak mengada-ada."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_completion_tokens=350,
    )


def generate_cetak_kalender_ai(calendar_data):
    prompt = (
        "Buat keluaran JSON valid tanpa markdown berdasarkan data Wariga Bali "
        "berikut. Jangan mengarang dan jangan menghilangkan makna penting. "
        "Gunakan format persis: "
        '{"karakter_kelahiran":"satu paragraf","hal_baik":["poin"],'
        '"hal_dihindari":["poin"]}. '
        "Untuk karakter_kelahiran, ringkas dan parafrase menjadi satu paragraf "
        "padat maksimal 110 kata yang mengalir. Kalimat awalnya mulai dengan: "
        "Seorang dengan kelahiran tersebut memiliki karakter berikut. "
        "Wajib gunakan makna aspek-aspek yang tersedia pada data. Jangan menggunakan kata "
        "pengantar atau frasa 'menurut dataset'. "
        "Untuk hal_baik dan hal_dihindari, ringkas informasi pakakalan menjadi "
        "maksimal 4 poin pendek pada masing-masing daftar. Jika tidak ada data, "
        "gunakan daftar kosong. "
        f"Detail makna karakter dari database: {calendar_data['karakter_kelahiran']} "
        f"Informasi pakakalan: {calendar_data['baik_buruk_hari']}"
    )
    response = request_groq(
        [
            {
                "role": "system",
                "content": (
                    "Anda merangkum data kalender Wariga Bali secara akurat. "
                    "Balas hanya dengan JSON valid."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_completion_tokens=700,
        temperature=0.2,
    )

    try:
        result = json.loads(response)
    except json.JSONDecodeError as error:
        raise RuntimeError("Respons ringkasan Groq bukan JSON valid") from error

    return {
        "karakter_kelahiran": str(result.get("karakter_kelahiran", "")).strip(),
        "hal_baik": [
            str(item).strip()
            for item in result.get("hal_baik", [])
            if str(item).strip()
        ][:4],
        "hal_dihindari": [
            str(item).strip()
            for item in result.get("hal_dihindari", [])
            if str(item).strip()
        ][:4],
    }


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
                "Boleh merapikan jawaban agar "
                "terdengar seperti percakapan, tetapi jangan mengubah fakta, "
                "tanggal, nama wuku, wewaran, atau status Dewasa dari database. "
                "Jika data belum cukup, minta pengguna melengkapi informasi yang "
                "kurang secara singkat. Jika pengguna menyebut pembayuhan atau "
                "pebayuhan, pahami keduanya sebagai istilah yang sama dan gunakan "
                "konteks Pembayuhan/Pebayuhan bila tersedia. Jika "
                "pengguna menanyakan pertemuan lanang istri, pahami lanang sebagai "
                "laki-laki dan istri sebagai perempuan/pasangan istri; gunakan "
                "tanggal lahir masing-masing dan konteks Pertemuan Lanang Istri "
                "bila tersedia. Jika "
                "pertanyaan membutuhkan data kalender spesifik yang tidak "
                "diberikan, jelaskan bahwa pengguna perlu menyebutkan tanggal "
                "dengan jelas, misalnya 22 Juni 2026 atau besok, atau membuka "
                "fitur kalender. Jangan mengarang fakta dan jangan menyatakan "
                "interpretasi tradisi sebagai kepastian mutlak. Jangan gunakan "
                "format Markdown, jangan gunakan tanda bintang, dan jangan "
                "menebalkan teks. Jika membuat daftar, gunakan baris biasa "
                "dengan angka atau tanda hubung tanpa simbol bintang. Untuk "
                "pertanyaan Dewasa, gunakan istilah Ayu untuk baik, Ala-Ayu "
                "untuk biasa saja atau campuran, dan Ala untuk buruk.\n\n"
                "dengan jelas, misalnya 22 Juni 2026 atau besok, atau membuka "
                "fitur kalender. Jangan mengarang fakta dan jangan menyatakan "
                "interpretasi tradisi sebagai kepastian mutlak. Jangan gunakan "
                "format Markdown, jangan gunakan tanda bintang, dan jangan "
                "menebalkan teks. Jika membuat daftar, gunakan baris biasa "
                "dengan angka atau tanda hubung tanpa simbol bintang. Untuk "
                "pertanyaan Dewasa, gunakan istilah Ayu untuk baik, Ala-Ayu "
                "untuk biasa saja atau campuran, dan Ala untuk buruk.\n\n"
                f"KONTEKS DATABASE BACKEND:\n{database_context}"
            ),
        },
    ]
    safe_messages.extend(messages[-10:])

    return request_groq(
        safe_messages,
        max_completion_tokens=4000,
        temperature=0.5,
        model=model,
    )
