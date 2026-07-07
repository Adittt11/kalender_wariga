import { useEffect, useRef, useState } from "react";
import { CalendarSearch, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Moon } from "lucide-react";
import { getDashboardCalendarByMonth } from "../services/calendarApi";

const dayNames = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"];
const initialDate = new Date(1900, 0, 1);

const MONTHS_ID = [
  "Januari", "Februari", "Maret", "April", "Mei", "Juni",
  "Juli", "Agustus", "September", "Oktober", "November", "Desember",
];

function getMonthCells(year, month, monthData) {
  const firstDay = (new Date(year, month - 1, 1).getDay() + 6) % 7;
  const totalDays = new Date(year, month, 0).getDate();
  const cells = Array.from({ length: firstDay }, () => null);

  for (let day = 1; day <= totalDays; day += 1) {
    cells.push(monthData.find((item) => item.tanggal === day) || { tanggal: day });
  }

  while (cells.length % 7) {
    cells.push(null);
  }

  return cells;
}

function LunarMark({ status }) {
  if (!status || status === "-") {
    return null;
  }

  const tilem = status.toLowerCase().includes("tilem");

  return (
    <span className={`dashboard-lunar-mark ${tilem ? "dashboard-lunar-tilem" : "dashboard-lunar-purnama"}`}>
      {tilem && <Moon size={10} />}
    </span>
  );
}

export default function CalendarCard({ onMonthDataChange, onSelectDate, selectedDate }) {
  const [year, setYear] = useState(initialDate.getFullYear());
  const [month, setMonth] = useState(initialDate.getMonth() + 1);
  const [monthData, setMonthData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dateFilterOpen, setDateFilterOpen] = useState(false);
  const [jumpDate, setJumpDate] = useState("");
  const dateInputRef = useRef(null);

  useEffect(() => {
    async function loadMonth() {
      setLoading(true);
      setError("");

      try {
        const response = await getDashboardCalendarByMonth(year, month);
        const data = response.data || [];
        setMonthData(data);
        onMonthDataChange?.(data, { year, month });
      } catch (err) {
        setMonthData([]);
        onMonthDataChange?.([], { year, month });
        setError(
          err.response?.data?.detail ||
          err.message ||
          "Tidak dapat memuat kalender Dawuh dari backend."
        );
      } finally {
        setLoading(false);
      }
    }

    loadMonth();
  }, [month, year]);

  function moveMonth(offset) {
    const nextDate = new Date(year, month - 1 + offset, 1);
    setYear(nextDate.getFullYear());
    setMonth(nextDate.getMonth() + 1);
  }

  function moveYear(offset) {
    setYear((currentYear) => currentYear + offset);
  }

  function applyJumpDate(value) {
    if (!value) return;
    const d = new Date(value + "T00:00:00");
    if (isNaN(d)) return;
    setYear(d.getFullYear());
    setMonth(d.getMonth() + 1);
    onSelectDate?.(value);
    setDateFilterOpen(false);
    setJumpDate(value);
  }

  const cells = getMonthCells(year, month, monthData);
  const monthIndex = month - 1;

  return (
    <section className="card dashboard-calendar-card" style={{ position: "relative" }}>
      <div className="dashboard-calendar-toolbar">
        <div className="dashboard-calendar-nav" aria-label="Navigasi bulan dan tahun">
          <button
            className="calendar-nav-button calendar-year-nav-button"
            type="button"
            title="Tahun sebelumnya"
            onClick={() => moveYear(-1)}
          >
            <ChevronsLeft size={18} />
          </button>
          <button
            className="calendar-nav-button"
            type="button"
            title="Bulan sebelumnya"
            onClick={() => moveMonth(-1)}
          >
            <ChevronLeft size={18} />
          </button>

          <div className="cal-month-label" aria-live="polite">
            <span>{MONTHS_ID[monthIndex]}</span>
            <span>{year}</span>
          </div>

          <button
            className="calendar-nav-button"
            type="button"
            title="Bulan berikutnya"
            onClick={() => moveMonth(1)}
          >
            <ChevronRight size={18} />
          </button>
          <button
            className="calendar-nav-button calendar-year-nav-button"
            type="button"
            title="Tahun berikutnya"
            onClick={() => moveYear(1)}
          >
            <ChevronsRight size={18} />
          </button>
        </div>

        <button
          className="cal-date-filter-btn"
          type="button"
          title="Pilih tanggal tertentu"
          onClick={() => setDateFilterOpen((open) => !open)}
        >
          <CalendarSearch size={16} />
        </button>
      </div>

      {dateFilterOpen && (
        <div className="cal-date-filter-panel">
          <p>Lompat ke tanggal:</p>
          <input
            ref={dateInputRef}
            type="date"
            className="cal-date-input"
            value={jumpDate}
            onChange={(e) => setJumpDate(e.target.value)}
          />
          <div className="cal-date-filter-actions">
            <button
              className="cal-filter-go-btn"
              type="button"
              onClick={() => applyJumpDate(jumpDate)}
            >
              Tampilkan
            </button>
            <button
              className="cal-filter-cancel-btn"
              type="button"
              onClick={() => setDateFilterOpen(false)}
            >
              Batal
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="py-16 text-center text-sm text-gray-500">Memuat kalender...</div>
      ) : error ? (
        <div className="m-4 rounded-2xl bg-red-50 p-4 text-sm text-red-700">{error}</div>
      ) : (
        <div className="dashboard-compact-calendar">
          {dayNames.map((day) => <strong key={day}>{day}</strong>)}
          {cells.map((item, index) => {
            const active = item?.tanggal_lengkap === selectedDate;

            return (
              <button
                key={`${item?.tanggal || "empty"}-${index}`}
                className={`dashboard-calendar-day ${active ? "dashboard-calendar-day-active" : ""}`}
                type="button"
                disabled={!item?.tanggal_lengkap}
                onClick={() => onSelectDate(item.tanggal_lengkap)}
              >
                {item?.tanggal}
                <LunarMark status={item?.status_purnama} />
              </button>
            );
          })}
        </div>
      )}

      {!loading && !error && !monthData.length && (
        <div className="m-4 flex items-center gap-3 rounded-2xl bg-baliSoft p-4 text-sm text-baliBrown">
          Data bulan ini belum tersedia di tabel kalender_bali.
        </div>
      )}
    </section>
  );
}
