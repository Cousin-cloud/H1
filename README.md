# Production Capacity Planning System

Full-stack standalone app for Joinery + Metal plant planning with 3 shifts, Supabase auth/RLS, demand uploads, validations, and planning analytics.

## Stack
- Frontend: React + TypeScript + Recharts
- Backend: FastAPI
- DB/Auth: Supabase Postgres + Auth + RLS

## Setup
1. Create a Supabase project.
2. Run `supabase/schema.sql` then `supabase/seed.sql` in SQL Editor.
3. Create users in Supabase Auth and map roles in `user_roles` table.
4. Backend env (`backend/.env`):
   - `SUPABASE_URL=...`
   - `SUPABASE_SERVICE_ROLE_KEY=...`
   - `SUPABASE_JWT_SECRET=...`
   - `CORS_ORIGINS=http://localhost:5173`
5. Frontend env (`frontend/.env`):
   - `VITE_API_URL=http://localhost:8000`
6. Run:
   - Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
   - Frontend: `cd frontend && npm install && npm run dev`

## Pseudocode (core planning)
```
parse file (csv/xlsx)
map flexible headers to canonical fields
for each row:
  validate date range + numeric hours
  if invalid -> save to error log
  else:
    days = inclusive(end-start)+1
    daily_hours = required_hours/days
    emit one demand row per day (even distribution)
aggregate demand by month+plant+operation+division and scenario forecast filter
compute capacity per plant+operation:
  daily = sum(workers_per_shift*hours_per_shift across shifts)
  monthly = daily*working_days_per_month
  stretch = monthly*1.2
compare demand vs monthly/stretch and set status green/amber/red
```

## API
- `POST /api/upload/preview` (planner/admin)
- `POST /api/upload/confirm` (planner/admin)
- `GET /api/capacity`
- `POST /api/capacity` (admin)
- `GET /api/planning?scenario=confirmed|confirmed_probable|all`

## Notes
- Failed rows are persisted in `upload_error_logs` with full reason.
- Demand is decomposed to daily records for accurate monthly split.
- Designed for high-volume aggregation via indexed dimensions.
