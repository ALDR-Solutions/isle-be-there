# Isle Be There

Isle Be There is a travel platform with a FastAPI backend and a Vue 3 frontend.

This guide is optimized for a Windows machine using PowerShell and a local-first demo setup with:

- FastAPI on `http://localhost:8000`
- Vite on `http://localhost:5173`
- PostgreSQL running in Docker

## Prerequisites

Install these first:

- `Git`
- `Python 3.9.x`
- `Node.js` and `npm`
- `Docker Desktop`

Notes:

- The repo targets Python `3.9.x` to match `.python-version` and CI.
- `.env` files are local-only and must not be committed.

## Quick Start

Run every command below from the repo root unless noted otherwise.

### 1. Start PostgreSQL

```powershell
docker compose up -d db
```

This starts a local PostgreSQL instance on `localhost:5432`.

### 2. Create local env files

```powershell
Copy-Item .env.example .env
Copy-Item frontend\.env.example frontend\.env
```

The default examples are already set up for a minimal local demo.

### 3. Create and activate a Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install backend dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The root `requirements.txt` is a thin wrapper around `backend\requirements.txt`, which is the backend dependency source of truth.

### 5. Bootstrap the local database schema

```powershell
python backend\init_db.py
```

This creates the schema and seeds only a few defaults such as pricing and discount rows.

### 6. Start the backend

```powershell
python -m uvicorn backend.main:app --reload
```

Backend URLs:

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 7. Start the frontend in a second terminal

Open a new PowerShell window in the repo root and run:

```powershell
npm --prefix frontend install
npm --prefix frontend run dev
```

Optional workspace helper scripts are also available:

```powershell
npm run frontend:install
npm run frontend:dev
```

## Open the App

Open:

- App: `http://localhost:5173`

The frontend example env file sets:

- `VITE_API_URL=http://localhost:8000`

The Vite proxy still exists, but the explicit API URL keeps the setup easier to understand for a fresh machine.

## What Works Without Extra Keys

With the example env files and local Postgres running, the minimal local demo is intended to support:

- backend startup
- frontend startup
- API docs
- health check
- auth flows that do not depend on real email delivery
- listings, bookings, itineraries, and general UI navigation

Optional integrations can stay blank for a demo:

- `Stripe` keys are only needed for payment flows
- `Resend` is only needed for real email delivery
- `Supabase` is only needed for image uploads
- review ML assets stay in the repo, and the app can still run in degraded or fallback mode when optional external services are not configured

## What Does Not Come Preloaded

A fresh local database is mostly empty.

After running `python backend\init_db.py`, you should expect:

- schema creation
- default pricing seed data
- default discount seed data

You should not expect:

- preloaded listings
- preloaded businesses
- preloaded interests
- demo bookings or itinerary data

If you want a content-rich demo, sample data needs to be added separately.

## Important Local Environment Values

The root `.env.example` already includes the main values for local use:

- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/isle_be_there`
- `ENV=development`
- `ENABLE_BACKGROUND_JOBS=false`

Recommended defaults for a lighter local demo:

- keep `ENV=development`
- keep `ENABLE_BACKGROUND_JOBS=false`

In local development, the app can fall back to local-safe auth secrets if `JWT_SECRET_KEY` and `FORGET_PWD_SECRET_KEY` are blank.

## Troubleshooting

### PowerShell blocks virtual environment activation

Run this in the current PowerShell session and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Port `5432`, `8000`, or `5173` is already in use

- stop the process using that port, or
- change the conflicting local service before retrying

### Docker is not running

Make sure Docker Desktop is open before running:

```powershell
docker compose up -d db
```

### Backend cannot connect to the database

Check that:

- Docker Desktop is running
- the `db` container is up
- `.env` still points to `localhost:5432`

Helpful command:

```powershell
docker compose ps
```

### Frontend starts but cannot reach the backend

Check that:

- the backend is running at `http://localhost:8000`
- `frontend\.env` exists
- `frontend\.env` contains `VITE_API_URL=http://localhost:8000`

## Advanced: Database Migrations

The default local setup uses:

```powershell
python backend\init_db.py
```

If you need to work with Alembic directly, use your local `DATABASE_URL` and run commands from the `backend` folder. The committed Alembic config now uses a safe local placeholder and should be adjusted through your local environment, not by committing hosted database URLs.

## Project Structure

```text
backend/app/
  core/
  infrastructure/
  modules/
  shared/

frontend/src/
  components/
  layouts/
  services/
  stores/
  views/
```
