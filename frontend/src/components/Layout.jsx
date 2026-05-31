import { Outlet } from "react-router-dom";
import { useState } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-baliBg">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="min-h-screen lg:pl-[280px]">
        <Header onOpenSidebar={() => setSidebarOpen(true)} />
        <section className="p-4 sm:p-5 md:p-7">
          <Outlet />
        </section>
      </main>
    </div>
  );
}