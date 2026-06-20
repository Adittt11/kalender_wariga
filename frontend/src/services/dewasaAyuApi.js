import api from "./api";

export async function getDewasaAyuOptions() {
  const response = await api.get("/api/dewasa-ayu/options");
  return response.data;
}

export async function searchDewasaAyu(filters) {
  const params = {
    jenis_yadnya: filters.category,
    upacara: filters.ceremony,
  };

  if (filters.timeMode === "day") {
    params.tanggal = filters.date;
  } else {
    params.bulan = filters.monthNumber;
    params.tahun = filters.year;
  }

  const response = await api.get("/api/dewasa-ayu/search", { params });
  return response.data;
}
