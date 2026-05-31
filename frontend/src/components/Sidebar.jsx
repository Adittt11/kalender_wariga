import { NavLink } from "react-router-dom";
import {
  Home,
  Bot,
  UserRound,
  Sun,
  Printer,
  Droplet,
  Menu,
  X
} from "lucide-react";

import pura from "../assets/pura.png";

const menus = [
  { label: "Dashboard", path: "/", icon: Home },
  { label: "Tanya Wariga AI", path: "/tanya-wariga-ai", icon: Bot },
  { label: "Karakter kelahiran", path: "/karakter-kelahiran", icon: UserRound },
  { label: "Dewasa Ayu", path: "/dewasa-ayu", icon: Sun },
  { label: "Cetak Kalender", path: "/cetak-kalender", icon: Printer },
  { label: "Penglukatan", path: "/penglukatan", icon: Droplet }
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Overlay Mobile */}
      <div
        onClick={onClose}
        className={`fixed inset-0 z-40 bg-black/40 transition lg:hidden ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      />

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-50 h-screen w-[280px] overflow-hidden border-r border-baliBorder bg-[#fbf6f0] transition-transform duration-300 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Header Sidebar */}
        <div className="px-6 pt-7">
          <div className="flex items-start justify-between">
            <h1 className="text-[24px] font-bold leading-tight text-baliDark">
              Kalender Bali
              <br />
              Wariga
            </h1>

            <button
              onClick={onClose}
              className="rounded-xl p-2 text-baliBrown lg:hidden"
            >
              <X size={26} />
            </button>

            <Menu
              className="mt-2 hidden text-baliBrown lg:block"
              size={28}
            />
          </div>

          <div className="my-7 h-[1px] bg-baliBrown/80" />
        </div>

        {/* Menu */}
        <nav className="px-4 space-y-3">
          {menus.map((menu) => {
            const Icon = menu.icon;

            return (
              <NavLink
                key={menu.path}
                to={menu.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-4 rounded-2xl px-5 py-4 text-[14px] transition ${
                    isActive
                      ? "bg-baliCream font-semibold text-baliBrown"
                      : "text-baliDark hover:bg-baliCream/60"
                  }`
                }
              >
                <Icon size={23} />
                <span>{menu.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Gambar Pura */}
        <div className="absolute bottom-0 left-0 right-0">
          <img
            src={pura}
            alt="Pura Bali"
            className="w-full object-cover opacity-90"
          />
        </div>
      </aside>
    </>
  );
}