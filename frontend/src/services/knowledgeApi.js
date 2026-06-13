import api from "./api";
import { getAdminAuthHeaders } from "./adminAuthApi";

export async function getKnowledgeCategories() {
  const response = await api.get("/api/knowledge/categories", {
    headers: getAdminAuthHeaders(),
  });
  return response.data;
}

export async function getKnowledgeDocuments() {
  const response = await api.get("/api/knowledge", {
    headers: getAdminAuthHeaders(),
  });
  return response.data;
}

export async function uploadKnowledge({ category, title, file }) {
  const formData = new FormData();

  formData.append("category", category);
  formData.append("title", title);
  formData.append("file", file);

  const response = await api.post("/api/knowledge", formData, {
    headers: {
      ...getAdminAuthHeaders(),
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}
