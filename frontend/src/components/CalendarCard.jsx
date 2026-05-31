import { ChevronLeft, ChevronRight, SlidersHorizontal } from "lucide-react";

const days = ["Sen", "Sel", "Rab", "Kam", "Jum", "Min"];
const dates = Array.from({ length: 30 }, (_, i) => i + 1);
const redDates = [6, 10, 12, 18, 19, 24, 30];

export default function CalendarCard() {
  return (
    <section className="card p-6">
      <div className="mb-5 flex items-center gap-3">
        <button className="rounded-xl border border-baliBorder p-2 hover:bg-baliSoft">
          <ChevronLeft size={20} />
        </button>
        <div className="flex-1 text-center">
          <h3 className="font-semibold">Mei 2026</h3>
        </div>
        <button className="rounded-xl border border-baliBorder p-2 hover:bg-baliSoft">
          <ChevronRight size={20} />
        </button>
        <button className="rounded-xl border border-baliBorder p-2 hover:bg-baliSoft">
          <SlidersHorizontal size={20} />
        </button>
      </div>

      <div className="rounded-2xl border border-baliBorder p-5">
        <div className="grid grid-cols-6 gap-y-5 text-center text-sm">
          {days.map((day) => (
            <div key={day} className="font-semibold">
              {day}
            </div>
          ))}

          {dates.map((date) => (
            <div key={date} className="flex justify-center">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm ${
                  date === 15
                    ? "bg-baliBrown font-semibold text-white"
                    : date === 10
                    ? "rounded-full border border-red-500 text-red-500"
                    : redDates.includes(date)
                    ? "text-red-500"
                    : "text-baliDark"
                }`}
              >
                {date}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
