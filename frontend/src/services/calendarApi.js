import api from "./api";

export async function getCalendarByMonth(year, month) {
  const response = await api.get(`/api/calendar/month/${year}/${month}`);
  return response.data;
}

export async function getCalendarByDate(date) {
  const response = await api.get(`/api/calendar/date/${date}`);
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
