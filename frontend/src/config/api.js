import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Send httpOnly cookies on every request
  headers: { "Content-Type": "application/json" },
});

// Response interceptor — auto-refresh on 401
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const original = error.config;
    // Skip auto-refresh and redirect for auth endpoints to prevent reload loops
    const isAuthEndpoint =
      original?.url?.includes("/auth/login") ||
      original?.url?.includes("/auth/me") ||
      original?.url?.includes("/auth/refresh-token");

    if (error.response?.status === 401 && !original._retry && !isAuthEndpoint) {
      original._retry = true;
      try {
        await axios.post(`${API_BASE_URL}/auth/refresh-token`, {}, { withCredentials: true });
        return api(original);
      } catch {
        if (window.location.pathname !== "/login" && window.location.pathname !== "/") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error.response?.data || error);
  }
);

export default api;

// --- Typed API helpers ---

export const authAPI = {
  login: (data) => api.post("/auth/login", data),
  register: (data) => api.post("/auth/register", data),
  logout: () => api.post("/auth/logout"),
  me: () => api.get("/auth/me"),
};

export const usersAPI = {
  list: (params) => api.get("/users", { params }),
  get: (id) => api.get(`/users/${id}`),
  create: (data) => api.post("/users", data),
  update: (id, data) => api.patch(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
};

export const branchesAPI = {
  list: (params) => api.get("/branches", { params }),
  get: (id) => api.get(`/branches/${id}`),
  create: (data) => api.post("/branches", data),
  update: (id, data) => api.patch(`/branches/${id}`, data),
  delete: (id) => api.delete(`/branches/${id}`),
};

export const zonesAPI = {
  list: (params) => api.get("/zones", { params }),
  create: (data) => api.post("/zones", data),
  update: (id, data) => api.patch(`/zones/${id}`, data),
  delete: (id) => api.delete(`/zones/${id}`),
  assignEmployee: (id, employeeId) => api.post(`/zones/${id}/assign-employee`, { employee_id: employeeId }),
};

export const leadsAPI = {
  list: (params) => api.get("/leads", { params }),
  get: (id) => api.get(`/leads/${id}`),
  create: (data) => api.post("/leads", data),
  updateStatus: (id, data) => api.patch(`/leads/${id}/status`, data),
  getLost: (params) => api.get("/leads/lost", { params }),
  getWon: (params) => api.get("/leads/won", { params }),
};

export const workOrdersAPI = {
  list: (params) => api.get("/work-orders", { params }),
  get: (id) => api.get(`/work-orders/${id}`),
  create: (data) => api.post("/work-orders", data),
  assignPartner: (id, partnerId) => api.post(`/work-orders/${id}/assign-partner`, { partner_id: partnerId }),
  assignEmployee: (id, employeeId) => api.post(`/work-orders/${id}/assign-farm-employee`, { employee_id: employeeId }),
  verify: (id) => api.post(`/work-orders/${id}/verify`),
  updateStatus: (id, data) => api.patch(`/work-orders/${id}/status`, data),
};

export const visitsAPI = {
  list: (params) => api.get("/visits", { params }),
  get: (id) => api.get(`/visits/${id}`),
  create: (data) => api.post("/visits", data),
  submitProof: (id, data) => api.post(`/visits/${id}/submit-proof`, data),
  pending: () => api.get("/visits/pending"),
  failed: () => api.get("/visits/failed"),
};

export const farmsAPI = {
  list: (params) => api.get("/farms", { params }),
  get: (id) => api.get(`/farms/${id}`),
  create: (data) => api.post("/farms", data),
  cropHealth: (id) => api.get(`/farms/${id}/crop-health`),
  agreements: (id) => api.get(`/farms/${id}/agreements`),
  workOrders: (id) => api.get(`/farms/${id}/work-orders`),
};

export const agreementsAPI = {
  list: (params) => api.get("/agreements", { params }),
  get: (id) => api.get(`/agreements/${id}`),
  create: (data) => api.post("/agreements", data),
};

export const prescriptionsAPI = {
  list: (params) => api.get("/prescriptions", { params }),
  get: (id) => api.get(`/prescriptions/${id}`),
  create: (data) => api.post("/prescriptions", data),
  updateStatus: (id, status) => api.patch(`/prescriptions/${id}/status`, { status }),
};

export const cropDesignsAPI = {
  list: (params) => api.get("/crop-designs", { params }),
  get: (id) => api.get(`/crop-designs/${id}`),
  create: (data) => api.post("/crop-designs", data),
  approve: (id) => api.post(`/crop-designs/${id}/approve`),
  getCycles: (id) => api.get(`/crop-designs/${id}/generate-cycles`),
};

export const landSalesAPI = {
  list: (params) => api.get("/land-sales", { params }),
  get: (id) => api.get(`/land-sales/${id}`),
  create: (data) => api.post("/land-sales", data),
  postPublic: (id) => api.post(`/land-sales/${id}/post-public`),
  broadcast: (id) => api.post(`/land-sales/${id}/broadcast`),
  expressInterest: (id) => api.post(`/land-sales/${id}/interest`),
  updateStatus: (id, status) => api.patch(`/land-sales/${id}/status`, { status }),
};

export const investmentsAPI = {
  list: (params) => api.get("/investments", { params }),
  get: (id) => api.get(`/investments/${id}`),
  create: (data) => api.post("/investments", data),
  revenueShare: (id) => api.get(`/investments/${id}/revenue-share`),
};

export const projectsAPI = {
  list: (params) => api.get("/projects", { params }),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post("/projects", data),
  updateStatus: (id, data) => api.patch(`/projects/${id}/status`, data),
};

export const brokersAPI = {
  list: (params) => api.get("/brokers", { params }),
  create: (data) => api.post("/brokers", data),
  assignZone: (id, zoneId) => api.post(`/brokers/${id}/assign-zone`, { zone_id: zoneId }),
};

export const workPartnersAPI = {
  list: (params) => api.get("/work-partners", { params }),
  create: (data) => api.post("/work-partners", data),
  accept: (id) => api.post(`/work-partners/${id}/accept`),
  reject: (id) => api.post(`/work-partners/${id}/reject`),
  verify: (id, workOrderId, qualityGood) =>
    api.post(`/work-partners/${id}/verify?work_order_id=${workOrderId}&quality_good=${qualityGood}`),
  payment: (id, data) => api.post(`/work-partners/${id}/payment`, data),
};

export const notificationsAPI = {
  list: (params) => api.get("/notifications", { params }),
  sendWhatsapp: (data) => api.post("/notifications/send-whatsapp", data),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
};

export const attendanceAPI = {
  list: (params) => api.get("/attendance", { params }),
  create: (data) => api.post("/attendance", data),
  today: () => api.get("/attendance/today"),
  markAbsent: (userId, replacementId) =>
    api.post(`/attendance/mark-absent?user_id=${userId}${replacementId ? `&replacement_user_id=${replacementId}` : ""}`),
};

export const analyticsAPI = {
  leads: () => api.get("/analytics/leads"),
  revenue: () => api.get("/analytics/revenue"),
  visits: () => api.get("/analytics/visits"),
  employees: () => api.get("/analytics/employees"),
  investments: () => api.get("/analytics/investments"),
};
