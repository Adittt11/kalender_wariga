import { NavLink } from "react-router-dom";
import {
  Home,
  Bot,
  UserRound,
  Sun,
  Printer,
  Droplet,
  HeartHandshake
} from "lucide-react";

import ornamen from "../assets/ornamen.png";
import pura from "../assets/pura1.png";

const menus = [
  { label: "Dashboard", path: "/", icon: Home },
  { label: "Tanya Wariga AI", path: "/tanya-wariga-ai", icon: Bot },
  { label: "Karakter kelahiran", path: "/karakter-kelahiran", icon: UserRound },
  { label: "Dewasa Ayu", path: "/dewasa-ayu", icon: Sun },
  { label: "Pertemuan Lanang Istri", path: "/pertemuan-lanang-istri", icon: HeartHandshake },
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
        className={`wariga-sidebar fixed left-0 top-0 z-50 flex h-screen w-[280px] flex-col overflow-hidden transition-transform duration-300 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Gambar Pura */}
        <div className="wariga-sidebar-scenery pointer-events-none absolute inset-x-0 bottom-0 z-0 overflow-hidden">
          <img
            src={pura}
            alt=""
            className="wariga-sidebar-scenery-image"
          />
        </div>

        {/* Title */}
        <div className="relative z-10 flex shrink-0 items-center gap-3 px-6 pb-6 pt-7">
          <img
            src={ornamen}
            alt=""
            className="h-14 w-14 object-contain brightness-0 invert sepia saturate-[4] hue-rotate-[350deg]"
          />
          <div>
            <h1 className="wariga-sidebar-title text-[25px] font-bold leading-none">
              WARIGA
            </h1>
            <p className="mt-1 text-sm font-medium tracking-wide text-[#e4bf82]">
              Kalender Bali
            </p>
          </div>
        </div>

        {/* Menu */}
        <nav className="relative z-10 flex-1 space-y-2 overflow-y-auto px-4 pb-[330px]">
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
                  `wariga-sidebar-menu flex items-center gap-4 rounded-xl px-4 py-3.5 text-[14px] transition ${
                    isActive
                      ? "wariga-sidebar-menu-active font-semibold"
                      : "hover:bg-white/10"
                  }`
                }
              >
                <Icon size={23} />
                <span>{menu.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
