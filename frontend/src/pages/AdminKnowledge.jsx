import { useEffect, useState } from "react";
import {
  BookOpen,
  Database,
  Download,
  FileSpreadsheet,
  FileText,
  LogOut,
  Loader2,
  UploadCloud,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  getKnowledgeCategories,
  getKnowledgeDocuments,
  uploadKnowledge,
} from "../services/knowledgeApi";
import { clearAdminToken } from "../services/adminAuthApi";

const defaultCategories = [
  "Penglukatan",
  "Pembayuhan",
  "Tenung",
  "Permata",
  "Lontar",
  "Wariga",
  "Pengetahuan Lain",
];

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("id-ID", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function getFileIcon(fileType) {
  if (["xlsx", "xlsm", "xls"].includes(String(fileType).toLowerCase())) {
    return FileSpreadsheet;
  }

  return FileText;
}

function downloadKnowledgeTemplate() {
  const csv = [
    "category,title,content",
    "Penglukatan,,",
    "Pembayuhan,,",
    "Tenung,,",
    "Permata,,",
    "Lontar,,",
    "Wariga,,",
    "Pengetahuan Lain,,",
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  const objectUrl = URL.createObjectURL(blob);

  link.href = objectUrl;
  link.download = "template-upload-knowledge.csv";
  link.click();
  setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
}

export default function AdminKnowledge() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState(defaultCategories);
  const [category, setCategory] = useState(defaultCategories[0]);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function handleRequestError(err, fallbackMessage) {
    if (err.response?.status === 401) {
      clearAdminToken();
      navigate("/admin-login", { replace: true });
      return "Sesi admin berakhir. Silakan login kembali.";
    }

    return err.response?.data?.detail || err.message || fallbackMessage;
  }

  async function loadDocuments() {
    setLoadingDocuments(true);

    try {
      const response = await getKnowledgeDocuments();
      setDocuments(response.data || []);
    } catch (err) {
      setError(handleRequestError(err, "Daftar knowledge gagal dimuat."));
    } finally {
      setLoadingDocuments(false);
    }
  }

  useEffect(() => {
    async function loadInitialData() {
      try {
        const response = await getKnowledgeCategories();
        const loadedCategories = response.data?.length
          ? response.data
          : defaultCategories;

        setCategories(loadedCategories);
        setCategory(loadedCategories[0]);
      } catch {
        setCategories(defaultCategories);
      }

      await loadDocuments();
    }

    loadInitialData();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!file) {
      setError("Pilih file PDF, Excel, atau Text terlebih dahulu.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await uploadKnowledge({ category, title, file });
      const uploaded = response.data;

      setMessage(
        `Knowledge "${uploaded.title}" berhasil di-upload dan dibuat ${uploaded.chunk_count} embedding.`
      );
      setTitle("");
      setFile(null);
      event.target.reset();
      await loadDocuments();
    } catch (err) {
      setError(handleRequestError(err, "Knowledge gagal di-upload."));
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    clearAdminToken();
    navigate("/admin-login", { replace: true });
  }

  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <div className="mb-5 flex justify-end">
        <button
          className="flex items-center gap-2 rounded-xl border border-baliBorder bg-white px-4 py-2 text-sm font-semibold text-baliBrown transition hover:bg-baliSoft"
          type="button"
          onClick={handleLogout}
        >
          <LogOut size={17} />
          Logout Admin
        </button>
      </div>
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(360px,0.85fr)_minmax(0,1.15fr)]">
        <section className="card p-5 sm:p-6 md:p-8">
          <div className="flex items-start gap-4">
            <div className="rounded-2xl bg-baliCream p-3 text-baliBrown">
              <UploadCloud size={26} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-baliDark sm:text-2xl">
                Admin Upload Knowledge
              </h2>
              <p className="mt-2 text-sm leading-7 text-gray-500">
                Tambahkan pengetahuan baru agar bisa masuk database, dibuat
                embedding, lalu dipakai oleh Tanya Wariga AI.
              </p>
            </div>
          </div>

          <button
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl border border-baliBorder bg-white px-4 py-3 text-sm font-semibold text-baliBrown transition hover:bg-baliSoft"
            type="button"
            onClick={downloadKnowledgeTemplate}
          >
            <Download size={18} />
            Download Template CSV Kosong
          </button>

          <form className="mt-8 space-y-5 border-t border-baliBorder pt-7" onSubmit={handleSubmit}>
            <div>
              <label className="mb-3 flex items-center gap-2 font-semibold text-baliDark">
                <BookOpen size={20} />
                Kategori Pengetahuan
              </label>
              <select
                className="input"
                value={category}
                onChange={(event) => setCategory(event.target.value)}
              >
                {categories.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-3 block font-semibold text-baliDark">
                Judul Knowledge
              </label>
              <input
                className="input"
                placeholder="Contoh: Lontar Penglukatan Dasar"
                type="text"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
              />
            </div>

            <div>
              <label className="mb-3 block font-semibold text-baliDark">
                File Knowledge
              </label>
              <input
                accept=".pdf,.xlsx,.xlsm,.txt,.md,.csv"
                className="input file:mr-4 file:rounded-lg file:border-0 file:bg-baliCream file:px-4 file:py-2 file:text-sm file:font-semibold file:text-baliBrown"
                type="file"
                onChange={(event) => setFile(event.target.files?.[0] || null)}
                required
              />
              <p className="mt-2 text-xs leading-6 text-gray-500">
                Format yang didukung: PDF, Excel .xlsx/.xlsm, Text .txt/.md/.csv.
              </p>
            </div>

            {message && (
              <div className="rounded-2xl bg-green-50 p-4 text-sm text-green-700">
                {message}
              </div>
            )}

            {error && (
              <div className="rounded-2xl bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              className="btn-primary flex w-full items-center justify-center gap-2 disabled:opacity-60"
              type="submit"
              disabled={loading}
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Database size={18} />}
              {loading ? "Mengupload..." : "Upload Pengetahuan Baru"}
            </button>
          </form>
        </section>

        <section className="card p-5 sm:p-6 md:p-8">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-xl font-bold text-baliDark sm:text-2xl">
                Knowledge Database
              </h2>
              <p className="mt-2 text-sm text-gray-500">
                Dokumen yang sudah dipecah menjadi embedding dan siap ditanyakan ke AI.
              </p>
            </div>
            <div className="rounded-full bg-baliSoft px-4 py-2 text-sm font-semibold text-baliBrown">
              {documents.length} Dokumen
            </div>
          </div>

          <div className="mt-7 overflow-hidden rounded-2xl border border-baliBorder">
            {loadingDocuments ? (
              <div className="flex min-h-[320px] items-center justify-center gap-2 text-sm text-gray-500">
                <Loader2 className="animate-spin" size={18} />
                Memuat knowledge...
              </div>
            ) : documents.length ? (
              <div className="divide-y divide-baliBorder">
                {documents.map((document) => {
                  const Icon = getFileIcon(document.file_type);

                  return (
                    <article
                      className="grid gap-4 bg-white p-4 sm:grid-cols-[auto_minmax(0,1fr)_auto] sm:items-center"
                      key={document.id}
                    >
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-baliSoft text-baliBrown">
                        <Icon size={22} />
                      </div>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-semibold text-baliDark">
                            {document.title}
                          </h3>
                          <span className="rounded-full bg-baliCream px-3 py-1 text-xs font-semibold text-baliBrown">
                            {document.category}
                          </span>
                        </div>
                        <p className="mt-1 truncate text-sm text-gray-500">
                          {document.source_filename}
                        </p>
                        <p className="mt-1 text-xs text-gray-500">
                          {formatDate(document.created_at)}
                        </p>
                      </div>
                      <div className="rounded-xl border border-baliBorder px-3 py-2 text-center text-sm font-semibold text-baliBrown">
                        {document.chunk_count} embedding
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="flex min-h-[320px] items-center justify-center text-center text-sm leading-7 text-gray-500">
                Belum ada knowledge. Upload file pertama untuk mulai menambah
                pengetahuan AI.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
