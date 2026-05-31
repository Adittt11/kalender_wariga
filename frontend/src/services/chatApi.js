import api from "./api";

export async function sendChatMessages(messages) {
  const response = await api.post("/api/chat", { messages });
  return response.data;
}
