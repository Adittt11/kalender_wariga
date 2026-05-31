import { Bot, Send } from "lucide-react";

export default function ChatWariga() {
  return (
    <section className="card p-5">
      <div className="mb-5 flex items-center gap-4">
        <div className="rounded-full bg-baliCream p-3 text-baliBrown">
          <Bot size={23} />
        </div>
        <h3 className="text-lg font-semibold">Tanya Wariga AI</h3>
        <p className="ml-auto max-w-[360px] text-sm leading-relaxed text-gray-500">
          Tanyakan tentang hari ini, watak kelahiran, baik buruk hari dan lainnya
        </p>
      </div>

      <div className="flex gap-3 rounded-2xl border border-baliBorder p-3">
        <input
          className="flex-1 px-2 text-sm outline-none"
          placeholder="Tulis pertanyaan Anda di sini..."
        />
        <button className="btn-primary flex items-center gap-2">
          <Send size={17} />
          Kirim
        </button>
      </div>
    </section>
  );
}
