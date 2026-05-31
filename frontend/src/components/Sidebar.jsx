import { NavLink } from "react-router-dom";
import {
  Home,
  Bot,
  UserRound,
  Sun,
  Printer,
  Droplet
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
      {/* Overlay mobile */}
      <div
        onClick={onClose}
        className={`fixed inset-0 z-40 bg-black/40 transition lg:hidden ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      />

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-50 h-screen w-[280px] overflow-hidden border-r border-baliBorder bg-[#fbf6f0] transition-transform duration-300 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Title */}
        <div className="px-6 pt-8">
          <h1 className="text-[24px] font-bold leading-tight text-baliDark">
            Kalender Bali
            <br />
            Wariga
          </h1>

          <div className="my-7 h-[1px] bg-baliBrown/80" />
        </div>

        {/* Menu */}
        <nav className="space-y-3 px-4">
          {menus.map((menu) => {
            const Icon = menu.icon;

            return (
              <NavLink
                key={menu.path}
                to={menu.path}
                onClick={() => {
                  if (window.innerWidth < 1024) onClose();
                }}
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
        <div className="absolute bottom-0 left-0 right-0 flex justify-center">
          <img
            src={pura}
            alt="Pura Bali"
            className="w-[230px] object-contain opacity-80"
          />
        </div>
      </aside>
    </>
  );
}