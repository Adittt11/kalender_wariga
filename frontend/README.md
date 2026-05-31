# Kalender Wariga Frontend

Frontend React untuk dashboard Kalender Bali Wariga.

## Cara menjalankan

```bash
cd kalender-wariga-frontend
npm install
npm run dev
```

Lalu buka alamat yang muncul di terminal, biasanya:

```bash
http://localhost:5173
```

## Struktur

```bash
src/
├── components/
├── pages/
├── router/
├── services/
└── data/
```

## Catatan

Frontend ini masih menggunakan mock data di `src/data/mockCalendar.js`.
Nanti ketika backend sudah siap, data bisa diambil dari endpoint FastAPI melalui `src/services/api.js`.
