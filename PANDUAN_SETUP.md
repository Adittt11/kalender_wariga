# Panduan Setup & Migrasi Kalender Bali Wariga & Chatbot AI

Dokumen ini berisi panduan lengkap untuk mempersiapkan, melakukan restorasi database, dan menjalankan aplikasi **Kalender Bali Wariga & Chatbot AI** (Backend FastAPI & Frontend React Vite).

---

## 1. Hasil Verifikasi Database (`supabase_full_2026-07-11.sql`)

Kami telah melakukan verifikasi kesamaan data antara database **Supabase Cloud (Live)** yang saat ini terhubung dengan file backup **`supabase_full_2026-07-11.sql`**.

Semua data telah dicocokkan berdasarkan jumlah baris (row count) pada masing-masing tabel utama. Hasilnya adalah **100% Identik/Sama**:

| Nama Tabel | Jumlah Baris (Live Supabase) | Jumlah Baris (File `.sql` Backup) | Status Sinkronisasi | Keterangan |
| :--- | :---: | :---: | :---: | :--- |
| **`kalender_bali`** | 29.219 | 29.219 | ✅ Cocok | Data kalender harian, wewaran, dll. |
| **`dewasa`** | 29.219 | 29.219 | ✅ Cocok | Aturan dewasa ayu (hari baik/buruk) |
| **`daftar_wariga`** | 55 | 55 | ✅ Cocok | Daftar wariga adat |
| **`pebayuhan`** | 35 | 35 | ✅ Cocok | Data ruwatan/penglukatan |
| **`makna_4aspek`** | 35 | 35 | ✅ Cocok | Arti lintang, pararasan, pratiti, dll. |
| **`keterangan_wuku`** | 30 | 30 | ✅ Cocok | Penjelasan wuku harian |
| **`keterangan_pancawara_saptawara`** | 7 | 7 | ✅ Cocok | Penjelasan pancawara & saptawara |
| **`knowledge_documents`** | 2 | 2 | ✅ Cocok | Dokumen referensi RAG Chatbot |
| **`knowledge_chunks`** | 5 | 5 | ✅ Cocok | Potongan teks bervektor untuk RAG |

> [!NOTE]
> File backup `supabase_full_2026-07-11.sql` sudah sepenuhnya aman dan lengkap untuk digunakan sebagai basis pengumpulan tugas ataupun restorasi ulang.

---

## 2. Cara Kerja Koneksi Database (Supabase vs PostgreSQL Lokal)

**Supabase** secara mendasar adalah layanan cloud yang menyediakan database **PostgreSQL**. Oleh karena itu:
1. **Tidak perlu migrasi tipe database** jika ingin berpindah dari Supabase ke PostgreSQL lokal karena keduanya menggunakan mesin database yang sama (PostgreSQL).
2. **Fleksibilitas Koneksi**: Aplikasi ini menghubungkan database melalui modul SQLAlchemy di Backend menggunakan variabel lingkungan (environment variables) di file `.env`. 
3. **Mengganti Database Sangat Mudah**: Jika ingin mengubah koneksi dari Supabase Cloud ke database lokal/baru, Anda **TIDAK PERLU mengubah kode program sama sekali**, cukup perbarui konfigurasi pada file `backend/.env`.

---

## 3. Opsi Setup Database

Anda dapat memilih untuk tetap menggunakan cloud (Supabase) atau melakukan migrasi ke PostgreSQL Lokal.

### OPSI A: Menggunakan Supabase Cloud (Sudah Aktif - Direkomendasikan untuk Kemudahan)
Saat ini backend sudah terkonfigurasi otomatis dengan database Supabase Cloud. Jika Anda atau Dosen ingin langsung menjalankannya tanpa menginstal PostgreSQL secara lokal, langsung lewati bagian ini dan lanjut ke **Langkah 4 (Setup Backend)**.

---

### OPSI B: Melakukan Migrasi/Restorasi ke PostgreSQL Lokal
Jika dosen meminta database harus berjalan secara lokal di komputer, ikuti langkah berikut:

#### Langkah B.1: Buat Database Baru di PostgreSQL Lokal
1. Buka **pgAdmin** atau terminal PostgreSQL Anda.
2. Buat database baru dengan nama bebas (contoh: `kalender_wariga`).

#### Langkah B.2: Impor/Restore File `supabase_full_2026-07-11.sql`
* **Menggunakan pgAdmin**:
  1. Klik kanan pada database baru (`kalender_wariga`) $\rightarrow$ pilih **Query Tool**.
  2. Buka file `supabase_full_2026-07-11.sql` di editor atau salin seluruh isinya.
  3. Tempelkan ke Query Tool pgAdmin, lalu tekan tombol **Execute / Run** (ikon petir atau F5).
  4. *Catatan*: Karena ukuran file yang besar (~163 MB), disarankan menggunakan command line agar lebih cepat dan stabil.

* **Menggunakan Command Line (Terminal/CMD)**:
  Buka CMD/PowerShell di direktori tempat file `.sql` berada, kemudian jalankan perintah berikut:
  ```bash
  psql -U <username_postgres> -d kalender_wariga -f supabase_full_2026-07-11.sql
  ```
  *(Masukkan password database Anda ketika diminta)*.

  > [!TIP]
  > Jika muncul error `'psql' is not recognized as an internal or external command`, Anda bisa menggunakan path instalasi lengkap `psql` sesuai versi PostgreSQL yang terinstal (contoh untuk PostgreSQL 18):
  > ```cmd
  > "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d kalender_wariga -f supabase_full_2026-07-11.sql
  > ```

#### Langkah B.3: Perbarui `.env` Backend
Buka file `backend/.env` dan ubah nilai variabel database menjadi seperti berikut:
```env
DB_USER=postgres            # Username PostgreSQL lokal Anda
DB_PASSWORD=password_anda    # Password PostgreSQL lokal Anda
DB_HOST=127.0.0.1           # Host lokal (localhost)
DB_PORT=5432                # Port default PostgreSQL lokal
DB_NAME=kalender_wariga     # Nama database yang baru dibuat
```

> [!TIP]
> **Cara Cepat Membuka File `.env` di Windows**: Karena Windows sering menyembunyikan file berformat `.env` (file tersembunyi), Anda bisa membukanya secara instan dengan masuk ke folder `backend` di CMD lalu ketik perintah:
> ```cmd
> notepad .env
> ```


---

## 4. Cara Menjalankan Backend (FastAPI)

### Langkah 4.1: Buka Terminal & Masuk ke Folder Backend
```bash
cd backend
```

### Langkah 4.2: Buat & Aktifkan Virtual Environment (Venv)
* **Windows**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **macOS/Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Langkah 4.3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Langkah 4.4: Konfigurasi API Key di `.env`
Buka file `backend/.env`. Pastikan API Key di bawah ini aktif (atau ganti dengan milik Anda sendiri jika diperlukan):
* `GROQ_API_KEY`: Digunakan untuk model LLM berlatensi cepat (Llama 3).
* `OPENAI_API_KEY`: Digunakan untuk modul interpretasi tanggal natural serta pembentukan Vector Embedding untuk RAG Chatbot.

### Langkah 4.5: Jalankan Server FastAPI
```bash
python run.py
```
Server backend akan berjalan di alamat: **`http://127.0.0.1:8000`**

---

## 5. Cara Menjalankan Frontend (React + Vite)

### Langkah 5.1: Buka Terminal Baru & Masuk ke Folder Frontend
```bash
cd frontend
```

### Langkah 5.2: Install Dependencies Node.js
```bash
npm install
```

### Langkah 5.3: Jalankan Developer Server
```bash
npm run dev
```
Aplikasi frontend akan berjalan di alamat default: **`http://localhost:5173`** (silakan buka di web browser Anda).

---

## 6. Tips Pengumpulan Tugas (Format Folder per Mahasiswa)

Untuk memenuhi instruksi dosen yang meminta pengumpulan folder masing-masing dengan rapi dan efisien:

1. **Struktur Folder Pengumpulan**:
   ```text
   NIM_Nama_WarigaApp/
   ├── backend/
   │   ├── app/
   │   ├── .env.example
   │   ├── .env                  # (Sertakan jika dosen perlu langsung tes koneksi cloud)
   │   ├── requirements.txt
   │   └── run.py
   ├── frontend/
   │   ├── src/
   │   ├── public/
   │   ├── package.json
   │   ├── vite.config.js
   │   └── ...
   ├── docs/                     # Folder arsitektur sistem dan database
   ├── supabase_full_2026-07-11.sql
   └── PANDUAN_SETUP.md          # Dokumen panduan ini
   ```

2. **Bersihkan Folder Sebelum Dikompres (ZIP/RAR)**:
   * **Hapus** folder `backend/venv/` (karena ukurannya besar dan berisi virtual environment lokal komputer Anda). Dosen akan membuat venv mereka sendiri.
   * **Hapus** folder `frontend/node_modules/` (karena ukurannya sangat besar). Dosen tinggal menjalankan perintah `npm install` saat setup pertama kali.
   * Langkah pembersihan ini akan memangkas ukuran file pengumpulan dari ratusan megabyte menjadi kurang dari 5MB (di luar file `.sql` database).
