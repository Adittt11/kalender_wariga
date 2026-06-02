import { useEffect, useRef, useState } from "react";
import { CalendarDays, CheckSquare, CircleCheck, CircleX, Printer } from "lucide-react";
import { toPng } from "html-to-image";
import DownloadCard from "../components/DownloadCard";
import { generateCalendar, generatePrintAi } from "../services/calendarApi";
import ornament from "../assets/ornamen.png";

const initialStartDate = "1900-01-01";
const initialEndDate = "1900-01-02";

function formatDate(date) {
  if (!date) {
    return "-";
  }

  return new Intl.DateTimeFormat("id-ID", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(`${date}T00:00:00`));
}

function splitValues(value, separator) {
  if (!value || value === "-") {
    return [];
  }

  return value
    .split(separator)
    .map((item) => item.trim())
    .filter(Boolean);
}

function OrnamentDivider() {
  return (
    <div className="print-ornament-divider">
      <span />
      <img src={ornament} alt="" />
      <span />
    </div>
  );
}

function getCalendarTheme(status) {
  const normalizedStatus = String(status || "").toLowerCase();

  if (normalizedStatus.includes("purnama")) {
    return "print-calendar-purnama";
  }

  if (normalizedStatus.includes("tilem")) {
    return "print-calendar-tilem";
  }

  return "print-calendar-regular";
}

function PrintableCalendar({ calendarRef, data }) {
  const pakakalan = splitValues(data.pakakalan, ",");
  const goodTimes = splitValues(data.dawuh, "|");
  const leftWewaran = [
    ["Ekawara", data.ekawara],
    ["Dwiwara", data.dwiwara],
    ["Triwara", data.triwara],
    ["Caturwara", data.caturwara],
    ["Pancawara", data.pancawara],
  ];
  const rightWewaran = [
    ["Sadwara", data.sadwara],
    ["Saptawara", data.saptawara],
    ["Astawara", data.astawara],
    ["Sangawara", data.sangawara],
    ["Dasawara", data.dasawara],
  ];
  const karakterDasar = [
    ["Ekajalarsi", data.ekajalarsi],
    ["Palalintangan", data.palalintangan],
    ["Pararasan", data.pararasan],
    ["Pratiti Samutpada", data.pratiti_samutpada],
  ];

  return (
    <article ref={calendarRef} className={`print-calendar ${getCalendarTheme(data.status_purnama)}`}>
      <div className="print-calendar-frame">
        <OrnamentDivider />

        <h1 className="print-calendar-date">
          {data.tanggal} {new Intl.DateTimeFormat("id-ID", { month: "long" }).format(
            new Date(`${data.tanggal_lengkap}T00:00:00`)
          )} {data.tahun}
        </h1>

        <div className="print-calendar-summary">
          {[
            ["Ingkel", data.ingkel],
            ["Wuku", data.wuku],
            ["Sasih", data.sasih],
            [data.label_lunar, data.nilai_lunar],
          ].map(([label, value]) => (
            <div key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>

        <div className="print-wewaran-grid">
          {[leftWewaran, rightWewaran].map((column, index) => (
            <div key={index} className="print-wewaran-column">
              {column.map(([label, value]) => (
                <div key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          ))}
        </div>

        <div className="print-character-grid">
          {karakterDasar.map(([label, value]) => (
            <div key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>

        <section className="print-calendar-section">
          <h2>Karakter Kelahiran</h2>
          <p>{data.karakter_kelahiran}</p>
        </section>

        <section className="print-calendar-section">
          <h2>Pakakalan</h2>
          <div className="print-calendar-tags">
            {pakakalan.map((item) => <span key={item}>{item}</span>)}
          </div>
        </section>

        <section className="print-calendar-section">
          <h2>Baik Buruk Hari</h2>
          <div className="print-day-guidance">
            <div className="print-day-guidance-good">
              <h3><CircleCheck size={15} /> Hal yang Baik</h3>
              <ul>
                {(data.hal_baik || []).map((item) => <li key={item}>{item}</li>)}
                {!data.hal_baik?.length && <li>Tidak ada informasi khusus.</li>}
              </ul>
            </div>
            <div className="print-day-guidance-avoid">
              <h3><CircleX size={15} /> Hal yang Harus Dihindari</h3>
              <ul>
                {(data.hal_dihindari || []).map((item) => <li key={item}>{item}</li>)}
                {!data.hal_dihindari?.length && <li>Tidak ada informasi khusus.</li>}
              </ul>
            </div>
          </div>
        </section>

        <section className="print-calendar-section">
          <h2>Waktu Baik</h2>
          <div className="print-calendar-tags">
            {goodTimes.length ? (
              goodTimes.map((item) => <span key={item}>{item}</span>)
            ) : (
              <p>Tidak ada waktu khusus.</p>
            )}
          </div>
        </section>

        <OrnamentDivider />
      </div>
    </article>
  );
}

export default function CetakKalender() {
  const [startDate, setStartDate] = useState(initialStartDate);
  const [endDate, setEndDate] = useState(initialEndDate);
  const [calendarData, setCalendarData] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [downloadingPng, setDownloadingPng] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [loadingAi, setLoadingAi] = useState(false);
  const [error, setError] = useState("");
  const calendarRef = useRef(null);
  const aiCacheRef = useRef({});

  const preview = calendarData[activeIndex];

  useEffect(() => {
    if (!preview || preview.ai_ready) {
      return;
    }

    const cachedPreview = aiCacheRef.current[preview.tanggal_lengkap];

    if (cachedPreview) {
      setCalendarData((current) =>
        current.map((item) =>
          item.tanggal_lengkap === preview.tanggal_lengkap
            ? cachedPreview
            : item
        )
      );
      return;
    }

    let cancelled = false;

    async function loadPreviewAi() {
      setLoadingAi(true);

      try {
        const response = await generatePrintAi(preview.tanggal_lengkap);
        const enrichedPreview = {
          ...preview,
          ...response.data,
          ai_ready: true,
        };
        aiCacheRef.current[preview.tanggal_lengkap] = enrichedPreview;

        if (!cancelled) {
          setCalendarData((current) =>
            current.map((item) =>
              item.tanggal_lengkap === preview.tanggal_lengkap
                ? enrichedPreview
                : item
            )
          );
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              err.message ||
              "Ringkasan AI kalender gagal dibuat."
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingAi(false);
        }
      }
    }

    loadPreviewAi();

    return () => {
      cancelled = true;
    };
  }, [preview]);

  async function handleGenerate(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await generateCalendar(startDate, endDate);
      setCalendarData(response.data || []);
      setActiveIndex(0);
      aiCacheRef.current = {};

      if (!response.data?.length) {
        setError("Data kalender untuk rentang tanggal tersebut tidak ditemukan.");
      }
    } catch (err) {
      setCalendarData([]);
      setActiveIndex(0);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Tidak dapat terhubung ke backend."
      );
    } finally {
      setLoading(false);
    }
  }

  function showPrevious() {
    setActiveIndex((index) => Math.max(0, index - 1));
  }

  function showNext() {
    setActiveIndex((index) => Math.min(calendarData.length - 1, index + 1));
  }

  function printCalendar() {
    window.print();
  }

  async function renderCalendarImage() {
    return toPng(calendarRef.current, {
      backgroundColor: "#fffdfb",
      cacheBust: true,
      pixelRatio: 3,
    });
  }

  async function downloadPng() {
    if (!calendarRef.current || !preview) {
      return;
    }

    setDownloadingPng(true);
    setError("");

    try {
      const dataUrl = await renderCalendarImage();
      const link = document.createElement("a");
      link.download = `kalender-wariga-${preview.tanggal_lengkap}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      setError(err.message || "Gambar kalender gagal diunduh.");
    } finally {
      setDownloadingPng(false);
    }
  }

  async function downloadPdf() {
    if (!calendarRef.current || !preview) {
      return;
    }

    setDownloadingPdf(true);
    setError("");

    try {
      const { jsPDF } = await import("jspdf");
      const dataUrl = await renderCalendarImage();
      const image = new Image();
      image.src = dataUrl;
      await image.decode();

      const pdf = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4",
      });
      const margin = 8;
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const availableWidth = pageWidth - margin * 2;
      const availableHeight = pageHeight - margin * 2;
      const scale = Math.min(
        availableWidth / image.width,
        availableHeight / image.height
      );
      const imageWidth = image.width * scale;
      const imageHeight = image.height * scale;

      pdf.addImage(
        dataUrl,
        "PNG",
        (pageWidth - imageWidth) / 2,
        (pageHeight - imageHeight) / 2,
        imageWidth,
        imageHeight
      );
      pdf.save(`kalender-wariga-${preview.tanggal_lengkap}.pdf`);
    } catch (err) {
      setError(err.message || "PDF kalender gagal diunduh.");
    } finally {
      setDownloadingPdf(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(380px,1fr)] xl:gap-8">
        <section className="card p-4 sm:p-6 md:p-7">
          <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
                <h2 className="text-2xl font-bold sm:text-3xl">Preview Hasil</h2>
                <p className="text-sm text-gray-600 sm:text-base">
                  Tanggal {formatDate(startDate)} - {formatDate(endDate)}
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                className="rounded-xl border border-baliBorder px-4 py-2 disabled:opacity-40"
                type="button"
                onClick={showPrevious}
                disabled={!preview || activeIndex === 0}
              >
                ‹
              </button>
              <button
                className="rounded-xl border border-baliBorder px-4 py-2 disabled:opacity-40"
                type="button"
                onClick={showNext}
                disabled={!preview || activeIndex === calendarData.length - 1}
              >
                ›
              </button>
            </div>
          </div>

          <div className="rounded-2xl border border-baliBorder bg-[#fdfcfb] p-3 shadow-soft sm:p-5">
            {!preview ? (
              <div className="flex min-h-[450px] items-center justify-center text-sm text-gray-500">
                Pilih rentang tanggal, lalu klik Konfirmasi Tanggal untuk memuat
                preview dari backend.
              </div>
            ) : (
              <>
                {loadingAi && (
                  <div className="mb-3 rounded-xl bg-baliSoft p-3 text-center text-xs font-semibold text-baliBrown">
                    Menyusun ringkasan karakter dan baik-buruk hari dengan AI...
                  </div>
                )}
                <PrintableCalendar calendarRef={calendarRef} data={preview} />
              </>
            )}
          </div>
        </section>

        <div className="space-y-6">
          <section className="card p-5 sm:p-6 md:p-8">
            <h2 className="text-xl font-bold sm:text-2xl">Cetak Kalender</h2>
            <p className="mt-4 max-w-[760px] text-sm leading-7 text-gray-500">
              Pilih tanggal kalender. Sistem akan mengambil data Bali dan Wariga
              dari backend untuk ditampilkan sebagai pratinjau.
            </p>

            <form onSubmit={handleGenerate}>
              <div className="mt-8 grid grid-cols-1 gap-6 border-t border-baliBorder pt-8 md:grid-cols-2">
                <div>
                  <label className="mb-3 flex items-center gap-2 font-semibold">
                    <CalendarDays size={22} />
                    Pilih Tanggal Awal
                  </label>
                  <input
                    className="input"
                    type="date"
                    value={startDate}
                    onChange={(event) => setStartDate(event.target.value)}
                    required
                  />
                </div>

                <div>
                  <label className="mb-3 flex items-center gap-2 font-semibold">
                    <CalendarDays size={22} />
                    Pilih Tanggal Akhir
                  </label>
                  <input
                    className="input"
                    type="date"
                    value={endDate}
                    onChange={(event) => setEndDate(event.target.value)}
                    required
                  />
                </div>
              </div>

              {error && (
                <div className="mt-5 rounded-2xl bg-red-50 p-4 text-sm text-red-700">
                  {error}
                </div>
              )}

              <div className="mt-8 flex justify-end">
                <button
                  className="btn-primary flex w-full items-center justify-center gap-2 disabled:opacity-60 sm:w-auto"
                  type="submit"
                  disabled={loading}
                >
                  <CheckSquare size={18} />
                  {loading ? "Memuat..." : "Konfirmasi Tanggal"}
                </button>
              </div>
            </form>
          </section>

          <button
            className="btn-primary flex w-full items-center justify-center gap-2 disabled:opacity-60"
            type="button"
            onClick={printCalendar}
            disabled={!preview || loadingAi || !preview.ai_ready}
          >
            <Printer size={18} />
            Cetak Preview
          </button>

          <section className="card p-5 sm:p-6 md:p-8">
            <h2 className="text-xl font-bold sm:text-2xl">Unduh Hasil</h2>
            <div className="mt-8 space-y-6">
              <DownloadCard
                type="PDF"
                description="Unduh sebagai dokumen siap cetak yang rapi dan profesional."
                loading={downloadingPdf}
                disabled={!preview || loadingAi || !preview.ai_ready}
                onDownload={downloadPdf}
              />
              <DownloadCard
                type="PNG"
                description="Unduh sebagai gambar kalender beresolusi tinggi."
                disabled={!preview || loadingAi || !preview.ai_ready}
                loading={downloadingPng}
                onDownload={downloadPng}
              />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
