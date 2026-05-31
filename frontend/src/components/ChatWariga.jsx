import { useState } from "react";
import { Bot, Send } from "lucide-react";
import { getCalendarByDate } from "../services/calendarApi";

export default function ChatWariga() {
  const [queryDate, setQueryDate] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setResult(null);

    const date = queryDate.trim();
    if (!date) {
      setError("Masukkan tanggal dalam format YYYY-MM-DD.");
      return;
    }

    setLoading(true);
    try {
      const response = await getCalendarByDate(date);
      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Terjadi kesalahan pada koneksi backend."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card p-5">
      <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-center">
        <div className="rounded-full bg-baliCream p-3 text-baliBrown">
          <Bot size={23} />
        </div>
        <div className="sm:flex-1">
          <h3 className="text-lg font-semibold">Tanya Wariga AI</h3>
          <p className="mt-1 text-sm leading-relaxed text-gray-500">
            Coba masukkan tanggal kalender untuk melihat data Wariga dari backend.
          </p>
        </div>
      </div>

      <form className="flex flex-col gap-3 md:flex-row" onSubmit={handleSubmit}>
        <input
          className="flex-1 rounded-2xl border border-baliBorder bg-white px-4 py-3 text-sm outline-none focus:border-baliBrown"
          placeholder="YYYY-MM-DD"
          value={queryDate}
          onChange={(event) => setQueryDate(event.target.value)}
        />
        <button
          type="submit"
          className="btn-primary flex items-center justify-center gap-2 px-5 py-3"
          disabled={loading}
        >
          <Send size={17} />
          {loading ? "Memuat..." : "Kirim"}
        </button>
      </form>

      {error && (
        <div className="mt-4 rounded-2xl bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-4 space-y-3 rounded-3xl border border-baliBorder bg-white p-5 text-sm shadow-sm">
          <div className="text-sm text-gray-500">
            Hasil dari backend untuk tanggal <span className="font-semibold">{result.tanggal_lengkap}</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl bg-baliCream p-4">
              <div className="text-xs uppercase text-gray-500">Pancawara</div>
              <div className="mt-2 font-semibold text-baliBrown">{result.pancawara}</div>
            </div>
            <div className="rounded-2xl bg-baliCream p-4">
              <div className="text-xs uppercase text-gray-500">Sadwara</div>
              <div className="mt-2 font-semibold text-baliBrown">{result.sadwara}</div>
            </div>
            <div className="rounded-2xl bg-baliCream p-4">
              <div className="text-xs uppercase text-gray-500">Saptawara</div>
              <div className="mt-2 font-semibold text-baliBrown">{result.saptawara}</div>
            </div>
            <div className="rounded-2xl bg-baliCream p-4">
              <div className="text-xs uppercase text-gray-500">Pakakalan</div>
              <div className="mt-2 font-semibold text-baliBrown">{result.pakakalan}</div>
            </div>
          </div>
          <div className="rounded-2xl bg-baliSoft p-4 text-sm leading-6 text-gray-700">
            <div className="font-semibold">Dawuh</div>
            <p className="mt-2">{result.dawuh}</p>
          </div>
        </div>
      )}
    </section>
  );
}
