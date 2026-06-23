import { useEffect, useRef, useState } from "react";
import { CalendarDays, CheckSquare, CircleCheck, CircleX } from "lucide-react";
import { toPng } from "html-to-image";
import { createRoot } from "react-dom/client";
import { flushSync } from "react-dom";
import fixWebmDuration from "fix-webm-duration";
import DownloadCard from "../components/DownloadCard";
import { generateCalendar, generatePrintAi } from "../services/calendarApi";
import ornament from "../assets/ornamen.png";

const initialStartDate = "1900-01-01";
const initialEndDate = "1900-01-02";
const exportCalendarWidth = 680;
const videoCanvasWidth = 1080;
const videoFrameDuration = 3000;
const videoTransitionDuration = 600;
const videoFps = 24;

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

function buildPrintFallback(data) {
  const dayGuidance = splitValues(data.baik_buruk_hari, ";");

  return {
    ...data,
    hal_baik: dayGuidance.slice(0, 4),
    hal_dihindari: [],
    ai_ready: true,
    ai_fallback: true,
  };
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
  const [downloadingVideo, setDownloadingVideo] = useState(false);
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
        const fallbackPreview = buildPrintFallback(preview);
        aiCacheRef.current[preview.tanggal_lengkap] = fallbackPreview;

        if (!cancelled) {
          setCalendarData((current) =>
            current.map((item) =>
              item.tanggal_lengkap === preview.tanggal_lengkap
                ? fallbackPreview
                : item
            )
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

  async function waitForCalendarAssets(calendar) {
    await document.fonts?.ready;

    const images = Array.from(calendar?.querySelectorAll("img") || []);
    await Promise.all(
      images.map((image) => (
        image.complete
          ? Promise.resolve()
          : new Promise((resolve) => {
              image.addEventListener("load", resolve, { once: true });
              image.addEventListener("error", resolve, { once: true });
            })
      ))
    );
  }

  async function renderCalendarImage(calendar) {
    await waitForCalendarAssets(calendar);

    const previousStyle = calendar.getAttribute("style");
    calendar.classList.add("print-calendar-export");
    calendar.style.margin = "0";
    calendar.style.maxWidth = "none";
    calendar.style.width = `${exportCalendarWidth}px`;

    await new Promise((resolve) => requestAnimationFrame(resolve));

    try {
      const height = Math.ceil(calendar.scrollHeight);

      return await toPng(calendar, {
        backgroundColor: "#fffdfb",
        cacheBust: true,
        height,
        pixelRatio: 3,
        style: {
          height: `${height}px`,
          margin: "0",
          maxWidth: "none",
          width: `${exportCalendarWidth}px`,
        },
        width: exportCalendarWidth,
      });
    } finally {
      calendar.classList.remove("print-calendar-export");

      if (previousStyle === null) {
        calendar.removeAttribute("style");
      } else {
        calendar.setAttribute("style", previousStyle);
      }
    }
  }

  async function enrichCalendarRange() {
    const enrichedCalendars = [];

    for (const item of calendarData) {
      const cachedItem = aiCacheRef.current[item.tanggal_lengkap];

      if (cachedItem) {
        enrichedCalendars.push(cachedItem);
        continue;
      }

      if (item.ai_ready) {
        enrichedCalendars.push(item);
        continue;
      }

      let enrichedItem;

      try {
        const response = await generatePrintAi(item.tanggal_lengkap);
        enrichedItem = {
          ...item,
          ...response.data,
          ai_ready: true,
        };
      } catch (err) {
        enrichedItem = buildPrintFallback(item);
      }

      aiCacheRef.current[item.tanggal_lengkap] = enrichedItem;
      enrichedCalendars.push(enrichedItem);
    }

    setCalendarData(enrichedCalendars);
    return enrichedCalendars;
  }

  async function renderCalendarRange() {
    const enrichedCalendars = await enrichCalendarRange();
    const images = [];

    for (const item of enrichedCalendars) {
      const host = document.createElement("div");
      let calendarElement = null;
      const root = createRoot(host);

      host.className = "print-calendar-export-host";
      document.body.appendChild(host);

      try {
        flushSync(() => {
          root.render(
            <PrintableCalendar
              calendarRef={(element) => {
                calendarElement = element;
              }}
              data={item}
            />
          );
        });

        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));

        if (!calendarElement) {
          throw new Error(`Kalender ${item.tanggal_lengkap} gagal dirender untuk export.`);
        }

        images.push(await renderCalendarImage(calendarElement));
      } finally {
        root.unmount();
        host.remove();
      }
    }

    if (images.length !== enrichedCalendars.length) {
      throw new Error("Jumlah frame video tidak sesuai dengan rentang tanggal.");
    }

    return images;
  }

  function getExportFileName(extension) {
    return `kalender-wariga-${startDate}-sampai-${endDate}.${extension}`;
  }

  async function loadImageFromDataUrl(dataUrl) {
    const image = new Image();
    image.src = dataUrl;
    await image.decode();
    return image;
  }

  function getSupportedVideoType() {
    if (!window.MediaRecorder) {
      return null;
    }

    return [
      "video/webm;codecs=vp9",
      "video/webm;codecs=vp8",
      "video/webm",
      "video/mp4",
    ].find((type) => MediaRecorder.isTypeSupported(type));
  }

  async function createCalendarVideo(dataUrls) {
    const mimeType = getSupportedVideoType();

    if (!mimeType) {
      throw new Error("Browser ini belum mendukung pembuatan video kalender.");
    }

    const images = await Promise.all(dataUrls.map(loadImageFromDataUrl));

    if (!images.length) {
      throw new Error("Tidak ada frame kalender yang bisa dibuat menjadi video.");
    }

    const maxAspectRatio = Math.max(
      ...images.map((image) => image.naturalHeight / image.naturalWidth)
    );
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    canvas.width = videoCanvasWidth;
    canvas.height = Math.ceil(videoCanvasWidth * maxAspectRatio);

    const stream = canvas.captureStream(videoFps);
    const recorder = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond: 4_000_000,
    });
    const chunks = [];

    recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    });

    const stopped = new Promise((resolve, reject) => {
      recorder.addEventListener("stop", resolve, { once: true });
      recorder.addEventListener("error", () => {
        reject(new Error("Video kalender gagal diproses."));
      }, { once: true });
    });

    function drawImage(image, alpha = 1, clear = true) {
      const scale = Math.min(
        canvas.width / image.naturalWidth,
        canvas.height / image.naturalHeight
      );
      const width = image.naturalWidth * scale;
      const height = image.naturalHeight * scale;

      if (clear) {
        context.fillStyle = "#fffdfb";
        context.fillRect(0, 0, canvas.width, canvas.height);
      }

      context.globalAlpha = alpha;
      context.drawImage(
        image,
        (canvas.width - width) / 2,
        (canvas.height - height) / 2,
        width,
        height
      );
      context.globalAlpha = 1;
    }

    const totalDuration = images.length * videoFrameDuration;

    function drawTimelineFrame(elapsed) {
      const timelineElapsed = Math.min(elapsed, Math.max(0, totalDuration - 1));
      const imageIndex = Math.max(
        0,
        Math.min(
          images.length - 1,
          Math.floor(timelineElapsed / videoFrameDuration)
        )
      );
      const segmentElapsed = timelineElapsed - (imageIndex * videoFrameDuration);
      const currentImage = images[imageIndex];
      const nextImage = images[Math.min(images.length - 1, imageIndex + 1)];
      const transitionStart = videoFrameDuration - videoTransitionDuration;

      drawImage(currentImage);

      if (
        imageIndex < images.length - 1 &&
        segmentElapsed >= transitionStart
      ) {
        const transitionProgress = Math.min(
          1,
          (segmentElapsed - transitionStart) / videoTransitionDuration
        );

        drawImage(nextImage, transitionProgress, false);
      }
    }

    drawImage(images[0]);
    recorder.start();

    await new Promise((resolve) => {
      const timelineStartedAt = performance.now();
      const frameInterval = 1000 / videoFps;
      let lastDrawAt = 0;

      function drawFrame(now) {
        if (now - lastDrawAt < frameInterval) {
          requestAnimationFrame(drawFrame);
          return;
        }

        lastDrawAt = now;
        const elapsed = now - timelineStartedAt;
        drawTimelineFrame(elapsed);

        if (elapsed >= totalDuration) {
          drawImage(images[images.length - 1]);
          resolve();
          return;
        }

        requestAnimationFrame(drawFrame);
      }

      requestAnimationFrame(drawFrame);
    });

    recorder.stop();
    await stopped;
    stream.getTracks().forEach((track) => track.stop());

    const videoBlob = new Blob(chunks, { type: mimeType });

    if (mimeType.includes("webm")) {
      return fixWebmDuration(
        videoBlob,
        totalDuration,
        { logger: false }
      );
    }

    return videoBlob;
  }

  function downloadBlob(blob, fileName) {
    const link = document.createElement("a");
    const objectUrl = URL.createObjectURL(blob);

    link.download = fileName;
    link.href = objectUrl;
    link.click();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
  }

  async function downloadPng() {
    if (!calendarRef.current || !preview) {
      return;
    }

    setDownloadingPng(true);
    setError("");

    try {
      const dataUrls = await renderCalendarRange();
      dataUrls.forEach((dataUrl, index) => {
        const link = document.createElement("a");
        link.download = `kalender-wariga-${calendarData[index].tanggal_lengkap}.png`;
        link.href = dataUrl;
        link.click();
      });
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
      const dataUrls = await renderCalendarRange();
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
      for (const [index, dataUrl] of dataUrls.entries()) {
        const image = await loadImageFromDataUrl(dataUrl);

        if (index > 0) {
          pdf.addPage();
        }

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
      }

      pdf.save(getExportFileName("pdf"));
    } catch (err) {
      setError(err.message || "PDF kalender gagal diunduh.");
    } finally {
      setDownloadingPdf(false);
    }
  }

  async function downloadVideo() {
    if (!calendarRef.current || !preview) {
      return;
    }

    setDownloadingVideo(true);
    setError("");

    try {
      const dataUrls = await renderCalendarRange();
      const video = await createCalendarVideo(dataUrls);
      const extension = video.type.includes("mp4") ? "mp4" : "webm";

      downloadBlob(video, getExportFileName(extension));
    } catch (err) {
      setError(err.message || "Video kalender gagal diunduh.");
    } finally {
      setDownloadingVideo(false);
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

          <section className="card p-5 sm:p-6 md:p-8">
            <h2 className="text-xl font-bold sm:text-2xl">Unduh Hasil</h2>
            <div className="mt-8 space-y-6">
              <DownloadCard
                type="PDF"
                description="Unduh seluruh rentang tanggal, satu halaman untuk setiap hari."
                loading={downloadingPdf}
                disabled={!preview || loadingAi || !preview.ai_ready}
                onDownload={downloadPdf}
              />
              <DownloadCard
                type="PNG"
                description="Unduh setiap tanggal sebagai file PNG terpisah."
                disabled={!preview || loadingAi || !preview.ai_ready}
                loading={downloadingPng}
                onDownload={downloadPng}
              />
              <DownloadCard
                type="VIDEO"
                description="Unduh rentang tanggal sebagai video slideshow kalender."
                disabled={!preview || loadingAi || !preview.ai_ready}
                loading={downloadingVideo}
                onDownload={downloadVideo}
              />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
