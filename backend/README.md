# Backend Kalender Bali Wariga

Backend FastAPI untuk mengambil dan menghasilkan kalender dari database
PostgreSQL.

## Tabel Database

- kalender_dawuh
- tambahan

## Cara menjalankan

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Isi file `.env`:

```env
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=postgres
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
```

## API

Generate range:

```bash
POST http://127.0.0.1:8000/api/generate/kalender
```

Body:

```json
{
  "start_date": "2026-05-01",
  "end_date": "2026-05-30"
}
```

Ambil per tanggal:

```bash
GET http://127.0.0.1:8000/api/calendar/date/2026-05-01
```

Ambil per bulan:

```bash
GET http://127.0.0.1:8000/api/calendar/month/2026/5
```

Generate narasi karakter kelahiran dengan Groq AI:

```bash
POST http://127.0.0.1:8000/api/calendar/date/1900-01-01/character-ai
```

Chat Tanya Wariga AI:

```bash
POST http://127.0.0.1:8000/api/chat
```
