import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { FARM_EMP_NAV } from "./_nav";
import WorkOrderCard from "../../components/WorkOrderCard";
import { workOrdersAPI } from "../../config/api";

export default function FarmEmpWorkMonitor() {
  const [workOrders, setWorkOrders] = useState([]);
  useEffect(() => { workOrdersAPI.list().then((r) => { if (r.success) setWorkOrders(r.data.items); }); }, []);
  return (
    <PortalPage title="Work Monitor" subtitle="Track all work orders assigned to you" navItems={FARM_EMP_NAV}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {workOrders.map((w) => <WorkOrderCard key={w.id} workOrder={w} />)}
        {workOrders.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No work orders assigned</p>}
      </div>
    </PortalPage>
  );
}
