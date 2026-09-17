import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { Toaster } from "react-hot-toast";
import { Leaf } from "lucide-react";
import useAppStore from "./store/useAppStore";
import { authAPI } from "./config/api";
import { getDefaultRoute, canAccessPath } from "./config/roleRoutes";

// Public & Auth pages
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

// Founder portal
import FounderDashboard from "./portals/founder/Dashboard";
import FounderBranches from "./portals/founder/Branches";
import FounderZones from "./portals/founder/Zones";
import FounderEmployees from "./portals/founder/Employees";
import FounderLeads from "./portals/founder/Leads";
import FounderRevenue from "./portals/founder/Revenue";
import FounderProjects from "./portals/founder/Projects";
import FounderAnalytics from "./portals/founder/Analytics";
import FounderApprovals from "./portals/founder/Approvals";
import FounderRiskFraud from "./portals/founder/RiskFraud";

// Zone Admin portal
import ZoneAdminDashboard from "./portals/zone-admin/Dashboard";
import ZoneAdminLeads from "./portals/zone-admin/Leads";
import ZoneAdminEmployees from "./portals/zone-admin/Employees";
import ZoneAdminWorkManagement from "./portals/zone-admin/WorkManagement";
import ZoneAdminRevenue from "./portals/zone-admin/Revenue";
import ZoneAdminBrokers from "./portals/zone-admin/Brokers";
import ZoneAdminVisits from "./portals/zone-admin/Visits";
import ZoneAdminEscalations from "./portals/zone-admin/Escalations";

// Employee portal
import EmployeeDashboard from "./portals/employee/Dashboard";
import EmployeeLeadPipeline from "./portals/employee/LeadPipeline";
import EmployeeWorkQueue from "./portals/employee/WorkQueue";
import EmployeeLandLeads from "./portals/employee/LandLeads";
import EmployeeInvestmentLeads from "./portals/employee/InvestmentLeads";
import EmployeePartnerAssignment from "./portals/employee/PartnerAssignment";
import EmployeeFollowUp from "./portals/employee/FollowUp";

// Agri Officer portal
import AgriDashboard from "./portals/agri-officer/Dashboard";
import AgriAssignments from "./portals/agri-officer/Assignments";
import AgriPrescriptions from "./portals/agri-officer/Prescriptions";
import AgriCropDesign from "./portals/agri-officer/CropDesign";
import AgriFarmVisits from "./portals/agri-officer/FarmVisits";
import AgriQuotes from "./portals/agri-officer/Quotes";

// Farm Employee portal
import FarmEmpDashboard from "./portals/farm-employee/Dashboard";
import FarmEmpMyVisits from "./portals/farm-employee/MyVisits";
import FarmEmpSubmitProof from "./portals/farm-employee/SubmitProof";
import FarmEmpWorkMonitor from "./portals/farm-employee/WorkMonitor";
import FarmEmpHarvest from "./portals/farm-employee/Harvest";
import FarmEmpIncidentReport from "./portals/farm-employee/IncidentReport";

// Customer portal
import CustomerMarketplace from "./portals/customer/Marketplace";
import CustomerDashboard from "./portals/customer/Dashboard";
import CustomerMyFarm from "./portals/customer/MyFarm";
import CustomerAgreements from "./portals/customer/Agreements";
import CustomerWorkDetails from "./portals/customer/WorkDetails";
import CustomerCropHealth from "./portals/customer/CropHealth";
import CustomerInvestments from "./portals/customer/Investments";
import CustomerLandSale from "./portals/customer/LandSale";
import CustomerPayments from "./portals/customer/Payments";
import CustomerServices from "./portals/customer/CustomerServices";

function AuthGuard({ children }) {
  const { user, isAuthenticated } = useAppStore();
  const location = useLocation();
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />;
  if (!canAccessPath(user.role, location.pathname) && user.role !== "founder") {
    return <Navigate to={getDefaultRoute(user.role)} replace />;
  }
  return children;
}

function AppInitializer({ children }) {
  const { setUser, clearUser } = useAppStore();
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    authAPI
      .me()
      .then((res) => {
        if (res.success) setUser(res.data);
      })
      .catch(() => {
        clearUser();
      })
      .finally(() => {
        setAuthLoading(false);
      });
  }, []);

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0f1f19] flex flex-col items-center justify-center p-4 text-center">
        <div className="w-14 h-14 bg-[#c9a84c]/20 border border-[#c9a84c]/40 rounded-2xl flex items-center justify-center mb-4 animate-pulse">
          <Leaf size={28} className="text-[#c9a84c]" />
        </div>
        <div className="w-6 h-6 border-2 border-[#c9a84c] border-t-transparent rounded-full animate-spin mb-3" />
        <p className="font-display text-lg font-bold text-[#f0ede4]">Prasad Farm Care 360°</p>
        <p className="text-xs text-[#8fac9a] mt-1">Initializing system session...</p>
      </div>
    );
  }

  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <AppInitializer>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: "#1e4535", color: "#f0ede4", border: "1px solid rgba(255,255,255,0.1)" },
          }}
        />
        <Routes>
          {/* Public */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Founder */}
          <Route path="/founder/dashboard" element={<AuthGuard><FounderDashboard /></AuthGuard>} />
          <Route path="/founder/branches" element={<AuthGuard><FounderBranches /></AuthGuard>} />
          <Route path="/founder/zones" element={<AuthGuard><FounderZones /></AuthGuard>} />
          <Route path="/founder/employees" element={<AuthGuard><FounderEmployees /></AuthGuard>} />
          <Route path="/founder/leads" element={<AuthGuard><FounderLeads /></AuthGuard>} />
          <Route path="/founder/revenue" element={<AuthGuard><FounderRevenue /></AuthGuard>} />
          <Route path="/founder/projects" element={<AuthGuard><FounderProjects /></AuthGuard>} />
          <Route path="/founder/analytics" element={<AuthGuard><FounderAnalytics /></AuthGuard>} />
          <Route path="/founder/approvals" element={<AuthGuard><FounderApprovals /></AuthGuard>} />
          <Route path="/founder/risk" element={<AuthGuard><FounderRiskFraud /></AuthGuard>} />

          {/* Zone Admin */}
          <Route path="/zone-admin/dashboard" element={<AuthGuard><ZoneAdminDashboard /></AuthGuard>} />
          <Route path="/zone-admin/leads" element={<AuthGuard><ZoneAdminLeads /></AuthGuard>} />
          <Route path="/zone-admin/employees" element={<AuthGuard><ZoneAdminEmployees /></AuthGuard>} />
          <Route path="/zone-admin/work" element={<AuthGuard><ZoneAdminWorkManagement /></AuthGuard>} />
          <Route path="/zone-admin/revenue" element={<AuthGuard><ZoneAdminRevenue /></AuthGuard>} />
          <Route path="/zone-admin/brokers" element={<AuthGuard><ZoneAdminBrokers /></AuthGuard>} />
          <Route path="/zone-admin/visits" element={<AuthGuard><ZoneAdminVisits /></AuthGuard>} />
          <Route path="/zone-admin/escalations" element={<AuthGuard><ZoneAdminEscalations /></AuthGuard>} />

          {/* Employee */}
          <Route path="/employee/dashboard" element={<AuthGuard><EmployeeDashboard /></AuthGuard>} />
          <Route path="/employee/leads" element={<AuthGuard><EmployeeLeadPipeline /></AuthGuard>} />
          <Route path="/employee/work-queue" element={<AuthGuard><EmployeeWorkQueue /></AuthGuard>} />
          <Route path="/employee/land-leads" element={<AuthGuard><EmployeeLandLeads /></AuthGuard>} />
          <Route path="/employee/investment-leads" element={<AuthGuard><EmployeeInvestmentLeads /></AuthGuard>} />
          <Route path="/employee/partners" element={<AuthGuard><EmployeePartnerAssignment /></AuthGuard>} />
          <Route path="/employee/follow-up" element={<AuthGuard><EmployeeFollowUp /></AuthGuard>} />

          {/* Agri Officer */}
          <Route path="/agri-officer/dashboard" element={<AuthGuard><AgriDashboard /></AuthGuard>} />
          <Route path="/agri-officer/assignments" element={<AuthGuard><AgriAssignments /></AuthGuard>} />
          <Route path="/agri-officer/prescriptions" element={<AuthGuard><AgriPrescriptions /></AuthGuard>} />
          <Route path="/agri-officer/crop-design" element={<AuthGuard><AgriCropDesign /></AuthGuard>} />
          <Route path="/agri-officer/farm-visits" element={<AuthGuard><AgriFarmVisits /></AuthGuard>} />
          <Route path="/agri-officer/quotes" element={<AuthGuard><AgriQuotes /></AuthGuard>} />

          {/* Farm Employee */}
          <Route path="/farm-employee/dashboard" element={<AuthGuard><FarmEmpDashboard /></AuthGuard>} />
          <Route path="/farm-employee/visits" element={<AuthGuard><FarmEmpMyVisits /></AuthGuard>} />
          <Route path="/farm-employee/submit-proof" element={<AuthGuard><FarmEmpSubmitProof /></AuthGuard>} />
          <Route path="/farm-employee/monitor" element={<AuthGuard><FarmEmpWorkMonitor /></AuthGuard>} />
          <Route path="/farm-employee/harvest" element={<AuthGuard><FarmEmpHarvest /></AuthGuard>} />
          <Route path="/farm-employee/incident" element={<AuthGuard><FarmEmpIncidentReport /></AuthGuard>} />

          {/* Customer */}
          <Route path="/customer/marketplace" element={<AuthGuard><CustomerMarketplace /></AuthGuard>} />
          <Route path="/customer/dashboard" element={<AuthGuard><CustomerDashboard /></AuthGuard>} />
          <Route path="/customer/my-farm" element={<AuthGuard><CustomerMyFarm /></AuthGuard>} />
          <Route path="/customer/agreements" element={<AuthGuard><CustomerAgreements /></AuthGuard>} />
          <Route path="/customer/work-details" element={<AuthGuard><CustomerWorkDetails /></AuthGuard>} />
          <Route path="/customer/crop-health" element={<AuthGuard><CustomerCropHealth /></AuthGuard>} />
          <Route path="/customer/investments" element={<AuthGuard><CustomerInvestments /></AuthGuard>} />
          <Route path="/customer/land-sale" element={<AuthGuard><CustomerLandSale /></AuthGuard>} />
          <Route path="/customer/payments" element={<AuthGuard><CustomerPayments /></AuthGuard>} />
          <Route path="/customer/services" element={<AuthGuard><CustomerServices /></AuthGuard>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AppInitializer>
    </BrowserRouter>
  );
}
