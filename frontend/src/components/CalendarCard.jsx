import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Moon, Search } from "lucide-react";
import { getDashboardCalendarByMonth } from "../services/calendarApi";

const dayNames = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"];
const initialDate = new Date(1900, 0, 1);

function getMonthLabel(year, month) {
  return new Intl.DateTimeFormat("id-ID", {
    month: "long",
    year: "numeric",
  }).format(new Date(year, month - 1, 1));
}

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

  const cells = getMonthCells(year, month, monthData);

  return (
    <section className="card dashboard-calendar-card">
      <div className="dashboard-calendar-toolbar">
        <button className="calendar-nav-button" type="button" onClick={() => moveMonth(-1)}>
          <ChevronLeft size={18} />
        </button>
        <h2 className="capitalize">{getMonthLabel(year, month)}</h2>
        <button className="calendar-nav-button" type="button" onClick={() => moveMonth(1)}>
          <ChevronRight size={18} />
        </button>
      </div>

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
          <Search size={18} />
          Data bulan ini belum tersedia di tabel kalender_bali.
        </div>
      )}
    </section>
  );
}
