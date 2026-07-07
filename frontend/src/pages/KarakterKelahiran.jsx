import { useState } from "react";
import { CalendarDays, Search, Sparkles, UserRound } from "lucide-react";
import { generateCharacterAi, getCalendarByDate } from "../services/calendarApi";

const initialDate = "1900-01-01";

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

export default function KarakterKelahiran() {
  const [date, setDate] = useState(initialDate);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingAi, setLoadingAi] = useState(false);
  const [aiCharacter, setAiCharacter] = useState("");
  const [error, setError] = useState("");
  const [selectedAspects, setSelectedAspects] = useState({
    palalintangan: true,
    ekajalarsi: true,
    pararasan: true,
    pratiti_samutpada: true,
    wuku: true,
    pancawara: true,
    saptawara: true,
  });

  const handleAspectChange = (aspect) => {
    setSelectedAspects((prev) => {
      const nextState = {
        ...prev,
        [aspect]: !prev[aspect],
      };

      const activeAspects = Object.keys(nextState).filter((key) => nextState[key]);
      if (activeAspects.length === 0) {
        setError("Pilih aspek terlebih dahulu.");
        setResult(null);
        setAiCharacter("");
      } else {
        setError((prevError) => 
          prevError === "Pilih aspek terlebih dahulu." ? "" : prevError
        );
      }

      return nextState;
    });
  };

  async function handleSubmit(event) {
    event.preventDefault();

    const activeAspects = Object.keys(selectedAspects).filter((key) => selectedAspects[key]);
    if (activeAspects.length === 0) {
      setError("Pilih aspek terlebih dahulu.");
      setResult(null);
      setAiCharacter("");
      return;
    }

    setLoading(true);
    setError("");
    setAiCharacter("");
    const aspectsStr = activeAspects.join(",");

    try {
      setLoadingAi(true);
      const [calendarResponse, aiResponse] = await Promise.all([
        getCalendarByDate(date, aspectsStr),
        generateCharacterAi(date, aspectsStr),
      ]);
      setResult(calendarResponse.data);
      setAiCharacter(aiResponse.data.karakter_kelahiran_ai);
    } catch (err) {
      setResult(null);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Tidak dapat mengambil karakter kelahiran dari backend."
      );
    } finally {
      setLoading(false);
      setLoadingAi(false);
    }
  }

  const characterSources = result
    ? [
        selectedAspects.ekajalarsi && ["Ekajalarsi", result.ekajalarsi],
        selectedAspects.palalintangan && ["Palalintangan", result.palalintangan],
        selectedAspects.pararasan && ["Pararasan", result.pararasan],
        selectedAspects.pratiti_samutpada && ["Pratiti Samutpada", result.pratiti_samutpada],
        selectedAspects.wuku && ["Wuku", result.wuku],
        selectedAspects.pancawara && ["Pancawara", result.pancawara],
        selectedAspects.saptawara && ["Saptawara", result.saptawara],
      ].filter(Boolean)
    : [];

  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <section className="overflow-hidden rounded-3xl bg-gradient-to-br from-[#5A321D] to-[#8A5838] p-6 text-white shadow-soft sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15">
              <UserRound size={25} />
            </div>
            <h1 className="mt-5 text-2xl font-bold sm:text-3xl">Karakter Kelahiran</h1>
            <p className="mt-3 text-sm leading-7 text-white/80 sm:text-base">
              Pilih tanggal lahir dan centang aspek di bawah untuk melihat karakter berdasarkan kalender Bali.
            </p>
          </div>

          <form
            className="flex w-full flex-col gap-3 rounded-2xl bg-white/10 p-4 backdrop-blur-sm sm:flex-row lg:max-w-xl"
            onSubmit={handleSubmit}
          >
            <label className="flex flex-1 items-center gap-3 rounded-xl bg-white px-4 text-baliDark">
              <CalendarDays size={20} className="text-baliBrown" />
              <input
                className="w-full bg-transparent py-3 text-sm outline-none"
                type="date"
                value={date}
                onChange={(event) => setDate(event.target.value)}
                required
              />
            </label>
            <button
              className="flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-baliBrown transition hover:bg-baliSoft disabled:opacity-60"
              type="submit"
              disabled={loading}
            >
              <Search size={18} />
              {loading ? "Memuat..." : "Lihat Karakter"}
            </button>
          </form>
        </div>

        <div className="mt-6 border-t border-white/10 pt-4 text-center">
          <p className="text-xs font-semibold uppercase tracking-wider text-white/70">Filter Aspek Karakter:</p>
          <div className="mt-3 flex flex-wrap justify-center gap-2 text-xs">
            {Object.keys(selectedAspects).map((aspect) => (
              <label 
                key={aspect} 
                className={`flex items-center gap-2.5 cursor-pointer select-none px-3.5 py-2 rounded-xl transition-all duration-200 border ${
                  selectedAspects[aspect]
                    ? "bg-white/15 border-white/20 text-white shadow-sm"
                    : "bg-white/5 border-white/5 text-white/60 hover:bg-white/10 hover:text-white"
                }`}
              >
                <div className="relative flex items-center justify-center">
                  <input
                    type="checkbox"
                    checked={selectedAspects[aspect]}
                    onChange={() => handleAspectChange(aspect)}
                    className="sr-only"
                  />
                  <div className={`w-4 h-4 rounded flex items-center justify-center transition-all duration-200 ${
                    selectedAspects[aspect]
                      ? "bg-white text-[#8A5838]"
                      : "border border-white/35 bg-transparent text-transparent"
                  }`}>
                    <svg
                      className="w-3.5 h-3.5 stroke-[3.5]"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                </div>
                <span className="capitalize font-medium tracking-wide">
                  {aspect.replace("_", " ")}
                </span>
              </label>
            ))}
          </div>
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
            Masukkan tanggal lahir untuk menampilkan analisis karakter dari database.
          </p>
        </section>
      )}

      {result && (
        <div className="mt-6 space-y-6">
          <section className="rounded-3xl border border-baliBorder bg-white p-5 shadow-soft sm:p-7">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-baliBrown">
              Hasil Analisis
            </p>
            <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <h2 className="text-2xl font-bold text-baliDark">
                {formatDate(result.tanggal_lengkap)}
              </h2>
              <p className="text-sm text-gray-500">{result.saptawara} · {result.pancawara}</p>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {characterSources.map(([label, value]) => (
                <div key={label} className="rounded-2xl bg-baliSoft p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</p>
                  <p className="mt-2 font-semibold text-baliBrown">{value}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-baliBorder bg-white p-5 shadow-soft sm:p-7">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-baliCream text-baliBrown">
                <Sparkles size={20} />
              </div>
              <h2 className="text-xl font-bold text-baliDark">Makna Karakter Kelahiran</h2>
            </div>
            <p className="mt-5 whitespace-pre-line text-justify text-sm leading-8 text-gray-600">
              {loadingAi ? "Sedang menyusun makna karakter dengan AI..." : aiCharacter}
            </p>
          </section>
        </div>
      )}
    </div>
  );
}
