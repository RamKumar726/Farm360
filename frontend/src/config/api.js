import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://farm360-backend-bmap.onrender.com";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Send httpOnly cookies on every request
  headers: { "Content-Type": "application/json" },
});

// Request interceptor — attach Bearer token from localStorage for cross-domain auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — auto-refresh on 401
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const original = error.config;
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
        localStorage.removeItem("access_token");
        if (window.location.pathname !== "/login" && window.location.pathname !== "/") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error.response?.data || error);
  }
);

export default api;

// Generic helper function for endpoint paths
export const apiFetch = async (url, options = {}) => {
  const method = (options.method || "GET").toLowerCase();
  const data = options.body ? JSON.parse(options.body) : undefined;
  if (method === "get") return api.get(url, { params: options.params });
  if (method === "post") return api.post(url, data);
  if (method === "patch") return api.patch(url, data);
  if (method === "put") return api.put(url, data);
  if (method === "delete") return api.delete(url);
  return api({ url, method, data });
};


// --- Typed API helpers ---

export const authAPI = {
  login: async (data) => {
    const res = await api.post("/auth/login", data);
    if (res?.success && res?.data?.access_token) {
      localStorage.setItem("access_token", res.data.access_token);
    }
    return res;
  },
  register: (data) => api.post("/auth/register", data),
  logout: async () => {
    try {
      await api.post("/auth/logout");
    } finally {
      localStorage.removeItem("access_token");
    }
  },
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
  createPublic: (data) => api.post("/leads/public", data),
  registerCustomer: (id, data) => api.post(`/leads/${id}/register-customer`, data),
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
  close: (id, completionNotes) => api.post(`/work-orders/${id}/close`, { completion_notes: completionNotes }),
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
  expressInterest: (data) => api.post("/investments/express-interest", data),
  approveInterest: (id) => api.post(`/investments/${id}/approve-interest`),
  updatePipeline: (id, verification_stage, agreement_url) => api.patch(`/investments/${id}/pipeline`, { verification_stage, agreement_url }),
  revenueShare: (id) => api.get(`/investments/${id}/revenue-share`),
  recordPayout: (id, data) => api.post(`/investments/${id}/payout`, data),
};

export const paymentsAPI = {
  list: () => api.get("/payments"),
  leadOrder: (id) => api.post(`/payments/leads/${id}/order`),
  investmentOrder: (id) => api.post(`/payments/investments/${id}/order`),
  confirm: (data) => api.post("/payments/confirm", data),
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
  linkAccount: (id, user_email) => api.patch(`/work-partners/${id}/account`, { user_email }),
  accept: (id, data) => api.post(`/work-partners/${id}/accept`, data),
  reject: (id, data) => api.post(`/work-partners/${id}/reject`, data),
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

export const issuesAPI = {
  list: (params) => api.get("/issues", { params }),
  get: (id) => api.get(`/issues/${id}`),
  create: (data) => api.post("/issues", data),
  update: (id, data) => api.patch(`/issues/${id}`, data),
  escalate: (id) => api.post(`/issues/${id}/escalate`),
  resolve: (id, notes) => api.post(`/issues/${id}/resolve?resolution_notes=${encodeURIComponent(notes)}`),
  delete: (id) => api.delete(`/issues/${id}`),
};

export const harvestsAPI = {
  list: (params) => api.get("/harvests", { params }),
  get: (id) => api.get(`/harvests/${id}`),
  create: (data) => api.post("/harvests", data),
  update: (id, data) => api.patch(`/harvests/${id}`, data),
  recordPayment: (id, data) => api.post(`/harvests/${id}/record-payment`, data),
};

export const projectFinanceAPI = {
  expenses: (projectId) => api.get(`/finance/projects/${projectId}/expenses`),
  createExpense: (data) => api.post("/finance/expenses", data),
  reviewExpense: (id, approved, note) => api.post(`/finance/expenses/${id}/review`, { approved, note }),
  markExpensePaid: (id, data) => api.post(`/finance/expenses/${id}/mark-paid`, data),
  settlements: (projectId) => api.get(`/finance/projects/${projectId}/settlements`),
  createSettlement: (projectId, data) => api.post(`/finance/projects/${projectId}/settlements`, data),
  approveSettlement: (id, approved) => api.post(`/finance/settlements/${id}/approve?approved=${approved}`),
  markSettlementPaid: (id, data) => api.post(`/finance/settlements/${id}/mark-paid`, data),
  outsourcingContracts: (projectId) => api.get(`/finance/projects/${projectId}/outsourcing-contracts`),
  createOutsourcingContract: (projectId, data) => api.post(`/finance/projects/${projectId}/outsourcing-contracts`, data),
};
