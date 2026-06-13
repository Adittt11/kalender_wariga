import api from "./api";

const adminTokenKey = "wariga-admin-token";

export function getAdminToken() {
  return localStorage.getItem(adminTokenKey);
}

export function setAdminToken(token) {
  localStorage.setItem(adminTokenKey, token);
}

export function clearAdminToken() {
  localStorage.removeItem(adminTokenKey);
}

export function isAdminLoggedIn() {
  return Boolean(getAdminToken());
}

export async function loginAdmin(username, password) {
  const response = await api.post("/api/admin/login", {
    username,
    password,
  });
  const token = response.data?.data?.token;

  if (token) {
    setAdminToken(token);
  }

  return response.data;
}

export function getAdminAuthHeaders() {
  const token = getAdminToken();

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}
