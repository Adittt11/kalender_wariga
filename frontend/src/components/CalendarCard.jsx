import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Moon, Search, Sparkles } from "lucide-react";
import { getDashboardCalendarByMonth } from "../services/calendarApi";

const dayNames = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];
const initialDate = new Date(1900, 0, 1);

function getMonthLabel(year, month) {
  return new Intl.DateTimeFormat("id-ID", {
    month: "long",
    year: "numeric",
  }).format(new Date(year, month - 1, 1));
}

function getMonthRows(year, month, monthData) {
  const firstDay = new Date(year, month - 1, 1).getDay();
  const totalDays = new Date(year, month, 0).getDate();
  const cells = Array.from({ length: firstDay }, () => null);

  for (let day = 1; day <= totalDays; day += 1) {
    cells.push(monthData.find((item) => item.tanggal === day) || { tanggal: day });
  }

  while (cells.length % 7) {
    cells.push(null);
  }

  return Array.from({ length: cells.length / 7 }, (_, index) =>
    cells.slice(index * 7, index * 7 + 7)
  );
}

function LunarBadge({ status }) {
  if (!status || status === "-") {
    return null;
  }

  const tilem = status.toLowerCase().includes("tilem");

  return (
    <span className={`calendar-lunar-badge ${tilem ? "calendar-lunar-tilem" : "calendar-lunar-purnama"}`}>
      {tilem ? <Moon size={13} /> : <Sparkles size={13} />}
      {status}
    </span>
  );
}

export default function CalendarCard({ onSelectDate, selectedDate }) {
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
        setMonthData(response.data || []);
      } catch (err) {
        setMonthData([]);
        setError(
          err.response?.data?.detail ||
            err.message ||
            "Tidak dapat memuat kalender Bali dari backend."
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

  const rows = getMonthRows(year, month, monthData);

  return (
    <section className="card overflow-hidden p-4 sm:p-6">
      <div className="flex flex-col gap-4 border-b border-baliBorder pb-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-xl font-bold text-baliDark sm:text-2xl">Kalender Bali</h2>
          <p className="mt-1 text-sm text-gray-500">Klik tanggal untuk melihat detail kalender.</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button className="calendar-nav-button" type="button" onClick={() => moveMonth(-1)}>
            <ChevronLeft size={19} />
          </button>
          <div className="min-w-[170px] rounded-xl border border-baliBorder bg-baliSoft px-4 py-2 text-center text-sm font-semibold capitalize text-baliBrown">
            {getMonthLabel(year, month)}
          </div>
          <button className="calendar-nav-button" type="button" onClick={() => moveMonth(1)}>
            <ChevronRight size={19} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-sm text-gray-500">Memuat kalender...</div>
      ) : error ? (
        <div className="mt-5 rounded-2xl bg-red-50 p-4 text-sm text-red-700">{error}</div>
      ) : (
        <div className="mt-5 overflow-x-auto">
          <div className="min-w-[900px] overflow-hidden rounded-2xl border border-baliBorder">
            <div className="calendar-month-header">
              <div>Wuku</div>
              {dayNames.map((day, index) => (
                <div key={day} className={index === 0 ? "text-red-500" : ""}>{day}</div>
              ))}
            </div>

            {rows.map((week, index) => {
              const wuku = week.find((item) => item?.wuku)?.wuku || "-";

              return (
                <div key={index} className="calendar-month-row">
                  <div className="calendar-wuku-cell">{wuku}</div>
                  {week.map((item, dayIndex) => {
                    const active = item?.tanggal_lengkap === selectedDate;

                    return (
                      <button
                        key={`${index}-${dayIndex}`}
                        className={`calendar-day-cell ${active ? "calendar-day-selected" : ""}`}
                        type="button"
                        disabled={!item?.tanggal_lengkap}
                        onClick={() => onSelectDate(item.tanggal_lengkap)}
                      >
                        {item && (
                          <>
                            <strong className={dayIndex === 0 ? "text-red-500" : ""}>{item.tanggal}</strong>
                            {item.saptawara && (
                              <span>{item.saptawara.replace(/\s*\(\d+\)$/, "")} {item.pancawara?.replace(/\s*\(\d+\)$/, "")}</span>
                            )}
                            <LunarBadge status={item.status_purnama} />
                          </>
                        )}
                      </button>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!loading && !error && !monthData.length && (
        <div className="mt-5 flex items-center gap-3 rounded-2xl bg-baliSoft p-4 text-sm text-baliBrown">
          <Search size={18} />
          Data bulan ini belum tersedia di tabel kalender_bali.
        </div>
      )}
    </section>
  );
}
