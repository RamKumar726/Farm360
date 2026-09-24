import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.issues import Issue, IssueStatus, IssueSeverity
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user, require_roles
from sqlalchemy import or_

router = APIRouter(prefix="/issues", tags=["issues"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    farm_id: Optional[str] = None
    work_order_id: Optional[str] = None
    project_id: Optional[str] = None
    severity: IssueSeverity = IssueSeverity.medium
    photo_urls: Optional[str] = None   # JSON string of URLs


class IssueUpdate(BaseModel):
    status: Optional[IssueStatus] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    severity: Optional[IssueSeverity] = None


def issue_to_dict(i: Issue):
    return {
        "id": i.id,
        "title": i.title,
        "description": i.description,
        "farm_id": i.farm_id,
        "work_order_id": i.work_order_id,
        "project_id": i.project_id,
        "reported_by": i.reported_by,
        "assigned_to": i.assigned_to,
        "severity": i.severity.value if hasattr(i.severity, "value") else i.severity,
        "status": i.status.value if hasattr(i.status, "value") else i.status,
        "resolution_notes": i.resolution_notes,
        "photo_urls": i.photo_urls,
        "created_at": str(i.created_at),
        "updated_at": str(i.updated_at) if i.updated_at else None,
    }


def _scoped_issue_query(query, user: User, db: Session):
    if user.role == UserRole.founder:
        return query
    if user.role == UserRole.customer:
        return query.filter(Issue.reported_by == user.id)
    if user.role == UserRole.farm_employee:
        return query.filter(or_(Issue.reported_by == user.id, Issue.assigned_to == user.id))
    if user.role == UserRole.agri_officer:
        return query.filter(Issue.assigned_to == user.id)

    from app.models.projects import Project
    from app.models.leads import Lead
    from app.models.farms import Farm
    from app.models.work_orders import WorkOrder

    if user.role == UserRole.employee:
        project_ids = db.query(Project.id).outerjoin(Lead, Lead.id == Project.lead_id).filter(or_(
            Project.posted_by == user.id,
            Lead.employee_id == user.id,
            Lead.assigned_employee_id == user.id,
        ))
        work_ids = db.query(WorkOrder.id).filter(or_(
            WorkOrder.assigned_employee_id == user.id,
            WorkOrder.created_by == user.id,
        ))
        return query.filter(or_(
            Issue.reported_by == user.id,
            Issue.assigned_to == user.id,
            Issue.project_id.in_(project_ids),
            Issue.work_order_id.in_(work_ids),
        ))

    if user.role == UserRole.zone_admin:
        employee_ids = db.query(User.id)
        if user.branch_id:
            employee_ids = employee_ids.filter(User.branch_id == user.branch_id)
        elif user.zone_id:
            employee_ids = employee_ids.filter(User.zone_id == user.zone_id)
        else:
            employee_ids = employee_ids.filter(User.id == user.id)
        lead_query = db.query(Lead.id)
        if user.branch_id:
            lead_query = lead_query.filter(Lead.branch_id == user.branch_id)
        elif user.zone_id:
            lead_query = lead_query.filter(Lead.zone_id == user.zone_id)
        else:
            lead_query = lead_query.filter(Lead.branch_id.is_(None), Lead.zone_id.is_(None))
        project_ids = db.query(Project.id).filter(or_(Project.posted_by.in_(employee_ids), Project.lead_id.in_(lead_query)))
        farm_ids = db.query(Farm.id).filter(Farm.zone_id == user.zone_id) if user.zone_id else db.query(Farm.id).filter(False)
        work_ids = db.query(WorkOrder.id).filter(or_(
            WorkOrder.project_id.in_(project_ids), WorkOrder.farm_id.in_(farm_ids),
        ))
        return query.filter(or_(
            Issue.reported_by == user.id,
            Issue.assigned_to == user.id,
            Issue.project_id.in_(project_ids),
            Issue.farm_id.in_(farm_ids),
            Issue.work_order_id.in_(work_ids),
        ))
    return query.filter(False)


@router.get("")
def list_issues(
    page: int = Query(1, ge=1),
    page_size: int = Query(50),
    status: Optional[IssueStatus] = None,
    farm_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_roles = {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.farm_employee, UserRole.customer}
    if current_user.role not in allowed_roles:
        raise HTTPException(403, "You cannot access issues")
    query = db.query(Issue).filter(Issue.is_deleted == False)

    query = _scoped_issue_query(query, current_user, db)

    if status:
        query = query.filter(Issue.status == status)
    if farm_id:
        query = query.filter(Issue.farm_id == farm_id)

    total = query.count()
    items = query.order_by(Issue.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "items": [issue_to_dict(i) for i in items]})


@router.post("")
def create_issue(
    body: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Any logged-in user (customer, farm employee, AO) can raise an issue."""
    allowed_roles = {UserRole.founder, UserRole.zone_admin, UserRole.employee, UserRole.agri_officer, UserRole.farm_employee, UserRole.customer}
    if current_user.role not in allowed_roles:
        raise HTTPException(403, "You cannot report issues")
    if not any((body.farm_id, body.project_id, body.work_order_id)):
        raise HTTPException(400, "Link the issue to a farm, project, or work order")
    from app.models.projects import Project
    from app.models.work_orders import WorkOrder
    project = db.query(Project).filter(Project.id == body.project_id).first() if body.project_id else None
    work = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id, WorkOrder.is_deleted == False).first() if body.work_order_id else None
    if body.project_id and not project:
        raise HTTPException(404, "Project not found")
    if body.work_order_id and not work:
        raise HTTPException(404, "Work order not found")
    if body.project_id and work and work.project_id != body.project_id:
        raise HTTPException(400, "Work order does not belong to the selected project")
    if body.farm_id and project and project.farm_id != body.farm_id:
        raise HTTPException(400, "Farm does not belong to the selected project")
    if body.farm_id and work and work.farm_id != body.farm_id:
        raise HTTPException(400, "Work order does not belong to the selected farm")

    if current_user.role not in {UserRole.customer, UserRole.founder}:
        if current_user.role == UserRole.farm_employee:
            if not work or work.farm_employee_id != current_user.id:
                raise HTTPException(404, "Assigned work order not found")
        elif current_user.role == UserRole.agri_officer:
            if not ((work and work.agri_officer_id == current_user.id) or (project and project.assigned_ao_id == current_user.id)):
                raise HTTPException(404, "Assigned project or work order not found")
        else:
            if project:
                from app.routers.finance import _can_manage_project
                if not _can_manage_project(project, current_user):
                    raise HTTPException(404, "Project not found")
            elif work:
                from app.routers.work_orders import _authorize_work_order
                _authorize_work_order(work, current_user, db)
            else:
                raise HTTPException(400, "Staff issues must be linked to an assigned project or work order")
    if current_user.role == UserRole.customer:
        from app.models.farms import Farm
        from app.models.customers import Customer
        from app.models.projects import Project
        from app.models.work_orders import WorkOrder
        from app.models.leads import Lead
        owned_farm = None
        owned_project = None
        if body.farm_id:
            owned_farm = db.query(Farm).join(Customer, Customer.id == Farm.customer_id).filter(
                Farm.id == body.farm_id, Customer.user_id == current_user.id
            ).first()
            if not owned_farm:
                raise HTTPException(404, "Farm not found")
        if body.project_id:
            owned_project = db.query(Project).filter(Project.id == body.project_id, Project.customer_id == current_user.id).first()
            if not owned_project:
                raise HTTPException(404, "Project not found")
        work = None
        if body.work_order_id:
            work = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id).first()
            if not work:
                raise HTTPException(404, "Work order not found")
            if body.project_id and work.project_id != body.project_id:
                raise HTTPException(400, "Work order does not belong to the selected project")
            if body.farm_id and work.farm_id != body.farm_id:
                raise HTTPException(400, "Work order does not belong to the selected farm")
            farm_owned = db.query(Farm).join(Customer, Customer.id == Farm.customer_id).filter(Farm.id == work.farm_id, Customer.user_id == current_user.id).first() if work.farm_id else None
            lead_owned = db.query(Lead).filter_by(id=work.lead_id, customer_id=current_user.id).first() if work.lead_id else None
            work_project_owned = bool(work.project_id and db.query(Project.id).filter(Project.id == work.project_id, Project.customer_id == current_user.id).first())
            if not (farm_owned or lead_owned or work_project_owned):
                raise HTTPException(404, "Work order not found")
        if owned_project and body.farm_id and owned_project.farm_id != body.farm_id:
            raise HTTPException(400, "Farm does not belong to the selected project")
    issue = Issue(
        id=str(uuid.uuid4()),
        title=body.title,
        description=body.description,
        farm_id=body.farm_id,
        work_order_id=body.work_order_id,
        project_id=body.project_id,
        reported_by=current_user.id,
        severity=body.severity,
        status=IssueStatus.open,
        photo_urls=body.photo_urls,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    # Notify staff responsible for this project or farm, without crossing tenants.
    try:
        from app.services.notification_service import notify_incident_reported
        recipient_ids = set()
        if body.project_id:
            from app.models.projects import Project
            from app.models.leads import Lead
            project = db.query(Project).filter(Project.id == body.project_id).first()
            if project:
                recipient_ids.add(project.posted_by)
                lead = db.query(Lead).filter(Lead.id == project.lead_id).first() if project.lead_id else None
                if lead:
                    recipient_ids.update(value for value in (lead.employee_id, lead.assigned_employee_id, lead.assigned_ao_id) if value)
        farm_id = body.farm_id
        if body.work_order_id:
            from app.models.work_orders import WorkOrder
            work = db.query(WorkOrder).filter(WorkOrder.id == body.work_order_id).first()
            if work:
                farm_id = farm_id or work.farm_id
                recipient_ids.update(value for value in (work.assigned_employee_id, work.agri_officer_id) if value)
        if farm_id:
            from app.models.farms import Farm
            farm = db.query(Farm).filter(Farm.id == farm_id).first()
            if farm and farm.zone_id:
                admins = db.query(User).filter(
                    User.role.in_([UserRole.zone_admin, UserRole.employee]),
                    User.zone_id == farm.zone_id, User.is_deleted == False,
                ).all()
                recipient_ids.update(admin.id for admin in admins)
        for recipient_id in recipient_ids - {current_user.id}:
            notify_incident_reported(recipient_id, farm_id or issue.id, db)
    except Exception:
        pass

    return success(data=issue_to_dict(issue), message="Issue raised successfully")


@router.get("/{issue_id}")
def get_issue(issue_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.is_deleted == False).first()
    if not issue:
        raise HTTPException(404, "Issue not found")
    _authorize_issue(issue, current_user, db)
    return success(data=issue_to_dict(issue))


@router.patch("/{issue_id}")
def update_issue(
    issue_id: str,
    body: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.employee, UserRole.agri_officer, UserRole.zone_admin, UserRole.founder)),
):
    """Employees / Agri Officers / Zone Admins / Founders can update issue status."""
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.is_deleted == False).first()
    if not issue:
        raise HTTPException(404, "Issue not found")
    _authorize_issue(issue, current_user, db)

    if body.assigned_to is not None:
        assignee = db.query(User).filter(
            User.id == body.assigned_to,
            User.role.in_([UserRole.employee, UserRole.agri_officer, UserRole.zone_admin]),
            User.is_deleted == False,
        ).first()
        if not assignee:
            raise HTTPException(400, "Issue assignee must be an active employee, Agriculture Officer, or Zone Admin")
        if current_user.role == UserRole.zone_admin and current_user.zone_id and assignee.zone_id != current_user.zone_id:
            raise HTTPException(400, "Issue assignee must belong to your zone")

    if body.status is not None:
        issue.status = body.status
    if body.assigned_to is not None:
        issue.assigned_to = body.assigned_to
    if body.resolution_notes is not None:
        issue.resolution_notes = body.resolution_notes
    if body.severity is not None:
        issue.severity = body.severity

    db.commit()
    db.refresh(issue)
    return success(data=issue_to_dict(issue), message=f"Issue updated to status '{issue.status.value}'")


@router.post("/{issue_id}/escalate")
def escalate_issue(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.zone_admin, UserRole.founder, UserRole.employee)),
):
    """Escalate an issue to senior management."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(404, "Issue not found")
    _authorize_issue(issue, current_user, db)
    issue.status = IssueStatus.escalated
    db.commit()
    db.refresh(issue)
    return success(data=issue_to_dict(issue), message="Issue escalated to senior management")


@router.post("/{issue_id}/resolve")
def resolve_issue(
    issue_id: str,
    resolution_notes: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.employee, UserRole.agri_officer, UserRole.zone_admin, UserRole.founder)),
):
    """Mark an issue as resolved with notes."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(404, "Issue not found")
    _authorize_issue(issue, current_user, db)
    issue.status = IssueStatus.resolved
    issue.resolution_notes = resolution_notes
    db.commit()
    db.refresh(issue)
    return success(data=issue_to_dict(issue), message="Issue marked as resolved")


@router.delete("/{issue_id}")
def delete_issue(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.founder, UserRole.zone_admin)),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(404, "Issue not found")
    _authorize_issue(issue, current_user, db)
    issue.is_deleted = True
    db.commit()
    return success(message="Issue deleted")


def _authorize_issue(issue: Issue, user: User, db: Session) -> None:
    if not _scoped_issue_query(db.query(Issue).filter(Issue.id == issue.id), user, db).first():
        raise HTTPException(404, "Issue not found")
