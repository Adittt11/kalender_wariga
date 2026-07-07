from sqlalchemy import text
from app.services.database import engine

with engine.connect() as conn:
    row = conn.execute(text('SELECT MIN("Tahun"), MAX("Tahun") FROM kalender_bali')).fetchone()
    print("Year range:", row)
    samples = conn.execute(text('SELECT "Tahun", "Bulan", "Tanggal", "Saptawara", "Pancawara" FROM kalender_bali LIMIT 3')).fetchall()
    for r in samples:
        print(r)
