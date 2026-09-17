"""
Crop Cycle Auto-Generation Service
After agriculture officer's crop design is approved:
  → Crop Cycle auto-generated
  → Work Cycle auto-generated (work orders)
  → Visit Cycle auto-generated (visits)
"""
import uuid
from datetime import date, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.models.crop_designs import CropDesign
from app.models.crop_cycles import CropCycle
from app.models.work_orders import WorkOrder, WorkOrderType, WorkOrderStatus, PaymentStatus
from app.models.visits import Visit, VisitType, VisitStatus


def generate_cycles_from_design(crop_design: CropDesign, db: Session):
    """Auto-generate crop cycle, work orders, and visit schedule after design approval."""
    farm_id = crop_design.farm_id
    today = date.today()

    # 1. Generate Crop Cycle (quarterly by default)
    crop_cycles = []
    for i, season in enumerate(["Kharif Season", "Rabi Season", "Zaid Season", "Post-Harvest"]):
        cycle = CropCycle(
            id=str(uuid.uuid4()),
            crop_design_id=crop_design.id,
            farm_id=farm_id,
            cycle_name=f"{season} - {today.year}",
            start_date=today + timedelta(days=i * 90),
            end_date=today + timedelta(days=(i + 1) * 90 - 1),
            auto_generated=True,
        )
        db.add(cycle)
        crop_cycles.append(cycle)

    # 2. Generate Work Orders (standard sequence for one-time workflow)
    work_types_sequence = [
        WorkOrderType.soil_water_test,
        WorkOrderType.land_leveling,
        WorkOrderType.cleaning,
        WorkOrderType.irrigation,
        WorkOrderType.cropping,
        WorkOrderType.fertilizer_pestcontrol,
        WorkOrderType.harvest,
    ]
    for idx, wtype in enumerate(work_types_sequence):
        wo = WorkOrder(
            id=str(uuid.uuid4()),
            farm_id=farm_id,
            agri_officer_id=crop_design.agri_officer_id,
            type=wtype,
            status=WorkOrderStatus.pending,
            start_date=today + timedelta(days=idx * 14),
            end_date=today + timedelta(days=idx * 14 + 13),
            payment_status=PaymentStatus.pending,
            created_by=crop_design.agri_officer_id,
        )
        db.add(wo)

        # 3. Generate Visit for each work order
        visit = Visit(
            id=str(uuid.uuid4()),
            work_order_id=wo.id,
            farm_id=farm_id,
            farm_employee_id=crop_design.agri_officer_id,  # placeholder; will be replaced by assignment
            type=VisitType.auto_visit,
            status=VisitStatus.pending,
            visited_at=None,
        )
        db.add(visit)

    db.commit()
    return crop_cycles
