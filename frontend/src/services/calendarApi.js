import api from "./api";

export async function getCalendarByMonth(year, month) {
  const response = await api.get(`/api/calendar/month/${year}/${month}`);
  return response.data;
}

export async function getCalendarByDate(date, aspects = "") {
  const url = aspects ? `/api/calendar/date/${date}?aspects=${aspects}` : `/api/calendar/date/${date}`;
  const response = await api.get(url);
  return response.data;
}

export async function generateCharacterAi(date, aspects = "") {
  const url = aspects ? `/api/calendar/date/${date}/character-ai?aspects=${aspects}` : `/api/calendar/date/${date}/character-ai`;
  const response = await api.post(url);
  return response.data;
}

export async function generatePrintAi(date, aspects = "") {
  const url = aspects ? `/api/calendar/date/${date}/print-ai?aspects=${aspects}` : `/api/calendar/date/${date}/print-ai`;
  const response = await api.post(url);
  return response.data;
}

export async function generateCalendar(startDate, endDate) {
  const response = await api.post("/api/generate/kalender", {
    start_date: startDate,
    end_date: endDate,
  });
  return response.data;
}

export async function getDashboardCalendarByMonth(year, month) {
  const response = await api.get(`/api/dashboard/month/${year}/${month}`);
  return response.data;
}

export async function getDashboardCalendarByDate(date) {
  const response = await api.get(`/api/dashboard/date/${date}`);
  return response.data;
}
