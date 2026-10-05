from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import (
    CORS_ORIGINS, FEATURE_INVESTMENTS, FEATURE_LAND_SALES, PAYMENT_MODE,
    ENVIRONMENT, JWT_SECRET, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET,
)

# Import all models (required for Alembic autogenerate and SQLAlchemy relationship resolution)
import app.models  # noqa: F401

# Import routers
from app.routers import (
    auth, users, branches, zones, leads, work_orders,
    visits, farms, agreements, prescriptions, crop_designs,
    land_sales, investments, projects, brokers, work_partners,
    notifications, attendance, analytics, issues, harvests, payments, finance, services, quotes, invoices, audit,
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Prasad Farm Care 360°",
    description="Multi-tenant farm management, real estate, and investment platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

if ENVIRONMENT == "production" and JWT_SECRET == "change-me-in-production":
    raise RuntimeError("JWT_SECRET must be configured in production")
if PAYMENT_MODE == "live" and not all((RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET)):
    raise RuntimeError("Live payments require Razorpay key id, key secret and webhook secret")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = list(dict.fromkeys(CORS_ORIGINS + (["http://localhost:5173", "http://localhost:3000"] if ENVIRONMENT != "production" else [])))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
if FEATURE_LAND_SALES:
    app.include_router(land_sales.router)
if FEATURE_INVESTMENTS:
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
app.include_router(quotes.router)
app.include_router(invoices.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return {"success": True, "message": "Prasad Farm Care 360° API is running 🌿"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "Prasad Farm Care 360°"}


@app.get("/features")
def features():
    return {
        "success": True,
        "data": {
            "investments": FEATURE_INVESTMENTS,
            "land_sales": FEATURE_LAND_SALES,
            "payment_mode": PAYMENT_MODE,
            "native_mobile": False,
        },
    }
