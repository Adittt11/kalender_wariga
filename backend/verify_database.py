"""
============================================================
  VERIFIKASI DATABASE LOKAL — Kalender Bali Wariga
============================================================
Script ini mengecek apakah database PostgreSQL lokal sudah
terkonfigurasi dengan benar dan semua tabel berisi data.

Cara pakai:
  cd backend
  venv\Scripts\activate
  python verify_database.py
============================================================
"""

import sys
import os

# Tambahkan parent directory supaya bisa import app.config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

# Tabel yang WAJIB ada beserta jumlah minimum baris yang diharapkan
EXPECTED_TABLES = {
    "kalender_bali":                    {"min_rows": 29000, "description": "Data kalender harian utama"},
    "kalender_dawuh":                   {"min_rows": 29000, "description": "Data kalender + dawuh + pakakalan"},
    "dewasa":                           {"min_rows": 29000, "description": "Aturan dewasa ayu (hari baik/buruk)"},
    "daftar_wariga":                    {"min_rows": 50,    "description": "Daftar wariga adat"},
    "pebayuhan":                        {"min_rows": 30,    "description": "Data ruwatan/penglukatan"},
    "makna_4aspek":                     {"min_rows": 30,    "description": "Arti lintang, pararasan, pratiti, dll."},
    "keterangan_wuku":                  {"min_rows": 25,    "description": "Penjelasan wuku harian"},
    "keterangan_pancawara_saptawara":   {"min_rows": 5,     "description": "Penjelasan pancawara & saptawara"},
    "knowledge_documents":              {"min_rows": 0,     "description": "Dokumen referensi RAG Chatbot"},
    "knowledge_chunks":                 {"min_rows": 0,     "description": "Potongan teks bervektor untuk RAG"},
}


def main():
    print()
    print("=" * 60)
    print("  VERIFIKASI DATABASE LOKAL — Kalender Bali Wariga")
    print("=" * 60)
    print()

    # ─── 1. Tampilkan konfigurasi koneksi ─────────────────────
    print(f"  Koneksi yang digunakan (dari backend/.env):")
    print(f"    Host     : {DB_HOST}")
    print(f"    Port     : {DB_PORT}")
    print(f"    Database : {DB_NAME}")
    print(f"    User     : {DB_USER}")
    print(f"    Password : {'*' * min(len(DB_PASSWORD or ''), 8)}...")
    print()

    # ─── 2. Coba koneksi ─────────────────────────────────────
    print("  [1/3] Mengecek koneksi ke database...", end=" ")
    try:
        from sqlalchemy import create_engine, text
        url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
        print("OK ✓")
        print(f"        PostgreSQL version: {version.split(',')[0]}")
    except Exception as e:
        print("GAGAL ✗")
        print()
        print(f"  [ERROR] Tidak bisa terhubung ke database!")
        print(f"          {e}")
        print()
        print("  Solusi:")
        print("  1. Pastikan PostgreSQL service sedang berjalan")
        print("  2. Pastikan file backend/.env sudah benar")
        print("  3. Pastikan database sudah dibuat (jalankan migrate_to_local.bat)")
        print()
        sys.exit(1)
    print()

    # ─── 3. Cek semua tabel ──────────────────────────────────
    print("  [2/3] Mengecek tabel dan data...")
    print(f"  {'Tabel':<40} {'Baris':>10}   Status")
    print(f"  {'-'*40} {'-'*10}   {'-'*10}")

    all_ok = True
    with engine.connect() as conn:
        for table_name, info in EXPECTED_TABLES.items():
            try:
                result = conn.execute(text(f"SELECT count(*) FROM {table_name}"))
                count = result.scalar()
                if count >= info["min_rows"]:
                    status = "OK ✓"
                elif count > 0:
                    status = "PARTIAL ⚠"
                else:
                    status = "KOSONG ✗"
                    all_ok = False
                print(f"  {table_name:<40} {count:>10}   {status}")
            except Exception:
                print(f"  {table_name:<40} {'—':>10}   TIDAK ADA ✗")
                all_ok = False

    print()

    # ─── 4. Tes query yang dipakai aplikasi ──────────────────
    print("  [3/3] Mengecek query utama aplikasi...")
    queries_ok = True

    test_queries = [
        {
            "name": "Kalender per tanggal (hari ini)",
            "sql": """
                SELECT * FROM kalender_dawuh
                WHERE "Tahun" = EXTRACT(YEAR FROM CURRENT_DATE)::int
                  AND "Bulan" = EXTRACT(MONTH FROM CURRENT_DATE)::int
                  AND "Tanggal" = EXTRACT(DAY FROM CURRENT_DATE)::int
            """
        },
        {
            "name": "Kalender Bali per tanggal",
            "sql": """
                SELECT * FROM kalender_bali
                WHERE "Tahun" = 2025 AND "Bulan" = 1 AND "Tanggal" = 1
                LIMIT 1
            """
        },
        {
            "name": "Makna 4 aspek",
            "sql": "SELECT * FROM makna_4aspek LIMIT 1"
        },
        {
            "name": "Keterangan wuku",
            "sql": "SELECT * FROM keterangan_wuku LIMIT 1"
        },
        {
            "name": "Dewasa ayu",
            "sql": "SELECT * FROM dewasa LIMIT 1"
        },
        {
            "name": "Daftar wariga",
            "sql": "SELECT * FROM daftar_wariga LIMIT 1"
        },
        {
            "name": "Pebayuhan",
            "sql": "SELECT * FROM pebayuhan LIMIT 1"
        },
    ]

    with engine.connect() as conn:
        for tq in test_queries:
            try:
                result = conn.execute(text(tq["sql"]))
                rows = result.fetchall()
                if rows:
                    print(f"    {tq['name']:<45} OK ✓")
                else:
                    print(f"    {tq['name']:<45} DATA KOSONG ⚠")
                    queries_ok = False
            except Exception as e:
                print(f"    {tq['name']:<45} GAGAL ✗")
                print(f"      Error: {e}")
                queries_ok = False

    print()

    # ─── 5. Ringkasan ────────────────────────────────────────
    print("=" * 60)
    if all_ok and queries_ok:
        print("  ✅ SEMUA VERIFIKASI BERHASIL!")
        print()
        print("  Database lokal siap digunakan.")
        print("  Jalankan aplikasi:")
        print("    Backend  : python run.py")
        print("    Frontend : cd ../frontend && npm run dev")
        print("    Buka     : http://localhost:5173")
    elif all_ok:
        print("  ⚠️  Database terkoneksi dan tabel ada,")
        print("     tapi beberapa query mengembalikan hasil kosong.")
        print("     Ini mungkin normal jika data belum lengkap.")
    else:
        print("  ❌ ADA MASALAH PADA DATABASE!")
        print()
        print("  Beberapa tabel tidak ditemukan atau kosong.")
        print("  Pastikan file SQL sudah diimpor dengan benar:")
        print("    jalankan migrate_to_local.bat atau impor manual via pgAdmin")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
