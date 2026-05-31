import { Menu } from "lucide-react";
import ornamen from "../assets/ornamen.png";

export default function Header({ onOpenSidebar }) {
  return (
    <header className="flex min-h-[90px] items-center gap-4 bg-[#fbf6f0] px-4 py-4 sm:px-6 md:px-8">

      {/* Tombol Menu Mobile */}
      <button
        onClick={onOpenSidebar}
        className="rounded-xl border border-baliBorder p-2 text-baliBrown lg:hidden"
      >
        <Menu size={24} />
      </button>

      {/* Logo Ornamen */}
      <div className="flex-shrink-0">
        <img
          src={ornamen}
          alt="Ornamen Bali"
          className="h-16 w-auto object-contain sm:h-20 md:h-24"
        />
      </div>

      {/* Teks */}
      <div className="min-w-0">
        <h2 className="text-xl font-semibold text-baliDark sm:text-2xl md:text-[28px]">
          Om swastyastu
        </h2>

        <p className="mt-1 text-xs text-gray-500 sm:text-sm md:text-base">
          Selamat datang di dashboard kalender bali wariga
        </p>
      </div>
    </header>
  );
}