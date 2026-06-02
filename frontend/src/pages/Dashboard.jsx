import { useEffect, useState } from "react";
import { ArrowRight, Bot, CalendarDays, Clock3, Moon, Scale, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import CalendarCard from "../components/CalendarCard";
import { getDashboardCalendarByDate } from "../services/calendarApi";

const initialDate = "1900-01-01";

function splitValues(value, separator) {
  if (!value || value === "-") {
    return [];
  }

  return value.split(separator).map((item) => item.trim()).filter(Boolean);
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("id-ID", {
    weekday: "short",
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function InfoRows({ detail }) {
  const rows = [
    ["Ingkel", detail.ingkel, "Sasih", detail.sasih],
    ["Wuku", detail.wuku, detail.label_lunar, detail.nilai_lunar],
    ["Ekawara", detail.ekawara, "Sadwara", detail.sadwara],
    ["Dwiwara", detail.dwiwara, "Saptawara", detail.saptawara],
    ["Triwara", detail.triwara, "Astawara", detail.astawara],
    ["Caturwara", detail.caturwara, "Sangawara", detail.sangawara],
    ["Pancawara", detail.pancawara, "Dasawara", detail.dasawara],
    ["Ekajalarsi", detail.ekajalarsi, "Pararasan", detail.pararasan],
    ["Palalintangan", detail.palalintangan, "Pratiti Samutpada", detail.pratiti_samutpada],
  ];

  return (
    <div className="dashboard-info-rows">
      {rows.map((row, index) => (
        <div className={index === 2 || index === 7 ? "dashboard-info-row dashboard-info-separator" : "dashboard-info-row"} key={row[0]}>
          <span>{row[0]}</span><strong>{row[1] || "-"}</strong>
          <span>{row[2]}</span><strong>{row[3] || "-"}</strong>
        </div>
      ))}
    </div>
  );
}

function LunarStatus({ status }) {
  if (!status || status === "-") {
    return null;
  }

  const tilem = status.toLowerCase().includes("tilem");

  return (
    <div className={`dashboard-status ${tilem ? "dashboard-status-tilem" : "dashboard-status-purnama"}`}>
      {tilem ? <Moon size={16} /> : <Sparkles size={16} />}
      Hari {status}
    </div>
  );
}

export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState(initialDate);
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState("");

  async function loadDate(date) {
    setSelectedDate(date);
    setLoadingDetail(true);
    setError("");

    try {
      const response = await getDashboardCalendarByDate(date);
      setDetail(response.data);
    } catch (err) {
      setDetail(null);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Detail kalender Dawuh tidak dapat dimuat."
      );
    } finally {
      setLoadingDetail(false);
    }
  }

  useEffect(() => {
    loadDate(initialDate);
  }, []);

  const goodTimes = splitValues(detail?.dawuh, "|");

  return (
    <div className="dashboard-page">
      <div className="dashboard-layout">
        <div className="space-y-5">
          <Link className="card dashboard-ai-shortcut" to="/tanya-wariga-ai">
            <div className="dashboard-card-icon"><Bot size={19} /></div>
            <div>
              <h2>Tanya Wariga AI</h2>
              <p>Tanyakan informasi kalender Bali dan Wariga.</p>
            </div>
            <ArrowRight className="ml-auto" size={20} />
          </Link>

          <CalendarCard onSelectDate={loadDate} selectedDate={selectedDate} />

          <section className="card dashboard-data-card">
            <div className="dashboard-card-heading">
              <div className="dashboard-card-icon"><Clock3 size={19} /></div>
              <h2>Waktu Baik</h2>
            </div>
            <div className="dashboard-time-tags">
              {goodTimes.length
                ? goodTimes.map((item) => <span key={item}>{item}</span>)
                : <p>Tidak ada waktu khusus.</p>}
            </div>
          </section>
        </div>

        <div className="space-y-5">
          <section className="card dashboard-info-card">
            <div className="dashboard-info-heading">
              <div className="dashboard-card-heading">
                <div className="dashboard-card-icon"><CalendarDays size={19} /></div>
                <h2>Informasi Kalender</h2>
              </div>
              <strong>{formatDate(selectedDate)}</strong>
            </div>
            {loadingDetail ? (
              <p className="py-12 text-center text-sm text-gray-500">Memuat informasi...</p>
            ) : detail ? (
              <>
                <LunarStatus status={detail.status_purnama} />
                <InfoRows detail={detail} />
              </>
            ) : (
              <p className="py-12 text-center text-sm text-gray-500">{error}</p>
            )}
          </section>

          <section className="card dashboard-data-card dashboard-dewasa-card">
            <div className="dashboard-card-heading">
              <div className="dashboard-card-icon"><Scale size={19} /></div>
              <h2>Ala - Ayu Dewasa</h2>
            </div>
            <p><strong>Pakakalan:</strong> {detail?.pakakalan || "-"}</p>
            <p className="mt-3 text-gray-600">{detail?.baik_buruk_hari || "Tidak ada informasi khusus."}</p>
          </section>
        </div>
      </div>

    </div>
  );
}
