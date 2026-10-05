# FARM360 Web Application

FARM360 contains a FastAPI backend and a React/Vite frontend. Local development uses SQLite by default, so PostgreSQL, Razorpay, Twilio and Cloudinary are not required to explore the application.

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer, including npm
- Windows PowerShell 5.1 or PowerShell 7

## Fresh clone: setup and run

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-dev.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\run-dev.ps1
```

Open <http://localhost:5173>. API documentation is available at <http://localhost:8000/api/docs>.

The setup script creates a Python virtual environment, installs backend and frontend dependencies, copies safe development environment files, creates the SQLite schema and loads demonstration data. The run script starts both services; press `Ctrl+C` to stop them.

## Demo login

All seeded demonstration accounts use the password `password123`.

| Role | Email |
| --- | --- |
| Founder | `founder@prasadfarm.com` |
| Zone administrator | `zoneadmin@prasadfarm.com` |
| Employee | `employee@prasadfarm.com` |
| Agriculture Officer | `agriofficer@prasadfarm.com` |
| Farm employee | `farmemployee@prasadfarm.com` |
| Customer | `customer@prasadfarm.com` |

## Manual startup

Backend terminal:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python seed_db.py
python -m uvicorn app.main:app --reload --port 8000
```

Frontend terminal:

```powershell
cd frontend
npm run dev
```

An unauthenticated `GET /auth/me` returning `401` is expected before login. It is a session check, not an application failure.

## Run automated checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
cd frontend
npm run build
```

## Production

Production must set `ENVIRONMENT=production`, a strong `JWT_SECRET`, an exact `CORS_ORIGINS` allowlist and a PostgreSQL `DATABASE_URL`. Apply migrations from `backend` with `alembic upgrade head`. Never use the demonstration database, users or passwords in production.

See [docs/DATABASE_DEPLOYMENT.md](docs/DATABASE_DEPLOYMENT.md) for live PostgreSQL deployment and first-Founder setup.
