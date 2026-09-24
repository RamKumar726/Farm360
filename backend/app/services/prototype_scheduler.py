"""Create database-backed work orders from a crop prototype."""
import uuid
from datetime import date, timedelta

from app.models.projects import ProjectType
from app.models.prototypes import Prototype
from app.models.work_orders import WorkOrder, WorkOrderStatus, WorkOrderType
from app.services.notification_service import notify_work_order_created


def schedule_prototype_tasks(project, prototype: Prototype, db, start_date: date, end_date: date, created_by: str):
    if not project.farm_id:
        return []
    cycle_length = max(1, int(prototype.total_duration_days or 1))
    cycle_start = start_date
    cycle_number = 1
    created = []

    while cycle_start < end_date:
        cycle_end = min(end_date, cycle_start + timedelta(days=cycle_length))

        def add_task(due, task_type, label, ao_task=False):
            if due > cycle_end or due > end_date:
                return
            notes = f"Prototype {prototype.id}: Cycle {cycle_number}, Day {(due - cycle_start).days} - {label} ({prototype.crop_name})"
            exists = db.query(WorkOrder.id).filter(
                WorkOrder.project_id == project.id,
                WorkOrder.type == task_type,
                WorkOrder.start_date == due,
                WorkOrder.notes == notes,
                WorkOrder.is_deleted == False,
            ).first()
            if exists:
                return
            work_order = WorkOrder(
                id=str(uuid.uuid4()), farm_id=project.farm_id, project_id=project.id,
                type=task_type,
                status=WorkOrderStatus.assigned if ao_task and project.assigned_ao_id else WorkOrderStatus.pending,
                start_date=due, end_date=due,
                agri_officer_id=project.assigned_ao_id if ao_task else None,
                notes=notes, created_by=created_by,
            )
            db.add(work_order)
            db.flush()
            created.append(work_order)
            if work_order.agri_officer_id:
                notify_work_order_created(work_order.agri_officer_id, work_order.id, db)

        schedules = (
            (prototype.water_schedule_days, WorkOrderType.irrigation, "Watering", False),
            (prototype.fertilizer_schedule_days, WorkOrderType.fertilizer_pestcontrol, "Fertilizer", False),
            (prototype.ao_visit_schedule_days, WorkOrderType.monitoring, "Agriculture Officer inspection", True),
        )
        for interval, work_type, label, ao_task in schedules:
            if not interval or interval < 1:
                continue
            day = int(interval)
            while day <= prototype.total_duration_days:
                add_task(cycle_start + timedelta(days=day), work_type, label, ao_task)
                day += int(interval)

        if prototype.harvest_day and 1 <= prototype.harvest_day <= prototype.total_duration_days:
            add_task(cycle_start + timedelta(days=prototype.harvest_day), WorkOrderType.harvest, "Harvest")

        if project.type != ProjectType.lease:
            break
        cycle_start += timedelta(days=cycle_length)
        cycle_number += 1

    return created
