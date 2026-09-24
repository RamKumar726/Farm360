import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.models.users import User, UserRole
from app.models.customers import Customer
from app.models.leads import Lead
from app.auth.jwt import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: UserRole = UserRole.customer


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


def error(err="", message=""):
    return {"success": False, "error": err, "message": message}


@router.post("/login")
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email, User.is_deleted == False).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token({"sub": user.id})

    # Set cookie with samesite=none and secure=True for cross-origin compatibility
    response.set_cookie("access_token", access_token, httponly=True, samesite="none", secure=True, max_age=3600)
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="none", secure=True, max_age=604800)

    return success(
        data={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "access_token": access_token,
        },
        message="Login successful",
    )


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        phone=body.phone,
        password_hash=hash_password(body.password),
        # Public registration must never allow a caller to grant themselves a staff role.
        role=UserRole.customer,
    )
    db.add(user)
    db.flush()
    db.add(Customer(id=str(uuid.uuid4()), user_id=user.id))
    db.query(Lead).filter(Lead.contact_email == user.email, Lead.customer_id == None).update(
        {Lead.customer_id: user.id}, synchronize_session=False
    )
    db.commit()
    db.refresh(user)
    return success(data={"id": user.id, "email": user.email, "role": user.role.value}, message="Registered successfully")


@router.post("/refresh-token")
def refresh_token(response: Response, refresh_token: Optional[str] = Cookie(default=None), db: Session = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.query(User).filter(User.id == payload["sub"], User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token({"sub": user.id, "role": user.role.value})
    response.set_cookie("access_token", new_access, httponly=True, samesite="lax", max_age=3600)
    return success(message="Token refreshed")


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return success(message="Logged out")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success(data={
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value,
        "branch_id": current_user.branch_id,
        "zone_id": current_user.zone_id,
    })
