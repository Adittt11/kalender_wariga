import api from "./api";

export function getPebayuhan(tanggal) {
    return api.get(`/api/pebayuhan/${tanggal}`);
}
