"""
Work Assignment Service
Zone-based queue assignment for farm employees.
Rule: Each zone has one responsible employee.
If absent, the next available employee in any zone takes over.
No work_order record is changed — only the runtime assignment pointer.
"""
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from app.models.users import User, UserRole
from app.models.zones import Zone
from app.models.attendance import Attendance, AttendanceStatus
from app.models.work_orders import WorkOrder


def get_available_employee_for_zone(zone_id: str, work_date: date, db: Session) -> Optional[User]:
    """Return the responsible employee for a zone, or next available if absent."""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone or not zone.responsible_employee_id:
        return _find_any_available_farm_employee(work_date, db)

    # Check if responsible employee is absent
    absence = db.query(Attendance).filter(
        Attendance.user_id == zone.responsible_employee_id,
        Attendance.date == work_date,
        Attendance.status.in_([AttendanceStatus.absent, AttendanceStatus.holiday, AttendanceStatus.sunday]),
    ).first()

    if not absence:
        # Responsible employee is available
        return db.query(User).filter(User.id == zone.responsible_employee_id).first()

    # If absent, check if attendance record has an explicit replacement
    if absence.replacement_user_id:
        return db.query(User).filter(User.id == absence.replacement_user_id, User.is_available == True).first()

    # Fall back: find any available farm employee
    return _find_any_available_farm_employee(work_date, db, exclude_id=zone.responsible_employee_id)


def _find_any_available_farm_employee(work_date: date, db: Session, exclude_id: Optional[str] = None) -> Optional[User]:
    """Find any farm employee who is not absent on the given date."""
    absent_ids = db.query(Attendance.user_id).filter(
        Attendance.date == work_date,
        Attendance.status.in_([AttendanceStatus.absent]),
    ).subquery()

    query = db.query(User).filter(
        User.role == UserRole.farm_employee,
        User.is_available == True,
        User.is_deleted == False,
        User.id.notin_(absent_ids),
    )
    if exclude_id:
        query = query.filter(User.id != exclude_id)
    return query.first()


def auto_assign_farm_employee(work_order: WorkOrder, db: Session) -> Optional[User]:
    """Auto-assign a farm employee based on the farm's zone and work date."""
    from app.models.farms import Farm
    farm = db.query(Farm).filter(Farm.id == work_order.farm_id).first()
    if not farm or not farm.zone_id:
        return None

    work_date = work_order.start_date or date.today()
    employee = get_available_employee_for_zone(farm.zone_id, work_date, db)
    if employee:
        work_order.farm_employee_id = employee.id
        db.commit()
    return employee
