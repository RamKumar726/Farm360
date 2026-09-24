from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import FRONTEND_URL

# Import all models (required for Alembic autogenerate and SQLAlchemy relationship resolution)
import app.models  # noqa: F401

# Import routers
from app.routers import (
    auth, users, branches, zones, leads, work_orders,
    visits, farms, agreements, prescriptions, crop_designs,
    land_sales, investments, projects, brokers, work_partners,
    notifications, attendance, analytics, issues, harvests, payments, finance, services,
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Prasad Farm Care 360°",
    description="Multi-tenant farm management, real estate, and investment platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,   # Required for httpOnly cookie auth
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(branches.router)
app.include_router(zones.router)
app.include_router(leads.router)
app.include_router(work_orders.router)
app.include_router(visits.router)
app.include_router(farms.router)
app.include_router(agreements.router)
app.include_router(prescriptions.router)
app.include_router(crop_designs.router)
app.include_router(land_sales.router)
app.include_router(investments.router)
app.include_router(projects.router)
app.include_router(brokers.router)
app.include_router(work_partners.router)
app.include_router(notifications.router)
app.include_router(attendance.router)
app.include_router(analytics.router)
app.include_router(issues.router)
app.include_router(harvests.router)
app.include_router(payments.router)
app.include_router(finance.router)
app.include_router(services.router)


@app.get("/")
def root():
    return {"success": True, "message": "Prasad Farm Care 360° API is running 🌿"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "Prasad Farm Care 360°"}
