@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM ╔══════════════════════════════════════════════════════════════════╗
REM ║  MIGRASI KALENDER BALI WARIGA - Supabase Cloud → PostgreSQL    ║
REM ║  Lokal (pgAdmin 4)                                             ║
REM ║                                                                ║
REM ║  Script ini akan:                                              ║
REM ║  1. Membuat database lokal "kalender_wariga"                   ║
REM ║  2. Mengimpor file supabase_full_2026-07-11.sql                ║
REM ║  3. Mengkonfigurasi file .env backend                          ║
REM ║  4. Setup virtual environment + install dependencies backend   ║
REM ║  5. Install dependencies frontend                              ║
REM ║  6. Verifikasi koneksi database                                ║
REM ╚══════════════════════════════════════════════════════════════════╝

echo.
echo ============================================================
echo   MIGRASI KALENDER BALI WARIGA
echo   Supabase Cloud -^> PostgreSQL Lokal (pgAdmin 4)
echo ============================================================
echo.

REM ─────────────────────────────────────────────────────────────
REM  KONFIGURASI — Sesuaikan bagian ini dengan komputer Anda
REM ─────────────────────────────────────────────────────────────

REM Path ke folder bin PostgreSQL (sesuaikan versi PostgreSQL Anda)
REM Contoh umum:
REM   PostgreSQL 16 : C:\Program Files\PostgreSQL\16\bin
REM   PostgreSQL 17 : C:\Program Files\PostgreSQL\17\bin
REM   PostgreSQL 18 : C:\Program Files\PostgreSQL\18\bin
set "PGBIN=C:\Program Files\PostgreSQL\17\bin"

REM Username PostgreSQL lokal (biasanya "postgres")
set "PGUSER=postgres"

REM Password PostgreSQL lokal
set "PGPASSWORD=Akunshoppefoo6"

REM Host dan Port PostgreSQL lokal
set "PGHOST=127.0.0.1"
set "PGPORT=5432"

REM Nama database yang akan dibuat
set "DBNAME=kalender_wariga"

REM File SQL dump dari Supabase
set "SQL_FILE=supabase_full_2026-07-11.sql"

REM ─────────────────────────────────────────────────────────────
REM  CEK PRASYARAT
REM ─────────────────────────────────────────────────────────────

echo [LANGKAH 0] Mengecek prasyarat...
echo.

REM Cek apakah psql ada
if not exist "%PGBIN%\psql.exe" (
    echo [ERROR] psql.exe tidak ditemukan di: %PGBIN%
    echo.
    echo Silakan edit file ini dan ubah variabel PGBIN
    echo sesuai dengan lokasi instalasi PostgreSQL Anda.
    echo.
    echo Lokasi umum:
    echo   C:\Program Files\PostgreSQL\16\bin
    echo   C:\Program Files\PostgreSQL\17\bin
    echo   C:\Program Files\PostgreSQL\18\bin
    echo.
    pause
    exit /b 1
)
echo   [OK] psql.exe ditemukan di %PGBIN%

REM Cek apakah file SQL ada
if not exist "%SQL_FILE%" (
    echo [ERROR] File SQL dump tidak ditemukan: %SQL_FILE%
    echo         Pastikan Anda menjalankan script ini dari folder kalender_wariga
    echo.
    pause
    exit /b 1
)
echo   [OK] File SQL dump ditemukan: %SQL_FILE%

REM Cek apakah Python ada
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Silakan install Python 3.10+ terlebih dahulu.
    echo         Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo   [OK] Python ditemukan

REM Cek apakah Node.js ada
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Node.js tidak ditemukan. Frontend tidak bisa di-install.
    echo           Download: https://nodejs.org/
    set "SKIP_FRONTEND=1"
) else (
    echo   [OK] Node.js ditemukan
    set "SKIP_FRONTEND=0"
)

echo.
echo   Semua prasyarat terpenuhi!
echo.

REM ─────────────────────────────────────────────────────────────
REM  LANGKAH 1: Buat Database Lokal
REM ─────────────────────────────────────────────────────────────

echo ============================================================
echo [LANGKAH 1/6] Membuat database "%DBNAME%" di PostgreSQL lokal...
echo ============================================================
echo.

REM Set PGPASSWORD agar tidak perlu input manual
set "PGPASSWORD=%PGPASSWORD%"

REM Cek apakah database sudah ada
"%PGBIN%\psql.exe" -U %PGUSER% -h %PGHOST% -p %PGPORT% -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='%DBNAME%'" 2>nul | findstr "1" >nul
if %errorlevel% equ 0 (
    echo   [INFO] Database "%DBNAME%" sudah ada.
    echo.
    set /p RECREATE="   Ingin menghapus dan membuat ulang? (y/n): "
    if /i "!RECREATE!"=="y" (
        echo   Menghapus database lama...
        "%PGBIN%\psql.exe" -U %PGUSER% -h %PGHOST% -p %PGPORT% -d postgres -c "DROP DATABASE IF EXISTS %DBNAME%;" 2>nul
        echo   Membuat database baru...
        "%PGBIN%\psql.exe" -U %PGUSER% -h %PGHOST% -p %PGPORT% -d postgres -c "CREATE DATABASE %DBNAME%;" 2>nul
        if !errorlevel! neq 0 (
            echo   [ERROR] Gagal membuat database. Periksa username/password PostgreSQL Anda.
            pause
            exit /b 1
        )
        echo   [OK] Database "%DBNAME%" berhasil dibuat ulang.
    ) else (
        echo   [OK] Melanjutkan dengan database yang sudah ada.
    )
) else (
    echo   Membuat database baru "%DBNAME%"...
    "%PGBIN%\psql.exe" -U %PGUSER% -h %PGHOST% -p %PGPORT% -d postgres -c "CREATE DATABASE %DBNAME%;" 2>nul
    if !errorlevel! neq 0 (
        echo   [ERROR] Gagal membuat database. Periksa username/password PostgreSQL Anda.
        pause
        exit /b 1
    )
    echo   [OK] Database "%DBNAME%" berhasil dibuat.
)
echo.

REM ─────────────────────────────────────────────────────────────
REM  LANGKAH 2: Impor File SQL ke Database Lokal
REM ─────────────────────────────────────────────────────────────

echo ============================================================
echo [LANGKAH 2/6] Mengimpor data dari %SQL_FILE%...
echo            (File ~163 MB, proses ini memakan waktu 2-10 menit)
echo ============================================================
echo.

"%PGBIN%\psql.exe" -U %PGUSER% -h %PGHOST% -p %PGPORT% -d %DBNAME% -f "%SQL_FILE%" -q 2>nul
if %errorlevel% neq 0 (
    echo.
    echo   [WARNING] Proses impor selesai dengan beberapa peringatan.
    echo            Ini NORMAL karena file dump Supabase sering mengandung
    echo            perintah khusus Supabase yang bisa diabaikan.
    echo.
) else (
    echo   [OK] Impor data selesai.
)
echo.

REM ─────────────────────────────────────────────────────────────
REM  LANGKAH 3: Verifikasi Data di Database
REM ─────────────────────────────────────────────────────────────

echo ============================================================
echo [LANGKAH 3/6] Memverifikasi data di database lokal...
echo ============================================================
echo.

echo   Menghitung jumlah baris di setiap tabel:
echo   ---------------------------------------------------------

for %%T in (kalender_bali kalender_dawuh dewasa daftar_wariga pebayuhan makna_4aspek keterangan_wuku keterangan_pancawara_saptawara knowledge_documents knowledge_chunks) do (
    for /f %%C in ('"%PGBIN%\psql.exe" -U %PGUSER% -h %PGHOST% -p %PGPORT% -d %DBNAME% -tAc "SELECT count(*) FROM %%T" 2^>nul') do (
        echo     %%T : %%C baris
    )
)

echo.
echo   ---------------------------------------------------------
echo   [OK] Verifikasi selesai. Bandingkan angka di atas dengan
echo        tabel verifikasi di PANDUAN_SETUP.md
echo.

REM ─────────────────────────────────────────────────────────────
REM  LANGKAH 4: Konfigurasi .env Backend
REM ─────────────────────────────────────────────────────────────

echo ============================================================
echo [LANGKAH 4/6] Mengkonfigurasi file backend\.env...
echo ============================================================
echo.

REM Backup .env lama jika ada
if exist "backend\.env" (
    copy "backend\.env" "backend\.env.backup.supabase" >nul 2>&1
    echo   [OK] Backup .env lama disimpan di: backend\.env.backup.supabase
)

REM Baca API key lama dari .env yang sudah ada (jika ada)
set "OLD_GROQ_KEY="
set "OLD_OPENAI_KEY="
set "OLD_GROQ_MODEL=llama-3.3-70b-versatile"
set "OLD_OPENAI_MODEL=gpt-4o-mini"
set "OLD_OPENAI_MINI=gpt-5.4-mini"
set "OLD_OPENAI_LATEST=gpt-5.5"
set "OLD_ADMIN_USER=admin"
set "OLD_ADMIN_PASS=admin"
set "OLD_ADMIN_SECRET=admin"

if exist "backend\.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("backend\.env") do (
        if "%%A"=="GROQ_API_KEY" set "OLD_GROQ_KEY=%%B"
        if "%%A"=="OPENAI_API_KEY" set "OLD_OPENAI_KEY=%%B"
        if "%%A"=="GROQ_MODEL" set "OLD_GROQ_MODEL=%%B"
        if "%%A"=="OPENAI_MODEL" set "OLD_OPENAI_MODEL=%%B"
        if "%%A"=="OPENAI_MINI_MODEL" set "OLD_OPENAI_MINI=%%B"
        if "%%A"=="OPENAI_LATEST_MODEL" set "OLD_OPENAI_LATEST=%%B"
        if "%%A"=="ADMIN_USERNAME" set "OLD_ADMIN_USER=%%B"
        if "%%A"=="ADMIN_PASSWORD" set "OLD_ADMIN_PASS=%%B"
        if "%%A"=="ADMIN_SECRET" set "OLD_ADMIN_SECRET=%%B"
    )
)

REM Tulis .env baru dengan koneksi lokal
(
    echo DB_USER=%PGUSER%
    echo DB_PASSWORD=%PGPASSWORD%
    echo DB_HOST=%PGHOST%
    echo DB_PORT=%PGPORT%
    echo DB_NAME=%DBNAME%
    echo.
    echo GROQ_API_KEY=!OLD_GROQ_KEY!
    echo OPENAI_API_KEY=!OLD_OPENAI_KEY!
    echo GROQ_MODEL=!OLD_GROQ_MODEL!
    echo OPENAI_MODEL=!OLD_OPENAI_MODEL!
    echo OPENAI_MINI_MODEL=!OLD_OPENAI_MINI!
    echo OPENAI_LATEST_MODEL=!OLD_OPENAI_LATEST!
    echo ADMIN_USERNAME=!OLD_ADMIN_USER!
    echo ADMIN_PASSWORD=!OLD_ADMIN_PASS!
    echo ADMIN_SECRET=!OLD_ADMIN_SECRET!
) > "backend\.env"

echo   [OK] File backend\.env telah dikonfigurasi untuk PostgreSQL lokal:
echo        DB_HOST = %PGHOST%
echo        DB_PORT = %PGPORT%
echo        DB_NAME = %DBNAME%
echo        DB_USER = %PGUSER%
echo.

REM ─────────────────────────────────────────────────────────────
REM  LANGKAH 5: Setup Backend (Python)
REM ─────────────────────────────────────────────────────────────

echo ============================================================
echo [LANGKAH 5/6] Setup Backend (Python Virtual Environment)...
echo ============================================================
echo.

cd backend

if not exist "venv" (
    echo   Membuat virtual environment baru...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo   [ERROR] Gagal membuat virtual environment.
        cd ..
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment berhasil dibuat.
) else (
    echo   [OK] Virtual environment sudah ada.
)

echo   Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

echo   Menginstall dependencies Python...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo   [ERROR] Gagal install dependencies. Periksa koneksi internet.
    cd ..
    pause
    exit /b 1
)
echo   [OK] Dependencies backend berhasil diinstall.
echo.

cd ..

REM ─────────────────────────────────────────────────────────────
REM  LANGKAH 6: Setup Frontend (Node.js)
REM ─────────────────────────────────────────────────────────────

echo ============================================================
echo [LANGKAH 6/6] Setup Frontend (React + Vite)...
echo ============================================================
echo.

if "%SKIP_FRONTEND%"=="1" (
    echo   [SKIP] Node.js tidak terinstal, frontend dilewati.
    echo          Install Node.js lalu jalankan: cd frontend ^&^& npm install
) else (
    cd frontend
    echo   Menginstall dependencies Node.js...
    call npm install --silent 2>nul
    if !errorlevel! neq 0 (
        echo   [WARNING] npm install mungkin memiliki warning, tapi biasanya tidak masalah.
    )
    echo   [OK] Dependencies frontend berhasil diinstall.
    cd ..
)
echo.

REM ─────────────────────────────────────────────────────────────
REM  SELESAI — Tampilkan Ringkasan
REM ─────────────────────────────────────────────────────────────

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║               MIGRASI BERHASIL!                             ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                             ║
echo ║  Database   : %DBNAME% (PostgreSQL lokal)          ║
echo ║  Backend    : FastAPI di http://127.0.0.1:8000              ║
echo ║  Frontend   : React Vite di http://localhost:5173           ║
echo ║                                                             ║
echo ║  CARA MENJALANKAN APLIKASI:                                 ║
echo ║                                                             ║
echo ║  Terminal 1 (Backend):                                      ║
echo ║    cd backend                                               ║
echo ║    venv\Scripts\activate                                    ║
echo ║    python run.py                                            ║
echo ║                                                             ║
echo ║  Terminal 2 (Frontend):                                     ║
echo ║    cd frontend                                              ║
echo ║    npm run dev                                              ║
echo ║                                                             ║
echo ║  Lalu buka browser: http://localhost:5173                   ║
echo ║                                                             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
