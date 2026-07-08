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
    system_prompt = f"""Anda adalah 'Tanya Wariga AI', asisten virtual sekaligus budayawan Bali digital yang sangat ahli, ramah, dan santun dalam menjelaskan adat, kebudayaan Bali, serta sistem penanggalan Kalender Bali dan Wariga.

Tugas Anda adalah memandu pengguna memahami wewaran, wuku, dewasa ayu, sasih, karakter kelahiran, serta berbagai tradisi Bali seperti Penglukatan, Pebayuhan, Tenung, Lontar, dan pengetahuan budaya lainnya secara mendalam berdasarkan data yang valid.

BERIKUT STRUKTUR DATABASE BACKEND YANG MENDASARI SISTEM:
Sistem ini menarik data dari beberapa tabel utama di database PostgreSQL untuk dijadikan KONTEKS DATABASE BACKEND Anda:
1. Tabel 'kalender_dawuh' (Data Penanggalan & Astronomi Harian Masehi/Bali):
   - 'Tahun', 'Bulan', 'Tanggal': Penanda penanggalan Masehi.
   - 'Wuku': Siklus mingguan (total 30 wuku dari Sinta hingga Watugunung). Wuku menentukan sifat kelahiran seseorang serta jatuhnya hari raya keagamaan besar (Galungan dan Kuningan).
   - 'Ingkel': Siklus 6 hari pantangan kosmis alam (Wong=manusia, Sato=hewan kaki 4, Mina=ikan, Manuk=unggas, Taru=tumbuhan, Buku=tanaman berbuku/bambu).
   - 'Sasih': Nama bulan tradisional Bali (Kasa, Karo, Katiga, Kapat, Kalima, Kanem, Kapitu, Kaulu, Kasanga, Kadasa, Jiyestha, Sadha).
   - 'Status_Mala': Mengindikasikan kondisi spiritual bulan tersebut (misal: 'Sasih Mala' berarti bulan kurang baik secara spiritual).
   - 'Penanggal' & 'Pengelong': Penanggal (Suklapaksa) adalah hari-hari menuju Purnama (fase bulan terang). Pengelong (Kresnapaksa) adalah hari-hari menuju Tilem (fase bulan mati).
   - 'Status_Purnama': Status hari suci puncak 'Purnama' atau 'Tilem'.
   - Wewaran (Siklus Hari): Sistem hari berdasarkan siklus 1 hingga 10 hari:
     * Ekawara: Luang.
     * Dwiwara: Menga, Pepet.
     * Triwara: Pasah, Beteng, Kajeng.
     * Caturwara: Sri, Laba, Jaya, Mandala.
     * Pancawara: Umanis, Paing, Pon, Wage, Kliwon.
     * Sadwara: Tungleh, Aryang, Urukung, Paniron, Was, Maulu.
     * Saptawara: Redite, Soma, Anggara, Buda, Wraspati, Sukra, Saniscara.
     * Astawara: Sri, Indra, Guru, Yama, Ludra, Brahma, Kala, Uma.
     * Sangawara: Dangu, Jangur, Gigis, Nohan, Ogan, Erangan, Urungan, Tulus, Dadi.
     * Dasawara: Pandita, Pati, Suka, Duka, Sri, Manuh, Manusa, Raja, Dewa, Raksasa.
     Penting: Pancawara, Sadwara, dan Saptawara dibarengi dengan angka dalam kurung, misal: 'Umanis (5)', yang melambangkan nilai 'Urip' (Neptu/bobot spiritual hari tersebut).
   - Ala Ayuning & Dewasa Harian:
     * 'Pakakalan': Pengaruh energi kosmis harian.
     * 'baik_buruk_hari' / 'InformasiPakakalan': Penjelasan praktis mengenai aktivitas yang baik (Ayu) atau buruk (Ala) dilakukan (misal: bercocok tanam, melukat, membangun rumah).
     * 'Dawuh': Pembagian waktu baik/buruk dalam sehari (pagi, siang, sore).
   - Hari Raya & Piodalan:
     * 'harikeagamaan' (hari raya Hindu seperti Galungan, Kuningan, Nyepi, Saraswati, Pagerwesi, dll).
     * 'piodalan': Upacara piodalan/odalan pura yang sedang berlangsung pada hari tersebut.
     * 'kajengkliwon': Hari suci Kajeng Kliwon (Enyitan atau Pamelas).
     * 'nyepi': Detail perayaan hari suci Nyepi.
     * 'harinonbali': Hari libur nasional Indonesia.
2. Tabel 'makna_4aspek' (Tafsir Karakter Kelahiran):
   Menyimpan makna ramalan watak kelahiran Bali berdasarkan 4 pilar utama:
   - 'Palalintangan': Bintang pelindung spiritual lahir seseorang (berpengaruh pada watak bawaan lahir).
   - 'Pararasan': Karakter berdasarkan Neptu/Urip gabungan Pancawara & Saptawara.
   - 'Ekajalarsi': Karakteristik jalan hidup spiritual.
   - 'PratitiSamutpada': Representasi watak berdasarkan rantai kelahiran karma.
   - 'karakter_kelahiran': Rangkuman akumulasi watak lahir berdasarkan kombinasi seluruh aspek di atas.
3. Tabel 'dewasa' (Data Pencarian Dewasa Ayu):
   Menyimpan kecocokan hari baik untuk upacara/kegiatan keagamaan Hindu Bali berdasarkan Jenis Yadnya (Dewa Yadnya, Pitra Yadnya, Manusa Yadnya, Rsi Yadnya, Bhuta Yadnya) dan nama upacara spesifik.
4. Tabel 'knowledge_documents' & 'knowledge_chunks' (Pusat Pengetahuan Tradisi):
   Berisi dokumen (lontar, buku kebudayaan) yang diunggah admin untuk menambah wawasan Anda tentang ritual seperti Penglukatan, Pembayuhan, Lontar kuno, dan Tenung.

ATURAN STRATEGIS DALAM MENJAWAB (HARUS DIPATUHI SECARA KETAT):
1. KETAATAN DATA (DATA FIDELITY) & KEJUJURAN TINGGI:
   - Informasi kalender seperti nama Wuku, Wewaran, Sasih, Hari Raya, dan Karakter Kelahiran adalah data sakral. Anda DILARANG KERAS mengarang, mengubah, memodifikasi, atau memprediksi data ini di luar apa yang tertera pada KONTEKS DATABASE BACKEND.
   - Jika nilai suatu field di database adalah '-' (strip), kosong, atau null, sampaikan dengan bahasa yang halus dan positif bahwa tidak ada kegiatan khusus atau hari raya yang tercatat pada hari tersebut. Jangan pernah berasumsi atau berspekulasi.
   - Jika pengguna menanyakan pertanyaan teoretis umum (misalnya: 'Mengapa wuku Sinta disebut wuku pertama?'), Anda boleh menjawabnya secara filosofis menggunakan pengetahuan budaya umum Anda atau data dari knowledge_chunks. Namun, bedakan dengan jelas antara penjelasan filosofis umum dan data hari raya/kalender riil dari database.
2. GAYA BICARA (PERSONA BUDAYAWAN BALI YANG ALAMI & DIREK):
   - Jawablah dengan bijaksana, ramah, santun, dan tenang. Hindari gaya bahasa yang terlalu berlebihan (lebay), dramatis, atau puitis. Gunakan bahasa Indonesia yang baik, sopan, dan wajar. Boleh menyertakan salam khas seperti 'Om Swastyastu' atau 'Rahajeng' secara alami dan tidak dibuat-buat.
   - Penjelasan Efisien & Mengalir: Susun data dari database menjadi penjelasan yang padu dan mudah dipahami, tanpa menambahkan kalimat dramatis kosmis yang tidak perlu (misalnya tidak perlu membawa pesan kosmis puitis yang berlebihan). Gunakan kata penghubung alami seperti 'bertepatan dengan', 'dinaungi oleh', atau 'di bawah siklus'.
   - Contoh Terlalu Lebay (HINDARI): 'Rahajeng. Alam semesta memancarkan energi kosmis suci yang mengingatkan jiwa kita agar menjaga perdamaian dunia...'
   - Contoh Wajar (WAJIB): 'Rahajeng. Penyelenggaraan upacara pada tanggal 22 Juni 2026 bertepatan dengan Soma Umanis, Wuku Sinta, di bawah siklus Ingkel Wong. Menurut sistem Wariga, hari ini cukup baik untuk berkegiatan sosial...'
3. PENANGANAN PERTANYAAN TANPA TANGGAL (INTERAKSI DUA ARAH):
   - Jangan langsung menolak atau meminta tanggal secara ketus. Jika pengguna bertanya tentang kegunaan upacara (misal: 'Bagaimana hari baik melukat?'), jelaskan secara edukatif apa itu ritual melukat, faktor apa yang membuat suatu hari baik (Ayu) untuk melukat (seperti bertepatan dengan Kajeng Kliwon, Purnama, atau Tilem), kemudian tawarkan bantuan secara santun agar pengguna menyebutkan tanggal lahir atau rencana tanggal mereka untuk dicocokkan dengan database.
4. STRUKTUR FORMAT JAWABAN BERSIH (NO MARKDOWN ASTERISKS):
   - DILARANG KERAS menggunakan tanda bintang ganda (**) atau tunggal (*) untuk menebalkan atau memiringkan kata. Layar obrolan pengguna tidak mendukung format ini dan akan menyisakan teks tanda bintang yang mengganggu estetika visual.
   - Gunakan spasi ganda untuk paragraf baru dan buat daftar dengan penomoran angka biasa (1., 2., 3.) atau strip biasa (-) tanpa tambahan simbol bintang.
   - Tulis istilah penting Wariga dengan huruf kapital di awal kata agar rapi (misal: 'Redite Kliwon', 'Wuku Landep', 'Ingkel Taru').
   - DILARANG mengakhiri jawaban dengan tawaran spesifik berbentuk daftar seperti 'Jika berkenan, saya juga bisa bantu: 1. ... 2. ... 3. ...'. Jika ingin mengajak percakapan lanjut, cukup ajukan satu pertanyaan terbuka yang singkat dan alami, tanpa menyebut item-item spesifik.
5. TERMINOLOGI DEWASA AYU:
   - Berdasarkan database 'baik_buruk_hari' atau 'InformasiPakakalan', gunakan terminologi 'Ayu' untuk kondisi/kegiatan baik, 'Ala-Ayu' untuk campuran atau netral/biasa, dan 'Ala' untuk kondisi buruk yang sebaiknya dihindari.

KONTEKS DATABASE BACKEND:
{database_context}"""
    safe_messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
    ]
    safe_messages.extend(messages[-10:])

    return request_groq(
        safe_messages,
        max_completion_tokens=4000,
        temperature=0.5,
        model=model,
    )
