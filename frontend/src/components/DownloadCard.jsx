import { Download } from "lucide-react";

const typeIcons = {
  PDF: "📄",
  PNG: "🖼️",
  VIDEO: "🎬",
};

export default function DownloadCard({
  type,
  description,
  disabled = false,
  loading = false,
  progress,
  onDownload,
}) {
  const showProgress = loading && progress;

  return (
    <button
      className="flex w-full items-center gap-5 rounded-2xl border border-baliBorder p-5 text-left transition hover:bg-baliSoft disabled:cursor-not-allowed disabled:opacity-50"
      type="button"
      disabled={disabled || loading}
      onClick={onDownload}
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-baliSoft text-4xl">
        {typeIcons[type] || "⬇️"}
      </div>

      <div className="flex-1">
        <h4 className="text-lg font-semibold">Download {type}</h4>
        <p className="mt-1 text-sm leading-relaxed text-gray-500">{description}</p>
        {showProgress && (
          <div className="mt-4">
            <div className="h-2 overflow-hidden rounded-full bg-baliSoft">
              <div
                className="h-full rounded-full bg-baliBrown transition-all duration-200"
                style={{ width: `${progress.percent}%` }}
              />
            </div>
            <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold text-baliBrown">
              <span>{progress.message}</span>
              <span>{progress.percent}% - {progress.elapsedSeconds} detik</span>
            </div>
          </div>
        )}
      </div>

      <div className="text-right text-gray-500">
        <Download className="ml-auto mb-2 text-baliBrown" size={22} />
        <p className="text-xs">{loading ? `${progress?.percent || 0}%` : "Unduh"}</p>
      </div>
    </button>
  );
}
