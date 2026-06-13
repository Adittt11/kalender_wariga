import { useRef, useState } from "react";
import { toPng } from "html-to-image";
import {
  Download,
  FileText,
  HeartHandshake,
  Search,
  Sparkles,
  UserRound,
  UsersRound,
} from "lucide-react";
import { calculatePertemuanLanangIstri } from "../services/pertemuanApi";

const initialLanangDate = "1900-01-01";
const initialIstriDate = "1900-01-01";
const exportMatchWidth = 680;

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("id-ID", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function PersonSummary({ icon, title, data }) {
  const urip = data?.urip?.detail || {};

  return (
    <section className="rounded-2xl border border-baliBorder bg-white p-5 shadow-soft">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-baliCream text-baliBrown">
          {icon}
        </div>
        <div>
          <h2 className="font-bold text-baliDark">{title}</h2>
          <p className="text-xs text-gray-500">{formatDate(data?.tanggal_lahir)}</p>
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {[
          ["Wuku", data?.wuku],
          ["Saptawara", data?.saptawara, urip.saptawara],
          ["Sadwara", data?.sadwara, urip.sadwara],
          ["Pancawara", data?.pancawara, urip.pancawara],
        ].map(([label, value, valueUrip]) => (
          <div key={label} className="rounded-xl bg-baliSoft p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500">{label}</p>
            <p className="mt-1 text-sm font-bold text-baliBrown">
              {value || "-"}
              {typeof valueUrip === "number" ? ` (${valueUrip})` : ""}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-xl bg-[#6b391b] px-4 py-3 text-white">
        <p className="text-xs text-white/75">Total Urip {title}</p>
        <strong className="text-2xl">{data?.urip?.total ?? 0}</strong>
      </div>
    </section>
  );
}

function splitCalculation(value) {
  const [subtraction, division] = String(value || "").split("|").map((item) => item.trim());

  return {
    pengurangan: division ? subtraction : "-",
    pembagian: division || subtraction || "-",
  };
}

function PrintablePertemuan({ data, printRef }) {
  if (!data) {
    return null;
  }

  return (
    <article ref={printRef} className="print-match-plain">
      <div className="print-match-plain-sheet">
        <p className="print-match-plain-kicker">Tenung Rumah Tangga</p>
        <h1>Pertemuan Lanang Istri</h1>

        <div className="print-match-plain-couple">
          {[
            ["Lanang", data.lanang],
            ["Istri", data.istri],
          ].map(([title, person]) => {
            const urip = person.urip.detail;

            return (
              <section key={title}>
                <h2>{title}</h2>
                <strong>{formatDate(person.tanggal_lahir)}</strong>
                <div>
                  <span>Wuku</span><b>{person.wuku}</b>
                  <span>Saptawara</span><b>{person.saptawara} ({urip.saptawara})</b>
                  <span>Sadwara</span><b>{person.sadwara} ({urip.sadwara})</b>
                  <span>Pancawara</span><b>{person.pancawara} ({urip.pancawara})</b>
                </div>
                <p>Total Urip: {person.urip.total}</p>
              </section>
            );
          })}
        </div>

        <div className="print-match-total">
          <span>Total Urip Pasangan</span>
          <strong>{data.total_urip}</strong>
        </div>

        <table className="print-match-table">
          <thead>
            <tr>
              <th>Umur Pernikahan</th>
              <th>Pengurangan Urip</th>
              <th>Pembagian Urip : 5</th>
              <th>Sisa</th>
              <th>Posisi</th>
              <th>Artinya</th>
            </tr>
          </thead>
          <tbody>
            {data.hasil.map((row) => {
              const calculation = splitCalculation(row.perhitungan);

              return (
                <tr key={row.umur_pernikahan}>
                  <td>{row.umur_pernikahan}</td>
                  <td>{calculation.pengurangan}</td>
                  <td>{calculation.pembagian}</td>
                  <td>{row.sisa}</td>
                  <td>{row.posisi}</td>
                  <td>{row.artinya}</td>
                </tr>
              );
            })}
          </tbody>
        </table>

        <section className="print-match-note">
          <h2>Dasar Perhitungan</h2>
          <p>
            Total urip pasangan dihitung dari urip Saptawara, Sadwara, dan
            Pancawara lanang ditambah urip Saptawara, Sadwara, dan Pancawara
            istri. Nilai tersebut dibagi 5 pada setiap periode pernikahan, lalu
            hasil bagi dipakai untuk menghitung ulang periode berikutnya.
          </p>
        </section>
      </div>
    </article>
  );
}

export default function PertemuanLanangIstri() {
  const [tanggalLanang, setTanggalLanang] = useState(initialLanangDate);
  const [tanggalIstri, setTanggalIstri] = useState(initialIstriDate);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [error, setError] = useState("");
  const printRef = useRef(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await calculatePertemuanLanangIstri(tanggalLanang, tanggalIstri);
      setResult(response.data);
    } catch (err) {
      setResult(null);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Tidak dapat menghitung pertemuan lanang istri."
      );
    } finally {
      setLoading(false);
    }
  }

  async function waitForPrintAssets(printElement) {
    await document.fonts?.ready;

    const images = Array.from(printElement?.querySelectorAll("img") || []);
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

  async function renderPrintImage(printElement) {
    await waitForPrintAssets(printElement);

    const previousStyle = printElement.getAttribute("style");
    printElement.classList.add("print-match-plain-export");
    printElement.style.margin = "0";
    printElement.style.maxWidth = "none";
    printElement.style.width = `${exportMatchWidth}px`;

    await new Promise((resolve) => requestAnimationFrame(resolve));

    try {
      const height = Math.ceil(printElement.scrollHeight);

      return await toPng(printElement, {
        backgroundColor: "#fffdfb",
        cacheBust: true,
        height,
        pixelRatio: 3,
        style: {
          height: `${height}px`,
          margin: "0",
          maxWidth: "none",
          width: `${exportMatchWidth}px`,
        },
        width: exportMatchWidth,
      });
    } finally {
      printElement.classList.remove("print-match-plain-export");

      if (previousStyle === null) {
        printElement.removeAttribute("style");
      } else {
        printElement.setAttribute("style", previousStyle);
      }
    }
  }

  async function loadImageFromDataUrl(dataUrl) {
    const image = new Image();
    image.src = dataUrl;
    await image.decode();
    return image;
  }

  async function downloadPdf() {
    if (!printRef.current || !result) {
      return;
    }

    setDownloadingPdf(true);
    setError("");

    try {
      const { jsPDF } = await import("jspdf");
      const dataUrl = await renderPrintImage(printRef.current);
      const image = await loadImageFromDataUrl(dataUrl);
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
      pdf.save(`pertemuan-lanang-istri-${tanggalLanang}-${tanggalIstri}.pdf`);
    } catch (err) {
      setError(err.message || "PDF Pertemuan Lanang Istri gagal diunduh.");
    } finally {
      setDownloadingPdf(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <section className="overflow-hidden rounded-3xl bg-gradient-to-br from-[#4d2a19] to-[#8A5838] p-6 text-white shadow-soft sm:p-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
          <div className="max-w-2xl">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15">
              <HeartHandshake size={26} />
            </div>
            <h1 className="mt-5 text-2xl font-bold sm:text-3xl">
              Pertemuan Lanang Istri
            </h1>
            <p className="mt-3 text-sm leading-7 text-white/80 sm:text-base">
              Hitung tenung perjalanan rumah tangga berdasarkan urip Saptawara,
              Sadwara, dan Pancawara dari tanggal lahir pasangan.
            </p>
          </div>

          <form
            className="grid w-full gap-3 rounded-2xl bg-white/10 p-4 backdrop-blur-sm sm:grid-cols-[1fr_1fr_auto] xl:max-w-3xl"
            onSubmit={handleSubmit}
          >
            <div>
              <p className="mb-2 flex items-center gap-2 text-xs font-bold text-white/90">
                <UserRound size={15} />
                Laki-laki
              </p>
              <label className="flex items-center rounded-xl bg-white px-4 text-baliDark">
                <span className="sr-only">Tanggal lahir laki-laki</span>
                <input
                  className="w-full bg-transparent py-3 text-sm outline-none"
                  onChange={(event) => setTanggalLanang(event.target.value)}
                  required
                  type="date"
                  value={tanggalLanang}
                />
              </label>
            </div>

            <div>
              <p className="mb-2 flex items-center gap-2 text-xs font-bold text-white/90">
                <UsersRound size={15} />
                Perempuan
              </p>
              <label className="flex items-center rounded-xl bg-white px-4 text-baliDark">
                <span className="sr-only">Tanggal lahir perempuan</span>
                <input
                  className="w-full bg-transparent py-3 text-sm outline-none"
                  onChange={(event) => setTanggalIstri(event.target.value)}
                  required
                  type="date"
                  value={tanggalIstri}
                />
              </label>
            </div>

            <button
              className="flex h-[46px] min-w-[118px] items-center justify-center gap-2 self-end justify-self-start rounded-xl bg-white px-4 text-sm font-semibold text-baliBrown transition hover:bg-baliSoft disabled:opacity-60"
              disabled={loading}
              type="submit"
            >
              <Search size={18} />
              {loading ? "Menghitung..." : "Hitung"}
            </button>
          </form>
        </div>
      </section>

      {error && (
        <div className="mt-6 rounded-2xl bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {!result && !error && (
        <section className="mt-6 rounded-3xl border border-baliBorder bg-white p-8 text-center shadow-soft">
          <Sparkles className="mx-auto text-baliBrown" size={28} />
          <p className="mt-4 text-sm leading-7 text-gray-500">
            Masukkan tanggal lahir lanang dan istri untuk menampilkan hasil
            pertemuan dalam tabel siklus lima tahunan.
          </p>
        </section>
      )}

      {result && (
        <div className="mt-6 space-y-6">
          <div className="grid gap-5 lg:grid-cols-2">
            <PersonSummary
              data={result.lanang}
              icon={<UserRound size={22} />}
              title="Lanang"
            />
            <PersonSummary
              data={result.istri}
              icon={<UsersRound size={22} />}
              title="Istri"
            />
          </div>

          <section className="rounded-3xl border border-baliBorder bg-white p-5 shadow-soft sm:p-7">
            <div className="flex flex-col gap-4 border-b border-baliBorder pb-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-baliBrown">
                  Hasil Urip Pasangan
                </p>
                <h2 className="mt-1 text-2xl font-bold text-baliDark">
                  Total Urip {result.total_urip}
                </h2>
              </div>

              <button
                className="flex items-center justify-center gap-2 rounded-xl bg-baliBrown px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#442313] disabled:opacity-60"
                disabled={downloadingPdf}
                onClick={downloadPdf}
                type="button"
              >
                <Download size={18} />
                {downloadingPdf ? "Menyiapkan PDF..." : "Export PDF"}
              </button>
            </div>

            <div className="mt-5 overflow-x-auto">
              <table className="pertemuan-result-table w-full min-w-[760px] border-collapse text-left text-sm">
                <thead>
                  <tr className="bg-baliSoft text-baliDark">
                    <th className="border border-baliBorder px-4 py-3">Umur Pernikahan</th>
                    <th className="border border-baliBorder px-4 py-3">Pengurangan Urip</th>
                    <th className="border border-baliBorder px-4 py-3">Pembagian Urip : 5</th>
                    <th className="border border-baliBorder px-4 py-3 text-center">Sisa</th>
                    <th className="border border-baliBorder px-4 py-3">Posisi</th>
                    <th className="border border-baliBorder px-4 py-3">Artinya</th>
                  </tr>
                </thead>
                <tbody>
                  {result.hasil.map((row) => {
                    const calculation = splitCalculation(row.perhitungan);

                    return (
                      <tr key={row.umur_pernikahan} className="odd:bg-white even:bg-[#fffaf4]">
                        <td className="border border-baliBorder px-4 py-3 font-semibold text-baliDark">
                          {row.umur_pernikahan}
                        </td>
                        <td className="border border-baliBorder px-4 py-3 text-gray-600">
                          {calculation.pengurangan}
                        </td>
                        <td className="border border-baliBorder px-4 py-3 text-gray-600">
                          {calculation.pembagian}
                        </td>
                        <td className="border border-baliBorder px-4 py-3 text-center font-bold text-baliBrown">
                          {row.sisa}
                        </td>
                        <td className="border border-baliBorder px-4 py-3 font-bold text-baliBrown">
                          {row.posisi}
                        </td>
                        <td className="border border-baliBorder px-4 py-3 text-gray-600">
                          {row.artinya}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-3xl border border-baliBorder bg-white p-5 shadow-soft sm:p-7">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-baliCream text-baliBrown">
                <FileText size={20} />
              </div>
              <h2 className="text-lg font-bold text-baliDark">Dasar Perhitungan</h2>
            </div>
            <p className="mt-4 text-sm leading-7 text-gray-600">
              Total urip pasangan dihitung dari urip Saptawara, Sadwara, dan
              Pancawara lanang ditambah urip Saptawara, Sadwara, dan Pancawara
              istri. Nilai tersebut dibagi 5 pada setiap periode pernikahan,
              lalu hasil bagi dipakai untuk menghitung ulang periode berikutnya.
            </p>
          </section>
        </div>
      )}

      {result && (
        <div className="print-match-export-host" aria-hidden="true">
          <PrintablePertemuan data={result} printRef={printRef} />
        </div>
      )}
    </div>
  );
}
