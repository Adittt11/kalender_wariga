import { Clock, Scale, UserRound } from "lucide-react";
import CalendarCard from "../components/CalendarCard";
import ChatWariga from "../components/ChatWariga";
import InfoKalender from "../components/InfoKalender";
import SmallCard from "../components/SmallCard";
import { calendarInfo } from "../data/mockCalendar";

export default function Dashboard() {
  return (
    <div className="grid grid-cols-1 gap-5 md:gap-7 xl:grid-cols-2">
      <div className="space-y-5 md:space-y-7">
        <InfoKalender />

        <SmallCard title="Karakter Kelahiran" icon={<UserRound size={23} />}>
          {calendarInfo.karakter}
        </SmallCard>
      </div>

      <div className="space-y-5 md:space-y-7">
        <CalendarCard />

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <SmallCard title="Pakakalan" icon={<Scale size={23} />}>
            {calendarInfo.pakakalan.join(", ")}
          </SmallCard>

          <SmallCard title="Waktu Baik" icon={<Clock size={23} />}>
            <div className="flex flex-wrap gap-3">
              {calendarInfo.waktuBaik.map((item) => (
                <span
                  key={item}
                  className="rounded-xl bg-baliBrown px-4 py-2 text-xs font-medium text-white"
                >
                  {item}
                </span>
              ))}
            </div>
          </SmallCard>
        </div>

        <ChatWariga />
      </div>
    </div>
  );
}