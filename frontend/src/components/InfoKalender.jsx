import { CalendarDays } from "lucide-react";
import { calendarInfo } from "../data/mockCalendar";

export default function InfoKalender() {
  return (
    <section className="card p-7">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="rounded-full bg-baliCream p-3 text-baliBrown">
            <CalendarDays size={24} />
          </div>
          <h3 className="text-lg font-semibold">Informasi Kalender</h3>
        </div>
        <p className="text-sm font-semibold">{calendarInfo.dateLabel}</p>
      </div>

      <div className="space-y-2">
        {calendarInfo.rows.map((row, index) => (
          <div
            key={index}
            className={`grid grid-cols-4 gap-4 text-[13px] leading-relaxed ${
              index === 2 || index === 7 ? "mt-4 border-t border-baliBorder pt-4" : ""
            }`}
          >
            <span className="text-gray-500">{row[0]}</span>
            <span className="font-semibold">{row[1]}</span>
            <span className="text-gray-500">{row[2]}</span>
            <span className="font-semibold">{row[3]}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
