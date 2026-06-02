import { Menu, Moon, Sun } from "lucide-react";
import ornamen from "../assets/ornamen.png";

export default function Header({ darkMode, onToggleSidebar, onToggleTheme }) {
  return (
    <header className="wariga-header">
      <div className="wariga-header-cloud wariga-header-cloud-left" />
      <div className="wariga-header-cloud wariga-header-cloud-right" />

      <button
        onClick={onToggleSidebar}
        className="wariga-header-menu-button"
        type="button"
        aria-label="Buka atau tutup sidebar"
      >
        <Menu size={24} />
      </button>

      <img
        src={ornamen}
        alt="Ornamen Bali"
        className="wariga-header-logo"
      />

      <div className="relative z-10 min-w-0">
        <h2 className="wariga-header-title">
          Kalender Bali
        </h2>
        <p className="wariga-header-subtitle">
          Wariga, Wuku, Sasih &amp; Rahina
        </p>
      </div>

      <div className="wariga-header-divider" aria-hidden="true">
        <span />
        <img src={ornamen} alt="" />
        <span />
      </div>

      <button
        onClick={onToggleTheme}
        className="wariga-header-theme-button"
        type="button"
        aria-label={darkMode ? "Aktifkan light mode" : "Aktifkan night mode"}
        title={darkMode ? "Light mode" : "Night mode"}
      >
        {darkMode ? <Sun size={21} /> : <Moon size={21} />}
      </button>
    </header>
  );
}
