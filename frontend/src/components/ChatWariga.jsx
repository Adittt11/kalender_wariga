import { useEffect, useRef, useState } from "react";
import { Bot, MessageSquareText, Plus, Send, Trash2, UserRound } from "lucide-react";
import { sendChatMessages } from "../services/chatApi";

const chatHistoryStorageKey = "wariga-chat-history";

const initialMessages = [
  {
    role: "assistant",
    content:
      "Om Swastyastu. Silakan tanyakan hal seputar kalender Bali, Wariga, wewaran, dewasa ayu, pakakalan, karakter kelahiran dan pebayuhan",
  },
];

function createConversation() {
  const now = new Date().toISOString();

  return {
    id: `chat-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    title: "Percakapan Baru",
    messages: initialMessages,
    model: "gpt54_mini",
    createdAt: now,
    updatedAt: now,
  };
}

function buildConversationTitle(content) {
  const cleanContent = String(content || "").replace(/\s+/g, " ").trim();

  if (!cleanContent) {
    return "Percakapan Baru";
  }

  return cleanContent.length > 42 ? `${cleanContent.slice(0, 42)}...` : cleanContent;
}

function formatHistoryTime(value) {
  if (!value) {
    return "";
  }

  try {
    const date = new Date(value);
    if (isNaN(date.getTime())) {
      return "";
    }
    return new Intl.DateTimeFormat("id-ID", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  } catch {
    return "";
  }
}

function loadChatHistory() {
  try {
    const stored = JSON.parse(localStorage.getItem(chatHistoryStorageKey) || "null");

    if (stored?.conversations?.length) {
      return {
        conversations: stored.conversations,
        activeConversationId:
          stored.activeConversationId || stored.conversations[0].id,
      };
    }
  } catch {
    localStorage.removeItem(chatHistoryStorageKey);
  }

  const firstConversation = createConversation();

  return {
    conversations: [firstConversation],
    activeConversationId: firstConversation.id,
  };
}

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
  const [chatHistory, setChatHistory] = useState(loadChatHistory);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatEndRef = useRef(null);
  const activeConversation =
    chatHistory.conversations.find(
      (conversation) => conversation.id === chatHistory.activeConversationId
    ) || chatHistory.conversations[0];
  const messages = activeConversation?.messages || initialMessages;
  const selectedModel = activeConversation?.model || "gpt54_mini";

  useEffect(() => {
    localStorage.setItem(chatHistoryStorageKey, JSON.stringify(chatHistory));
  }, [chatHistory]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [loading, messages]);

  function updateConversation(conversationId, updater) {
    setChatHistory((current) => ({
      ...current,
      conversations: current.conversations.map((conversation) =>
        conversation.id === conversationId ? updater(conversation) : conversation
      ),
    }));
  }

  function updateActiveConversation(updater) {
    updateConversation(chatHistory.activeConversationId, updater);
  }

  function handleNewConversation() {
    const conversation = createConversation();

    setChatHistory((current) => ({
      conversations: [conversation, ...current.conversations],
      activeConversationId: conversation.id,
    }));
    setQuestion("");
    setError("");
  }

  function handleSelectConversation(conversationId) {
    if (loading) {
      return;
    }

    setChatHistory((current) => ({
      ...current,
      activeConversationId: conversationId,
    }));
    setQuestion("");
    setError("");
  }

  function handleDeleteConversation(conversationId) {
    if (loading) {
      return;
    }

    setChatHistory((current) => {
      const remainingConversations = current.conversations.filter(
        (conversation) => conversation.id !== conversationId
      );

      if (!remainingConversations.length) {
        const conversation = createConversation();

        return {
          conversations: [conversation],
          activeConversationId: conversation.id,
        };
      }

      return {
        conversations: remainingConversations,
        activeConversationId:
          current.activeConversationId === conversationId
            ? remainingConversations[0].id
            : current.activeConversationId,
      };
    });
    setQuestion("");
    setError("");
  }

  function handleClearCurrentConversation() {
    if (loading) {
      return;
    }

    updateActiveConversation((conversation) => ({
      ...conversation,
      title: "Percakapan Baru",
      messages: initialMessages,
      updatedAt: new Date().toISOString(),
    }));
    setQuestion("");
    setError("");
  }

  function handleModelChange(model) {
    updateActiveConversation((conversation) => ({
      ...conversation,
      model,
      updatedAt: new Date().toISOString(),
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const content = question.trim();
    if (!content || loading) {
      return;
    }

    const userMessage = { role: "user", content };
    const nextMessages = [...messages, userMessage];
    const targetConversationId = chatHistory.activeConversationId;
    const now = new Date().toISOString();

    updateConversation(targetConversationId, (conversation) => ({
      ...conversation,
      title:
        conversation.title === "Percakapan Baru"
          ? buildConversationTitle(content)
          : conversation.title,
      messages: nextMessages,
      updatedAt: now,
    }));
    setQuestion("");
    setError("");
    setLoading(true);

    try {
      // Hanya kirim 20 pesan terakhir ke backend agar tidak melampaui batasan validasi max_length=20
      const messagesToSend = nextMessages.slice(-20);
      const response = await sendChatMessages(messagesToSend, selectedModel);
      const answer = response?.data?.answer || response?.answer || "";

      if (!answer) {
        throw new Error("Respons AI tidak memiliki teks jawaban yang valid.");
      }

      updateConversation(targetConversationId, (conversation) => ({
        ...conversation,
        messages: [
          ...(conversation.messages || []),
          { role: "assistant", content: answer },
        ],
        updatedAt: new Date().toISOString(),
      }));
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
    <section className="card grid overflow-hidden lg:grid-cols-[280px_minmax(0,1fr)]">
      <aside className="border-b border-baliBorder bg-white lg:border-b-0 lg:border-r">
        <div className="flex h-[86px] items-center border-b border-baliBorder px-4">
          <button
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-baliBorder bg-baliSoft px-4 py-3 text-sm font-semibold text-baliBrown transition hover:bg-baliCream"
            type="button"
            onClick={handleNewConversation}
          >
            <Plus size={17} />
            Chat Baru
          </button>
        </div>

        <div className="max-h-[220px] space-y-2 overflow-y-auto p-3 lg:max-h-[680px]">
          {chatHistory.conversations.map((conversation) => {
            const active = conversation.id === chatHistory.activeConversationId;

            return (
              <div
                className={`group grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 rounded-xl border px-3 py-2 transition ${active
                    ? "border-baliBrown bg-baliCream"
                    : "border-transparent hover:border-baliBorder hover:bg-baliSoft"
                  }`}
                key={conversation.id}
              >
                <button
                  className="min-w-0 text-left"
                  disabled={loading && !active}
                  type="button"
                  onClick={() => handleSelectConversation(conversation.id)}
                >
                  <span className="flex min-w-0 items-center gap-2 text-sm font-semibold text-baliDark">
                    <MessageSquareText className="shrink-0 text-baliBrown" size={15} />
                    <span className="truncate">{conversation.title}</span>
                  </span>
                  <span className="mt-1 block truncate pl-6 text-xs text-gray-500">
                    {formatHistoryTime(conversation.updatedAt)}
                  </span>
                </button>
                <button
                  aria-label={`Hapus histori ${conversation.title}`}
                  className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 opacity-100 transition hover:bg-red-50 hover:text-red-600 lg:opacity-0 lg:group-hover:opacity-100"
                  disabled={loading}
                  title="Hapus histori"
                  type="button"
                  onClick={() => handleDeleteConversation(conversation.id)}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            );
          })}
        </div>
      </aside>

      <div className="min-w-0">
        <div className="flex h-[86px] items-center justify-between gap-4 border-b border-baliBorder px-5">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-baliCream p-3 text-baliBrown">
              <Bot size={22} />
            </div>
            <div>
              <h2 className="font-semibold text-baliDark">Asisten Wariga</h2>
              <p className="mt-1 text-xs text-gray-500">
                Model aktif: {chatModelOptions.find((item) => item.key === selectedModel)?.label || selectedModel}
              </p>
            </div>
          </div>
          <button
            className="calendar-nav-button"
            type="button"
            onClick={handleClearCurrentConversation}
            title="Bersihkan percakapan aktif"
          >
            <Trash2 size={17} />
          </button>
        </div>

        <div className="border-b border-baliBorder bg-white px-4 py-3 sm:px-5">
          <div className="grid grid-cols-3 gap-2 rounded-2xl bg-baliSoft p-1">
            {chatModelOptions.map((option) => (
              <button
                className={`rounded-xl px-2 py-2 text-center text-xs font-semibold transition sm:text-sm ${selectedModel === option.key
                    ? "bg-white text-baliBrown shadow-sm"
                    : "text-gray-500 hover:bg-white/70 hover:text-baliDark"
                  }`}
                disabled={loading}
                key={option.key}
                onClick={() => handleModelChange(option.key)}
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
                  className={`max-w-[84%] whitespace-pre-line rounded-2xl px-4 py-3 text-sm leading-7 ${assistant
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
      </div>
    </section>
  );
}
