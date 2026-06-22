import api from "./api";

export async function sendChatMessages(messages, model = "gpt_latest") {
  const response = await api.post("/api/chat", { messages, model });
  return response.data;
}
