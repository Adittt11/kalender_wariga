import { Download } from "lucide-react";

export default function DownloadCard({ type, description }) {
  return (
    <div className="flex items-center gap-5 rounded-2xl border border-baliBorder p-5">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-baliSoft text-4xl">
        {type === "PDF" ? "📄" : "🖼️"}
      </div>

      <div className="flex-1">
        <h4 className="text-lg font-semibold">Download {type}</h4>
        <p className="mt-1 text-sm leading-relaxed text-gray-500">{description}</p>
      </div>

      <div className="text-right text-gray-500">
        <Download className="ml-auto mb-2 text-baliBrown" size={22} />
        <p className="text-xs">5,6 MB</p>
      </div>
    </div>
  );
}
