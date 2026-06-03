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

const categoryOptions = ["Dewa Yadnya", "Pitra Yadnya", "Manusa Yadnya"];
const ceremonyOptions = ["Pawiwahan", "Pitra Yadnya", "Manusa Yadnya"];
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

function getDayTitle(wewaran) {
  return [wewaran?.saptawara, wewaran?.pancawara].filter(Boolean).join(" ") || "-";
}

function getRuleNote(rule, ceremony) {
  if (rule.rule_text_id) {
    return rule.rule_text_id;
  }

  return `${rule.status || "Dewasa"} untuk ${ceremony}.`;
}

function getResultGroup(status) {
  if (status === "Baik") {
    return "ayu";
  }

  if (status === "Ala-Ayu") {
    return "dipakai";
  }

  return "ala";
}

function buildOptions(data) {
  const categories = new Set();
  const ceremonies = new Set();
  const years = new Set();

  data.forEach((day) => {
    if (day.tanggal) {
      years.add(day.tanggal.slice(0, 4));
    }

    day.dewasa?.forEach((item) => {
      if (item.jenis_yadnya) {
        categories.add(item.jenis_yadnya);
      }

      if (item.upacara) {
        ceremonies.add(item.upacara);
      }
    });
  });

  return {
    categories: [...categories].sort(),
    ceremonies: [...ceremonies].sort(),
    years: [...years].sort(),
  };
}

function filterDewasaResults(data, filters) {
  const grouped = {
    ayu: [],
    dipakai: [],
    ala: [],
  };
  const selectedMonth = String(months.indexOf(filters.month) + 1).padStart(2, "0");

  data.forEach((day) => {
    if (!day.tanggal?.startsWith(`${filters.year}-${selectedMonth}`)) {
      return;
    }

    day.dewasa?.forEach((item) => {
      if (item.jenis_yadnya !== filters.category || item.upacara !== filters.ceremony) {
        return;
      }

      item.rules_match?.forEach((rule) => {
        const group = getResultGroup(rule.status);
        grouped[group].push({
          date: formatDate(day.tanggal),
          title: rule.nama_entitas || getDayTitle(day.wewaran),
          note: getRuleNote(rule, item.upacara),
        });
      });
    });
  });

  return grouped;
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
  const [data, setData] = useState([]);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState("");
  const [category, setCategory] = useState("Manusa Yadnya");
  const [ceremony, setCeremony] = useState("Pawiwahan");
  const [timeMode, setTimeMode] = useState("month");
  const [month, setMonth] = useState("Januari");
  const [year, setYear] = useState("1900");
  const [submittedFilters, setSubmittedFilters] = useState({
    category: "Manusa Yadnya",
    ceremony: "Pawiwahan",
    month: "Januari",
    year: "1900",
  });

  useEffect(() => {
    async function loadDewasaData() {
      try {
        setLoadingData(true);
        const response = await fetch("/data/dewasa_hasil3.json");

        if (!response.ok) {
          throw new Error("Data Dewasa Ayu tidak dapat dimuat.");
        }

        const json = await response.json();
        const options = buildOptions(json);
        const defaultCategory = options.categories[0] || "Manusa Yadnya";
        const defaultCeremony = options.ceremonies.includes("Pawiwahan")
          ? "Pawiwahan"
          : options.ceremonies[0] || "Pawiwahan";
        const defaultYear = options.years[0] || "1900";
        const defaultMonth = getMonthName(json[0]?.tanggal);

        setData(json);
        setCategory(defaultCategory);
        setCeremony(defaultCeremony);
        setYear(defaultYear);
        setMonth(defaultMonth);
        setSubmittedFilters({
          category: defaultCategory,
          ceremony: defaultCeremony,
          month: defaultMonth,
          year: defaultYear,
        });
      } catch (err) {
        setError(err.message || "Data Dewasa Ayu tidak dapat dimuat.");
      } finally {
        setLoadingData(false);
      }
    }

    loadDewasaData();
  }, []);

  const options = useMemo(() => buildOptions(data), [data]);

  const filteredCeremonyOptions = useMemo(() => {
    const ceremonies = new Set();

    data.forEach((day) => {
      day.dewasa?.forEach((item) => {
        if (item.jenis_yadnya === category && item.upacara) {
          ceremonies.add(item.upacara);
        }
      });
    });

    return [...ceremonies].sort();
  }, [category, data]);

  useEffect(() => {
    if (filteredCeremonyOptions.length && !filteredCeremonyOptions.includes(ceremony)) {
      setCeremony(filteredCeremonyOptions[0]);
    }
  }, [ceremony, filteredCeremonyOptions]);

  const results = useMemo(
    () => filterDewasaResults(data, submittedFilters),
    [data, submittedFilters]
  );

  const resultTitle = useMemo(
    () => `Menampilkan Dewasa Upacara ${submittedFilters.ceremony} Bulan ${submittedFilters.month} Tahun ${submittedFilters.year}`,
    [submittedFilters]
  );

  return (
    <div className="dewasa-page">
      <div className="dewasa-top-grid">
        <section className="dewasa-panel dewasa-filter-panel">
          <StepLabel number="1" text="Pilih Kategori / Jenis Yadnya" />
          <OptionPills
            options={options.categories.length ? options.categories : categoryOptions}
            value={category}
            onChange={setCategory}
          />

          <StepLabel number="2" text="Pilih Jenis Upacara / Kegiatan" />
          <OptionPills
            options={filteredCeremonyOptions.length ? filteredCeremonyOptions : ceremonyOptions}
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

          <button
            className="dewasa-submit-button"
            disabled={loadingData}
            onClick={() => setSubmittedFilters({ category, ceremony, month, year })}
            type="button"
          >
            <Search size={15} />
            {loadingData ? "Memuat Data" : "Tampilkan Hasil"}
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
        ) : loadingData ? (
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
                title="Dewasa Dipakai (Ayu - Ala)"
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
