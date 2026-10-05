# FARM360 live database setup

FARM360 uses PostgreSQL for shared staging and production data. SQLite is only a disposable local-development convenience and must not be used as the live database.

## Managed PostgreSQL

Create a managed PostgreSQL database with Render, AWS RDS, Azure Database for PostgreSQL, Supabase or another provider. Require TLS, automated backups, point-in-time recovery where available, and separate staging and production databases.

Copy `backend/.env.production.example` to the secret/environment configuration of the backend host. Do not commit the resulting values. At minimum configure:

```text
ENVIRONMENT=production
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/farm360
AUTO_CREATE_SCHEMA=false
JWT_SECRET=<long random secret>
FRONTEND_URL=https://your-web-domain
CORS_ORIGINS=https://your-web-domain
COOKIE_SECURE=true
COOKIE_SAMESITE=none
```

Render users can deploy the repository's `render.yaml`; it provisions PostgreSQL and injects `DATABASE_URL` automatically.

## Create the schema

Run from the backend directory using the production environment variables:

```powershell
python -m alembic upgrade head
```

Do not run `seed_db.py` in production. It creates demonstration accounts and data.

## Create the first Founder

After migrations, run this once in the backend service shell:

```powershell
python create_founder.py --email owner@yourcompany.com --name "Company Founder"
```

The command prompts for the password without writing it to shell history.

## Create live organizational data

Sign in as the Founder and use the web portal in this order:

1. **Branches** — create the operating branches.
2. **Zones** — create zones inside each branch and optionally select responsible staff.
3. **Employees** — create Zone Admin, Agriculture Officer, Office Employee and Farm Employee accounts and assign their branch/zone.

The Founder can create, read, update and soft-delete staff. A Zone Admin can manage only ordinary operational staff in their own branch and cannot create Founders, other Zone Admins or move users across branches.

## Backups and operations

- Enable daily backups and point-in-time recovery with the database provider.
- Test restoration in staging before launch.
- Restrict database network access to the backend service.
- Rotate database and JWT credentials periodically.
- Run `alembic upgrade head` during every backend deployment before starting the API.
