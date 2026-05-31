import { Sun } from "lucide-react";
import SmallCard from "../components/SmallCard";

export default function DewasaAyu() {
  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <SmallCard title="Dewasa Ayu" icon={<Sun size={24} />}>
        Halaman ini siap dihubungkan dengan data Dewasa Ayu dari backend atau Supabase.
      </SmallCard>
    </div>
  );
}