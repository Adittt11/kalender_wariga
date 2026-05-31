import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "../components/Layout";
import Dashboard from "../pages/Dashboard";
import CetakKalender from "../pages/CetakKalender";
import TanyaWarigaAI from "../pages/TanyaWarigaAI";
import KarakterKelahiran from "../pages/KarakterKelahiran";
import DewasaAyu from "../pages/DewasaAyu";
import Penglukatan from "../pages/Penglukatan";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tanya-wariga-ai" element={<TanyaWarigaAI />} />
          <Route path="/karakter-kelahiran" element={<KarakterKelahiran />} />
          <Route path="/dewasa-ayu" element={<DewasaAyu />} />
          <Route path="/cetak-kalender" element={<CetakKalender />} />
          <Route path="/penglukatan" element={<Penglukatan />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
