import { CalendarDays, CheckSquare } from "lucide-react";
import DownloadCard from "../components/DownloadCard";

export default function CetakKalender() {
  return (
    <div className="grid grid-cols-1 gap-8 xl:grid-cols-2">
      <section className="card p-7">
        <div className="mb-5 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold">Preview Hasil</h2>
            <p className="mt-1 text-sm text-gray-500">
              Tanggal 29 Mei 2026 - 30 Mei 2026
            </p>
          </div>
          <div className="flex gap-2">
            <button className="rounded-xl border border-baliBorder px-4 py-2">‹</button>
            <button className="rounded-xl border border-baliBorder px-4 py-2">›</button>
          </div>
        </div>

        <div className="min-h-[650px] rounded-2xl border border-baliBorder bg-white p-8 text-center shadow-soft">
          <p className="font-serifBali text-sm uppercase tracking-[0.35em] text-gray-500">
            Kalender Bali Wariga
          </p>
          <h1 className="mt-5 font-serifBali text-4xl font-bold">1 MEI 2026</h1>

          <div className="mt-8 grid grid-cols-4 gap-4 border-y border-baliBorder py-5 text-sm">
            <b>INGKEL<br />WONG</b>
            <b>WUKU<br />LANGKIR</b>
            <b>SASIH<br />KENAM</b>
            <b>PANGELONG<br />15-TILEM</b>
          </div>

          <h2 className="mt-12 font-serifBali text-xl font-bold">KARAKTER KELAHIRAN</h2>
          <p className="mx-auto mt-4 max-w-[520px] text-justify text-sm leading-7 text-gray-600">
            Kepribadian ini memiliki kualitas baik yang menonjol, seperti kemampuan
            membangun hubungan baik dengan orang lain dan kepekaan terhadap
            lingkungan sekitar.
          </p>

          <h2 className="mt-12 font-serifBali text-xl font-bold">PAKAKALAN</h2>
          <div className="mt-4 flex flex-wrap justify-center gap-3">
            {["Amerta Buwana", "Babi Turun", "Kala Ketemu"].map((item) => (
              <span key={item} className="rounded-lg bg-gray-600 px-3 py-2 text-xs text-white">
                {item}
              </span>
            ))}
          </div>
        </div>
      </section>

      <div className="space-y-6">
        <section className="card p-8">
          <h2 className="text-2xl font-bold">Cetak Kalender</h2>
          <p className="mt-4 max-w-[760px] text-sm leading-7 text-gray-500">
            Pilih tanggal dan template kalender yang diinginkan. Sistem akan
            menghasilkan pratinjau kalender Bali dan Wariga yang dapat dicetak
            atau diunduh.
          </p>

          <div className="mt-8 grid grid-cols-1 gap-6 border-t border-baliBorder pt-8 md:grid-cols-2">
            <div>
              <label className="mb-3 flex items-center gap-2 font-semibold">
                <CalendarDays size={22} />
                Pilih Tanggal Awal
              </label>
              <input className="input" type="text" value="29 Mei 2026" readOnly />
            </div>

            <div>
              <label className="mb-3 flex items-center gap-2 font-semibold">
                <CalendarDays size={22} />
                Pilih Tanggal Akhir
              </label>
              <input className="input" type="text" value="30 Mei 2026" readOnly />
            </div>
          </div>

          <div className="mt-8 flex justify-end">
            <button className="btn-primary flex items-center gap-2">
              <CheckSquare size={18} />
              Konfirmasi Tanggal
            </button>
          </div>
        </section>

        <section className="card p-8">
          <h2 className="text-2xl font-bold">Unduh Hasil</h2>
          <div className="mt-8 space-y-6">
            <DownloadCard
              type="PDF"
              description="Unduh sebagai dokumen siap cetak yang rapi dan profesional."
            />
            <DownloadCard
              type="PNG"
              description="Unduh sebagai gambar berkualitas tinggi dan praktis."
            />
          </div>
        </section>
      </div>
    </div>
  );
}
