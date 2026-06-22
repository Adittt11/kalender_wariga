import { useEffect, useRef, useState } from "react";
import { Bot, Send, Trash2, UserRound } from "lucide-react";
import { sendChatMessages } from "../services/chatApi";

const initialMessages = [
  {
    role: "assistant",
    content:
      "Om swastyastu. Silakan tanyakan hal seputar kalender Bali, Wariga, wewaran, dewasa ayu, pakakalan, atau knowledge yang sudah di-upload admin seperti Penglukatan, Pembayuhan, Tenung, Permata, dan Lontar. Untuk detail kalender dari database, sebutkan tanggal secara natural, misalnya 22 Juni 2026, besok, atau 22/06/2026.",
  },
];

const chatModelOptions = [
  {
    key: "groq",
    label: "Groq",
    helper: "Cepat",
  },
  {
    key: "gpt54_mini",
    label: "GPT 5.4 Mini",
    helper: "Ringan",
  },
  {
    key: "gpt_latest",
    label: "GPT 5.5",
    helper: "Terbaru",
  },
];

export default function ChatWariga() {
  const [messages, setMessages] = useState(initialMessages);
  const [question, setQuestion] = useState("");
  const [selectedModel, setSelectedModel] = useState("gpt54_mini");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [loading, messages]);

  async function handleSubmit(event) {
    event.preventDefault();

    const content = question.trim();
    if (!content || loading) {
      return;
    }

    const userMessage = { role: "user", content };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const response = await sendChatMessages(nextMessages, selectedModel);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.data.answer },
      ]);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Tanya Wariga AI sedang tidak dapat dihubungi."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card overflow-hidden">
      <div className="flex items-center justify-between gap-4 border-b border-baliBorder p-5">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-baliCream p-3 text-baliBrown">
            <Bot size={22} />
          </div>
          <div>
            <h2 className="font-semibold text-baliDark">Asisten Wariga</h2>
            <p className="mt-1 text-xs text-gray-500">
              Model aktif: {chatModelOptions.find((item) => item.key === selectedModel)?.label}
            </p>
          </div>
        </div>
        <button
          className="calendar-nav-button"
          type="button"
          onClick={() => {
            setMessages(initialMessages);
            setError("");
          }}
          title="Bersihkan percakapan"
        >
          <Trash2 size={17} />
        </button>
      </div>

      <div className="border-b border-baliBorder bg-white px-4 py-3 sm:px-5">
        <div className="grid grid-cols-3 gap-2 rounded-2xl bg-baliSoft p-1">
          {chatModelOptions.map((option) => (
            <button
              className={`rounded-xl px-2 py-2 text-center text-xs font-semibold transition sm:text-sm ${
                selectedModel === option.key
                  ? "bg-white text-baliBrown shadow-sm"
                  : "text-gray-500 hover:bg-white/70 hover:text-baliDark"
              }`}
              disabled={loading}
              key={option.key}
              onClick={() => setSelectedModel(option.key)}
              type="button"
            >
              <span className="block truncate">{option.label}</span>
              <span className="block truncate text-[11px] font-medium opacity-75">
                {option.helper}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="h-[480px] space-y-4 overflow-y-auto bg-baliSoft/40 p-4 sm:p-6">
        {messages.map((message, index) => {
          const assistant = message.role === "assistant";

          return (
            <div
              key={`${message.role}-${index}`}
              className={`flex items-end gap-2 ${assistant ? "" : "justify-end"}`}
            >
              {assistant && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-baliCream text-baliBrown">
                  <Bot size={16} />
                </div>
              )}
              <div
                className={`max-w-[84%] whitespace-pre-line rounded-2xl px-4 py-3 text-sm leading-7 ${
                  assistant
                    ? "rounded-bl-md border border-baliBorder bg-white text-gray-700"
                    : "rounded-br-md bg-baliBrown text-white"
                }`}
              >
                {message.content}
              </div>
              {!assistant && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-baliBrown text-white">
                  <UserRound size={16} />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex items-end gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-baliCream text-baliBrown">
              <Bot size={16} />
            </div>
            <div className="rounded-2xl rounded-bl-md border border-baliBorder bg-white px-4 py-3 text-sm text-gray-500">
              Sedang menyusun jawaban...
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <form className="border-t border-baliBorder bg-white p-4 sm:p-5" onSubmit={handleSubmit}>
        {error && (
          <div className="mb-3 rounded-xl bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}
        <div className="flex gap-3">
          <textarea
            className="min-h-[48px] flex-1 resize-none rounded-2xl border border-baliBorder bg-white px-4 py-3 text-sm outline-none focus:border-baliBrown"
            placeholder="Contoh: Apa informasi Wariga pada 1 Januari 1900?"
            rows="1"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form.requestSubmit();
              }
            }}
          />
          <button
            className="btn-primary flex h-12 w-12 shrink-0 items-center justify-center p-0 disabled:opacity-60"
            type="submit"
            disabled={loading || !question.trim()}
            aria-label="Kirim pesan"
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </section>
  );
}
