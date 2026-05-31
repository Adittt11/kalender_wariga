import { Outlet } from "react-router-dom";
import { useState } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";
import BackgroundMusic from "./BackgroundMusic";

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-baliBg">
      <BackgroundMusic />
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main
        className={`min-h-screen transition-all duration-300 ${
          sidebarOpen ? "lg:pl-[280px]" : "lg:pl-0"
        }`}
      >
        <Header
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />

        <section className="min-h-[calc(100vh-90px)] p-4 sm:p-5 md:p-7">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
