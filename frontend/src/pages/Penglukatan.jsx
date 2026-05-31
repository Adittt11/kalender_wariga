import { Droplet } from "lucide-react";
import SmallCard from "../components/SmallCard";

export default function Penglukatan() {
  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <SmallCard title="Penglukatan" icon={<Droplet size={24} />}>
        Halaman ini siap dikembangkan untuk menampilkan informasi hari baik penglukatan.
      </SmallCard>
    </div>
  );
}