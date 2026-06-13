import api from "./api";

export async function calculatePertemuanLanangIstri(tanggalLanang, tanggalIstri) {
  const response = await api.post("/api/pertemuan/lanang-istri", {
    tanggal_lanang: tanggalLanang,
    tanggal_istri: tanggalIstri,
  });

  return response.data;
}
