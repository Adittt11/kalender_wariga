# Arsitektur Web Kalender Bali Wariga

## 1. Gambaran Umum

Kalender Bali Wariga adalah aplikasi web untuk menampilkan informasi kalender Bali, data wewaran, dawuh, karakter kelahiran, cetak kalender, Tanya Wariga AI, dan Dewasa Ayu.

Aplikasi menggunakan arsitektur client-server:

- Frontend: React + Vite untuk tampilan dan interaksi pengguna.
- Backend: FastAPI untuk API kalender, dashboard, generate data, dan AI.
- Database: sumber data kalender dan makna Wariga melalui service backend.
- AI Service: Groq API untuk fitur ringkasan, karakter kelahiran, cetak kalender, dan chat Wariga.
- Data Dewasa Ayu: saat ini masih berupa JSON statis di frontend, direkomendasikan dipindahkan ke backend atau database.

## 2. Diagram Arsitektur

```text
Pengguna
   |
   v
Frontend React + Vite
   |
   |-- Halaman Dashboard
   |-- Halaman Dewasa Ayu
   |-- Halaman Cetak Kalender
   |-- Halaman Karakter Kelahiran
   |-- Halaman Tanya Wariga AI
   |
   v
Axios API Client
   |
   v
Backend FastAPI
   |
   |-- /api/calendar
   |-- /api/dashboard
   |-- /api/generate
   |-- /api/chat
   |
   v
Service Layer
   |
   |-- kalender_service.py
   |-- kalender_bali_service.py
   |-- groq_service.py
   |-- chat_context_service.py
   |-- database.py
   |
   +--> Database Kalender / Supabase
   |
   +--> Groq API
```

## 3. Struktur Folder Utama

```text
kalender_wariga/
├── frontend/
│   ├── public/
│   │   └── data/
│   │       └── dewasa_hasil3.json
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── router/
│   │   ├── services/
│   │   ├── data/
│   │   └── assets/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── main.py
│   │   └── config.py
│   ├── requirements.txt
│   └── run.py
│
└── docs/
    └── ARSITEKTUR_WEB.md
```

## 4. Arsitektur Frontend

Frontend bertugas menampilkan UI, menerima input pengguna, memanggil API backend, dan menampilkan hasil.

Teknologi:

- React untuk komponen UI.
- Vite untuk development server dan build.
- React Router untuk routing halaman.
- Axios untuk komunikasi ke backend.
- Tailwind CSS dan CSS global untuk styling.
- Lucide React untuk icon.

Halaman utama:

- `Dashboard.jsx`: menampilkan kalender ringkas, informasi kalender, waktu baik, dan ringkasan dewasa.
- `DewasaAyu.jsx`: menampilkan filter kategori/upacara/bulan/tahun dan hasil Dewasa Ayu.
- `CetakKalender.jsx`: fitur cetak kalender.
- `KarakterKelahiran.jsx`: informasi karakter berdasarkan tanggal.
- `TanyaWarigaAI.jsx`: chat AI untuk pertanyaan Wariga.
- `Penglukatan.jsx`: halaman fitur penglukatan.

API client berada di:

```text
frontend/src/services/api.js
frontend/src/services/calendarApi.js
frontend/src/services/chatApi.js
```

`api.js` menggunakan base URL:

```js
import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
```

## 5. Arsitektur Backend

Backend bertugas menyediakan API, mengambil data dari database, memproses data kalender, dan menghubungkan aplikasi ke layanan AI.

Teknologi:

- FastAPI untuk REST API.
- SQLAlchemy untuk koneksi/query database.
- Groq API untuk fitur AI.
- Python service layer untuk memisahkan logika bisnis dari route.

Entry point backend:

```text
backend/app/main.py
```

Route utama:

```text
/api/calendar
/api/dashboard
/api/generate
/api/chat
```

Service utama:

```text
backend/app/services/database.py
backend/app/services/kalender_service.py
backend/app/services/kalender_bali_service.py
backend/app/services/groq_service.py
backend/app/services/chat_context_service.py
backend/app/services/supabase_service.py
```

## 6. Alur Data Kalender

```text
User memilih tanggal/bulan
   |
Frontend memanggil calendarApi.js
   |
GET /api/calendar/date/{tanggal}
atau
GET /api/calendar/month/{tahun}/{bulan}
   |
calendar_routes.py
   |
kalender_service.py
   |
database.py
   |
Database
   |
Response JSON ke frontend
   |
UI menampilkan data kalender
```

Contoh endpoint:

```text
GET /api/calendar/date/1900-01-01
GET /api/calendar/month/1900/1
```

## 7. Alur Data Dashboard

```text
Dashboard.jsx
   |
getDashboardCalendarByDate(date)
   |
GET /api/dashboard/date/{tanggal}
   |
dashboard_routes.py
   |
kalender_service.py
   |
Database
```

Dashboard menggunakan data yang sama dengan kalender, tetapi ditampilkan sebagai ringkasan:

- Informasi wewaran
- Sasih
- Wuku
- Status purnama/tilem
- Baik buruk hari
- Dawuh atau waktu baik

## 8. Alur Fitur AI

```text
Frontend
   |
POST /api/calendar/date/{tanggal}/character-ai
atau
POST /api/calendar/date/{tanggal}/print-ai
atau
POST /api/chat
   |
FastAPI Routes
   |
groq_service.py
   |
Groq API
   |
Hasil AI dikembalikan ke frontend
```

Fitur AI menggunakan data kalender sebagai konteks agar jawaban tetap sesuai dengan informasi Wariga yang tersedia.

## 9. Arsitektur Dewasa Ayu Saat Ini

Saat ini Dewasa Ayu berjalan penuh di frontend:

```text
DewasaAyu.jsx
   |
fetch("/data/dewasa_hasil3.json")
   |
frontend/public/data/dewasa_hasil3.json
   |
Filter dilakukan di browser
   |
Hasil ditampilkan di UI
```

Data JSON berada di:

```text
frontend/public/data/dewasa_hasil3.json
```

Kelebihan:

- Cepat dibuat.
- Tidak perlu endpoint backend tambahan.
- Mudah dicoba saat development.

Kekurangan:

- File JSON sangat besar, sekitar 149 MB.
- Browser harus memuat semua data.
- Filter dilakukan di frontend sehingga kurang efisien.
- Kurang ideal untuk deployment production.

## 10. Arsitektur Dewasa Ayu yang Direkomendasikan

Untuk production, Dewasa Ayu sebaiknya dipindahkan ke backend dan database.

```text
DewasaAyu.jsx
   |
GET /api/dewasa-ayu?jenis_yadnya=...&upacara=...&bulan=...&tahun=...
   |
dewasa_ayu_routes.py
   |
dewasa_ayu_service.py
   |
Database Dewasa Ayu
   |
Response hasil yang sudah difilter
   |
Frontend menampilkan hasil
```

Endpoint yang disarankan:

```text
GET /api/dewasa-ayu/options
GET /api/dewasa-ayu/search?jenis_yadnya=Manusa%20Yadnya&upacara=Pawiwahan&bulan=1&tahun=1900
GET /api/dewasa-ayu/date/1900-01-01
```

Contoh response `/api/dewasa-ayu/search`:

```json
{
  "success": true,
  "filters": {
    "jenis_yadnya": "Manusa Yadnya",
    "upacara": "Pawiwahan",
    "bulan": 1,
    "tahun": 1900
  },
  "data": {
    "ayu": [],
    "dipakai": [],
    "ala": []
  }
}
```

## 11. Rancangan Database Dewasa Ayu

Supaya JSON besar dapat dipakai secara efisien, data dapat dipecah menjadi beberapa tabel.

Tabel `dewasa_days`:

```text
id
tanggal
wuku
ekawara
dwiwara
triwara
caturwara
pancawara
sadwara
saptawara
astawara
sangawara
dasawara
sasih
penanggal
pengelong
status_purnama
status_mala
ingkel
ekajalarsi
palalintangan
pararasan
pratitisamutpada
```

Tabel `dewasa_events`:

```text
id
day_id
upacara
jenis_yadnya
```

Tabel `dewasa_rules`:

```text
id
event_id
rule_id
nama_entitas
status
rule_text_id
rule_text_bali
aspek_cocok_json
```

Index yang disarankan:

```text
dewasa_days(tanggal)
dewasa_events(jenis_yadnya, upacara)
dewasa_rules(status)
```

## 12. Pembagian Tanggung Jawab Layer

Frontend:

- Menampilkan UI.
- Mengelola state pilihan pengguna.
- Memanggil API.
- Menampilkan loading, error, dan hasil.

Backend routes:

- Menerima request HTTP.
- Validasi parameter.
- Mengembalikan response JSON.

Backend services:

- Query database.
- Filter dan transform data.
- Menyusun format response.
- Menghubungi AI service bila diperlukan.

Database:

- Menyimpan data kalender, makna Wariga, dan Dewasa Ayu.
- Menyediakan data yang sudah bisa difilter berdasarkan tanggal, bulan, tahun, jenis yadnya, dan upacara.

AI service:

- Membuat ringkasan karakter kelahiran.
- Membuat ringkasan cetak kalender.
- Menjawab pertanyaan Tanya Wariga AI berdasarkan konteks.

## 13. Rekomendasi Pengembangan Berikutnya

Prioritas 1:

- Pindahkan data Dewasa Ayu dari JSON frontend ke backend/database.
- Buat route `/api/dewasa-ayu/options`.
- Buat route `/api/dewasa-ayu/search`.
- Frontend Dewasa Ayu memanggil API, bukan membaca JSON besar.

Prioritas 2:

- Tambahkan loading dan pagination untuk hasil Dewasa Ayu.
- Tambahkan filter per hari jika mode `Per Hari` dipilih.
- Tambahkan batas jumlah hasil agar UI tidak terlalu panjang.

Prioritas 3:

- Rapikan konfigurasi CORS agar tidak selalu `allow_origins=["*"]` pada production.
- Tambahkan validasi tanggal dan parameter API.
- Tambahkan test backend untuk route kalender dan Dewasa Ayu.

## 14. Kesimpulan

Arsitektur aplikasi Kalender Bali Wariga sudah memiliki pondasi client-server yang baik: frontend React untuk UI, backend FastAPI untuk API, database untuk data kalender, dan Groq API untuk fitur AI.

Bagian yang paling perlu ditingkatkan adalah Dewasa Ayu. Saat ini data Dewasa Ayu masih dimuat langsung dari JSON besar di frontend. Untuk aplikasi production, data tersebut sebaiknya dipindahkan ke backend/database agar performa lebih ringan, filter lebih cepat, dan struktur aplikasi lebih rapi.
