import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  CalendarDays,
  Check,
  ChevronDown,
  CircleHelp,
  ListChecks,
  Search,
} from "lucide-react";

import { getDewasaAyuOptions, searchDewasaAyu } from "../services/dewasaAyuApi";

const months = [
  "Januari",
  "Februari",
  "Maret",
  "April",
  "Mei",
  "Juni",
  "Juli",
  "Agustus",
  "September",
  "Oktober",
  "November",
  "Desember",
];

const defaultResults = {
  ayu: [],
  dipakai: [],
  ala: [],
};

function formatDate(value) {
  if (!value) {
    return "-";
  }

  const [year, month, day] = value.split("-");
  return `${day}-${month}-${year}`;
}

function getMonthName(value) {
  const monthIndex = Number(value?.split("-")[1]) - 1;
  return months[monthIndex] || months[0];
}

function getMonthNumber(monthName) {
  return months.indexOf(monthName) + 1;
}

function StepLabel({ number, text }) {
  return (
    <div className="dewasa-step-label">
      <span>{number}</span>
      <p>{text}</p>
    </div>
  );
}

function OptionPills({ options, value, onChange }) {
  return (
    <div className="dewasa-pill-group">
      {options.map((option) => (
        <button
          className={value === option ? "dewasa-pill dewasa-pill-active" : "dewasa-pill"}
          key={option}
          onClick={() => onChange(option)}
          type="button"
        >
          {option}
        </button>
      ))}
    </div>
  );
}

function SelectField({ icon, label, value, onChange, options }) {
  return (
    <label className="dewasa-select-field">
      <span>{icon}{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
      <ChevronDown size={16} />
    </label>
  );
}

function DateField({ max, min, value, onChange }) {
  return (
    <label className="dewasa-select-field">
      <span><CalendarDays size={15} />Tanggal</span>
      <input
        max={max}
        min={min}
        onChange={(event) => onChange(event.target.value)}
        type="date"
        value={value}
      />
    </label>
  );
}

function ResultColumn({ emptyText, tone, title, items }) {
  return (
    <section className={`dewasa-result-column dewasa-result-${tone}`}>
      <h3>{title}</h3>
      <div className="dewasa-result-list">
        {items.length ? (
          items.map((item, index) => (
            <article key={`${tone}-${item.date}-${index}`}>
              <p>
                <strong>{item.date}</strong>
                <span>{item.title}</span>
              </p>
              <small>{item.note}</small>
            </article>
          ))
        ) : (
          <p className="dewasa-empty-text">{emptyText}</p>
        )}
      </div>
    </section>
  );
}

export default function DewasaAyu() {
  const [options, setOptions] = useState({
    categories: [],
    ceremonies: [],
    ceremonies_by_category: {},
    date_range: { min: "", max: "" },
    years: [],
  });
  const [results, setResults] = useState(defaultResults);
  const [loadingData, setLoadingData] = useState(true);
  const [loadingResults, setLoadingResults] = useState(false);
  const [error, setError] = useState("");
  const [category, setCategory] = useState("Manusa Yadnya");
  const [ceremony, setCeremony] = useState("Pawiwahan");
  const [timeMode, setTimeMode] = useState("month");
  const [date, setDate] = useState("1900-01-01");
  const [month, setMonth] = useState("Januari");
  const [year, setYear] = useState("1900");
  const [submittedFilters, setSubmittedFilters] = useState({
    category: "Manusa Yadnya",
    ceremony: "Pawiwahan",
    date: "1900-01-01",
    month: "Januari",
    timeMode: "month",
    year: "1900",
  });

  async function loadResults(filters) {
    const response = await searchDewasaAyu({
      ...filters,
      monthNumber: getMonthNumber(filters.month),
    });

    setResults(response.data || defaultResults);
  }

  useEffect(() => {
    async function loadDewasaData() {
      try {
        setLoadingData(true);
        const response = await getDewasaAyuOptions();
        const optionData = response.data || {};
        const defaultCategory = optionData.categories?.includes("Manusa Yadnya")
          ? "Manusa Yadnya"
          : optionData.categories?.[0] || "Manusa Yadnya";
        const ceremoniesForCategory = optionData.ceremonies_by_category?.[defaultCategory] || [];
        const defaultCeremony = ceremoniesForCategory.includes("Pawiwahan")
          ? "Pawiwahan"
          : ceremoniesForCategory[0] || optionData.ceremonies?.[0] || "Pawiwahan";
        const defaultDate = optionData.date_range?.min || "1900-01-01";
        const defaultYear = optionData.years?.[0] || "1900";
        const defaultMonth = getMonthName(defaultDate);
        const initialFilters = {
          category: defaultCategory,
          ceremony: defaultCeremony,
          date: defaultDate,
          month: defaultMonth,
          timeMode: "month",
          year: defaultYear,
        };

        setOptions({
          categories: optionData.categories || [],
          ceremonies: optionData.ceremonies || [],
          ceremonies_by_category: optionData.ceremonies_by_category || {},
          date_range: optionData.date_range || { min: "", max: "" },
          years: optionData.years || [],
        });
        setCategory(defaultCategory);
        setCeremony(defaultCeremony);
        setDate(defaultDate);
        setYear(defaultYear);
        setMonth(defaultMonth);
        setSubmittedFilters(initialFilters);
        await loadResults(initialFilters);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
          err.message ||
          "Data Dewasa Ayu tidak dapat dimuat."
        );
      } finally {
        setLoadingData(false);
      }
    }

    loadDewasaData();
  }, []);

  const dateRange = options.date_range || { min: "", max: "" };

  const filteredCeremonyOptions = useMemo(() => {
    return options.ceremonies_by_category?.[category] || [];
  }, [category, options.ceremonies_by_category]);

  useEffect(() => {
    if (filteredCeremonyOptions.length && !filteredCeremonyOptions.includes(ceremony)) {
      setCeremony(filteredCeremonyOptions[0]);
    }
  }, [ceremony, filteredCeremonyOptions]);

  const resultTitle = useMemo(
    () => {
      if (submittedFilters.timeMode === "day") {
        return `Menampilkan Dewasa Upacara ${submittedFilters.ceremony} Tanggal ${formatDate(submittedFilters.date)}`;
      }

      return `Menampilkan Dewasa Upacara ${submittedFilters.ceremony} Bulan ${submittedFilters.month} Tahun ${submittedFilters.year}`;
    },
    [submittedFilters]
  );

  return (
    <div className="dewasa-page">
      <div className="dewasa-top-grid">
        <section className="dewasa-panel dewasa-filter-panel">
          <StepLabel number="1" text="Pilih Kategori / Jenis Yadnya" />
          <OptionPills
            options={options.categories.length ? options.categories : [category]}
            value={category}
            onChange={setCategory}
          />

          <StepLabel number="2" text="Pilih Jenis Upacara / Kegiatan" />
          <OptionPills
            options={filteredCeremonyOptions.length ? filteredCeremonyOptions : [ceremony]}
            value={ceremony}
            onChange={setCeremony}
          />

          <StepLabel number="3" text="Pilih Waktu" />
          <div className="dewasa-time-toggle" aria-label="Pilih waktu">
            <button
              className={timeMode === "day" ? "dewasa-toggle-active" : ""}
              onClick={() => setTimeMode("day")}
              type="button"
            >
              <CalendarDays size={15} />
              Per Hari
            </button>
            <button
              className={timeMode === "month" ? "dewasa-toggle-active" : ""}
              onClick={() => setTimeMode("month")}
              type="button"
            >
              <ListChecks size={15} />
              Per Bulan
            </button>
          </div>

          {timeMode === "day" ? (
            <div className="dewasa-select-row">
              <DateField
                max={dateRange.max}
                min={dateRange.min}
                value={date}
                onChange={setDate}
              />
            </div>
          ) : (
            <div className="dewasa-select-row">
              <SelectField
                icon={<CalendarDays size={15} />}
                label="Bulan"
                options={months}
                value={month}
                onChange={setMonth}
              />
              <SelectField
                icon={<CalendarDays size={15} />}
                label="Tahun"
                options={options.years.length ? options.years : ["1900"]}
                value={year}
                onChange={setYear}
              />
            </div>
          )}

          <button
            className="dewasa-submit-button"
            disabled={loadingData || loadingResults}
            onClick={async () => {
              const nextFilters = { category, ceremony, date, month, timeMode, year };
              setError("");
              setLoadingResults(true);

              try {
                await loadResults(nextFilters);
                setSubmittedFilters(nextFilters);
              } catch (err) {
                setError(
                  err.response?.data?.detail ||
                  err.message ||
                  "Data Dewasa Ayu tidak dapat dimuat."
                );
              } finally {
                setLoadingResults(false);
              }
            }}
            type="button"
          >
            <Search size={15} />
            {loadingData || loadingResults ? "Memuat Data" : "Tampilkan Hasil"}
            <ArrowRight size={15} />
          </button>
        </section>

        <aside className="dewasa-panel dewasa-guide-panel">
          <div className="dewasa-guide-heading">
            <div className="dewasa-guide-icon"><BookOpen size={19} /></div>
            <h2>Panduan Dewasa Ayu</h2>
          </div>
          <ul>
            <li><Check size={14} />Pilih Kategori Dahulu ....</li>
            <li><Check size={14} />Pilih jenis upacara / kegiatan ....</li>
            <li><Check size={14} />Pilih Waktu ....</li>
            <li><CircleHelp size={14} />Hasil ditampilkan yaitu dewasa berdasarkan</li>
          </ul>
        </aside>
      </div>

      <section className="dewasa-results-panel">
        {error ? (
          <p className="dewasa-load-state">{error}</p>
        ) : loadingData || loadingResults ? (
          <p className="dewasa-load-state">Memuat data Dewasa Ayu...</p>
        ) : (
          <>
            <h2>{resultTitle}</h2>
            <div className="dewasa-results-grid">
              <ResultColumn
                emptyText="Tidak ada dewasa baik untuk pilihan ini."
                tone="ayu"
                title="Dewasa Ayu"
                items={results.ayu}
              />
              <ResultColumn
                emptyText="Tidak ada dewasa ayu-ala untuk pilihan ini."
                tone="dipakai"
                title="Dewasa Ala - Ayu"
                items={results.dipakai}
              />
              <ResultColumn
                emptyText="Tidak ada dewasa ala untuk pilihan ini."
                tone="ala"
                title="Dewasa Ala"
                items={results.ala}
              />
            </div>
          </>
        )}
      </section>
    </div>
  );
}
