import { Menu, Moon, Sun } from "lucide-react";
import ornamen from "../assets/ornamen.png";

export default function Header({ darkMode, onToggleSidebar, onToggleTheme }) {
  return (
    <header className="flex min-h-[90px] items-center gap-5 border-b border-baliBorder bg-white px-4 py-4 sm:px-6 md:px-8">
      {/* Tombol Sidebar */}
      <button
        onClick={onToggleSidebar}
        className="flex h-11 w-11 items-center justify-center rounded-xl border border-baliBorder bg-white text-baliBrown shadow-sm transition hover:bg-baliSoft"
      >
        <Menu size={24} />
      </button>

      {/* Logo */}
      <img
        src={ornamen}
        alt="Ornamen Bali"
        className="h-16 w-auto object-contain sm:h-20 md:h-24"
      />

      {/* Text */}
      <div className="min-w-0">
        <h2 className="text-xl font-semibold text-baliDark sm:text-2xl md:text-[28px]">
          Om swastyastu
        </h2>

        <p className="mt-1 text-xs text-gray-500 sm:text-sm md:text-base">
          Selamat datang di dashboard kalender bali wariga
        </p>
      </div>

      <button
        onClick={onToggleTheme}
        className="ml-auto flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-baliBorder bg-white text-baliBrown shadow-sm transition hover:bg-baliSoft"
        type="button"
        aria-label={darkMode ? "Aktifkan light mode" : "Aktifkan night mode"}
        title={darkMode ? "Light mode" : "Night mode"}
      >
        {darkMode ? <Sun size={21} /> : <Moon size={21} />}
      </button>
    </header>
  );
}
