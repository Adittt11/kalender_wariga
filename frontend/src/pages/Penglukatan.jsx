import { useState } from "react";
import { CalendarDays, Droplets, Search, Sparkles } from "lucide-react";
import { getPebayuhan } from "../services/pebayuhanApi";

function formatDate(dateStr) {
  if (!dateStr) return "-";
  return new Intl.DateTimeFormat("id-ID", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(`${dateStr}T00:00:00`));
}

export default function Penglukatan() {
  const [date, setDate] = useState("1960-01-01");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await getPebayuhan(date);
      setResult(response.data.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Tidak dapat mengambil data pebayuhan dari server."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      {/* Hero-form section */}
      <section className="overflow-hidden rounded-3xl bg-gradient-to-br from-[#5A321D] to-[#8A5838] p-6 text-white shadow-soft sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15">
              <Droplets size={25} />
            </div>
            <h1 className="mt-5 text-2xl font-bold sm:text-3xl">Pebayuhan</h1>
            <p className="mt-3 text-sm leading-7 text-white/80 sm:text-base">
              Temukan banten pebayuhan berdasarkan tanggal lahir Anda.
              Sistem akan menentukan Saptawara dan Pancawara lalu menampilkan
              sarana pebayuhan yang sesuai.
            </p>
          </div>

          <form
            className="flex w-full flex-col gap-3 rounded-2xl bg-white/10 p-4 backdrop-blur-sm sm:flex-row lg:max-w-xl"
            onSubmit={handleSubmit}
          >
            <label className="flex flex-1 items-center gap-3 rounded-xl bg-white px-4 text-baliDark">
              <CalendarDays size={20} className="text-baliBrown" />
              <input
                className="w-full bg-transparent py-3 text-sm outline-none"
                type="date"
                value={date}
                min="1900-01-01"
                max="1979-12-31"
                onChange={(e) => setDate(e.target.value)}
                required
              />
            </label>
            <button
              className="flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-baliBrown transition hover:bg-baliSoft disabled:opacity-60"
              type="submit"
              disabled={loading}
            >
              <Search size={18} />
              {loading ? "Memuat..." : "Cari Pebayuhan"}
            </button>
          </form>
        </div>
      </section>

      {/* Error */}
      {error && (
        <div className="mt-6 rounded-2xl bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Empty state */}
      {!result && !error && (
        <section className="mt-6 rounded-3xl border border-baliBorder bg-white p-8 text-center shadow-soft">
          <Sparkles className="mx-auto text-baliBrown" size={28} />
          <p className="mt-4 text-sm leading-7 text-gray-500">
            Masukkan tanggal lahir untuk menampilkan data pebayuhan.
          </p>
        </section>
      )}

      {/* Result */}
      {result && (
        <div className="mt-6 space-y-6">
          {/* Summary badge */}
          <section className="rounded-3xl border border-baliBorder bg-white p-5 shadow-soft sm:p-7">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-baliBrown">
              Hasil Pebayuhan
            </p>
            <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <h2 className="text-2xl font-bold text-baliDark">
                {formatDate(result.tanggal_lahir)}
              </h2>
              <p className="text-sm text-gray-500">
                {result.saptawara} · {result.pancawara}
              </p>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl bg-baliSoft p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Saptawara</p>
                <p className="mt-2 font-semibold text-baliBrown">{result.saptawara}</p>
              </div>
              <div className="rounded-2xl bg-baliSoft p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Pancawara</p>
                <p className="mt-2 font-semibold text-baliBrown">{result.pancawara}</p>
              </div>
            </div>
          </section>

          {/* Pebayuhan cards */}
          {result.pebayuhan && result.pebayuhan.length > 0 ? (
            result.pebayuhan.map((item, idx) => (
              <section
                key={idx}
                className="rounded-3xl border border-baliBorder bg-white p-5 shadow-soft sm:p-7"
              >
                <div className="flex items-center gap-3 border-b border-baliBorder pb-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-baliCream text-baliBrown">
                    <Droplets size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold text-baliDark">
                      {item.Saptawara} – {item.Pancawara}
                    </h3>
                  </div>
                </div>

                {item.Keterangan && (
                  <div className="mt-5">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-baliBrown">
                      {item.Saptawara}
                    </p>
                    <p className="whitespace-pre-line text-justify text-sm leading-8 text-gray-600">
                      {item.Keterangan}
                    </p>
                  </div>
                )}

                {item.Keterangan_1 && (
                  <div className="mt-5 border-t border-baliBorder pt-5">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-baliBrown">
                      {item.Pancawara}
                    </p>
                    <p className="whitespace-pre-line text-justify text-sm leading-8 text-gray-600">
                      {item.Keterangan_1}
                    </p>
                  </div>
                )}

                {item.kweh_toya_pancoran != null && (
                  <div className="mt-5 inline-flex items-center gap-2 rounded-xl bg-baliCream px-4 py-2">
                    <Droplets size={16} className="text-baliBrown" />
                    <span className="text-sm font-semibold text-baliBrown">
                      Kweh Toya Pancoran: {item.kweh_toya_pancoran}
                    </span>
                  </div>
                )}
              </section>
            ))
          ) : (
            <section className="rounded-3xl border border-baliBorder bg-white p-8 text-center shadow-soft">
              <p className="text-sm text-gray-500">
                Tidak ditemukan data pebayuhan untuk{" "}
                <span className="font-semibold text-baliBrown">
                  {result.saptawara} – {result.pancawara}
                </span>
                .
              </p>
            </section>
          )}
        </div>
      )}
    </div>
  );
}