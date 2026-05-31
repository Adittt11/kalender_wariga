import { UserRound } from "lucide-react";
import SmallCard from "../components/SmallCard";
import { calendarInfo } from "../data/mockCalendar";

export default function KarakterKelahiran() {
  return (
    <SmallCard title="Karakter Kelahiran" icon={<UserRound size={24} />}>
      {calendarInfo.karakter}
    </SmallCard>
  );
}
