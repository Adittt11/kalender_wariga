import { useState } from "react";
import { CalendarDays, Moon, Sparkles, X } from "lucide-react";
import CalendarCard from "../components/CalendarCard";
import { getDashboardCalendarByDate } from "../services/calendarApi";

function DetailRow({ label, value }) {
  return (
    <div className="rounded-xl bg-baliSoft p-3">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-baliBrown">{value || "-"}</p>
    </div>
  );
}

export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState("");
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState("");

  async function selectDate(date) {
    setSelectedDate(date);
    setLoadingDetail(true);
    setError("");

    try {
      const response = await getDashboardCalendarByDate(date);
      setDetail(response.data);
    } catch (err) {
      setDetail(null);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Detail kalender Bali tidak dapat dimuat."
      );
    } finally {
      setLoadingDetail(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <CalendarCard onSelectDate={selectDate} selectedDate={selectedDate} />

      {loadingDetail && (
        <div className="mt-6 rounded-2xl bg-white p-5 text-center text-sm text-gray-500 shadow-soft">
          Memuat detail tanggal...
        </div>
      )}

      {error && (
        <div className="mt-6 rounded-2xl bg-red-50 p-4 text-sm text-red-700">{error}</div>
      )}

      {detail && !loadingDetail && (
        <section className="mt-6 rounded-3xl border border-baliBorder bg-white p-5 shadow-soft sm:p-7">
          <div className="flex flex-col gap-4 border-b border-baliBorder pb-5 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-baliBrown">Detail Kalender Bali</p>
              <h2 className="mt-2 text-2xl font-bold text-baliDark">{detail.tanggal_lengkap}</h2>
              <p className="mt-1 text-sm text-gray-500">{detail.saptawara} · {detail.pancawara}</p>
            </div>
            <button className="calendar-nav-button" type="button" onClick={() => setDetail(null)}>
              <X size={18} />
            </button>
          </div>

          {detail.status_purnama !== "-" && (
            <div className={`mt-5 flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold ${
              detail.status_purnama.toLowerCase().includes("tilem")
                ? "bg-gray-900 text-white"
                : "bg-red-50 text-red-700"
            }`}>
              {detail.status_purnama.toLowerCase().includes("tilem") ? <Moon size={18} /> : <Sparkles size={18} />}
              Hari {detail.status_purnama}
            </div>
          )}

          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <DetailRow label="Wuku" value={detail.wuku} />
            <DetailRow label="Ingkel" value={detail.ingkel} />
            <DetailRow label="Sasih" value={detail.sasih} />
            <DetailRow label={detail.label_lunar} value={detail.nilai_lunar} />
            <DetailRow label="Ekawara" value={detail.ekawara} />
            <DetailRow label="Dwiwara" value={detail.dwiwara} />
            <DetailRow label="Triwara" value={detail.triwara} />
            <DetailRow label="Caturwara" value={detail.caturwara} />
            <DetailRow label="Pancawara" value={detail.pancawara} />
            <DetailRow label="Sadwara" value={detail.sadwara} />
            <DetailRow label="Saptawara" value={detail.saptawara} />
            <DetailRow label="Astawara" value={detail.astawara} />
            <DetailRow label="Sangawara" value={detail.sangawara} />
            <DetailRow label="Dasawara" value={detail.dasawara} />
          </div>

          <div className="mt-5 flex items-center gap-2 text-xs text-gray-500">
            <CalendarDays size={15} />
            Data detail diambil dari tabel kalender_bali.
          </div>
        </section>
      )}
    </div>
  );
}
