from typing import List, Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.jwt import decode_token
from app.models.users import User, UserRole


def get_current_user(
    access_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not access_token:
        raise credentials_exception

    payload = decode_token(access_token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if user is None:
        raise credentials_exception
    return user


def require_roles(*roles: UserRole):
    """Dependency factory — enforces that current user has one of the given roles."""
    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return current_user
    return _checker


# Convenience role guards
def founder_only(current_user: User = Depends(require_roles(UserRole.founder))) -> User:
    return current_user


def founder_or_zone_admin(
    current_user: User = Depends(
        require_roles(UserRole.founder, UserRole.zone_admin)
    )
) -> User:
    return current_user


def staff_roles(
    current_user: User = Depends(
        require_roles(
            UserRole.founder, UserRole.zone_admin, UserRole.employee,
            UserRole.agri_officer, UserRole.farm_employee,
        )
    )
) -> User:
    return current_user


def apply_scope_filter(query, model, current_user: User):
    """Apply role-based data scoping to any SQLAlchemy query."""
    role = current_user.role
    if role == UserRole.founder:
        return query  # sees ALL data
    elif role == UserRole.zone_admin:
        if hasattr(model, "branch_id"):
            return query.filter(model.branch_id == current_user.branch_id)
    elif role == UserRole.employee:
        if hasattr(model, "zone_id"):
            return query.filter(model.zone_id == current_user.zone_id)
    elif role == UserRole.agri_officer:
        if hasattr(model, "agri_officer_id"):
            return query.filter(model.agri_officer_id == current_user.id)
    elif role == UserRole.farm_employee:
        if hasattr(model, "farm_employee_id"):
            return query.filter(model.farm_employee_id == current_user.id)
    elif role == UserRole.customer:
        if hasattr(model, "customer_id"):
            return query.filter(model.customer_id == current_user.id)
    elif role == UserRole.real_estate:
        if hasattr(model, "real_estate_user_id"):
            return query.filter(model.real_estate_user_id == current_user.id)
    return query
