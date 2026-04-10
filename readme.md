# Isle Be There

Travel platform with a FastAPI backend and Vue 3 frontend.

## Stack

- Backend: FastAPI, SQLModel, SQLAlchemy, PostgreSQL
- Frontend: Vue 3, Vite, Pinia, Axios, Tailwind CSS

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend URLs:

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Backend environment variables for image uploads:

- `SUPABASE_URL` (your project URL, e.g. `https://<project-ref>.supabase.co`)
- `SUPABASE_SERVICE_ROLE_KEY` (server-side key for Storage upload API)
- `SUPABASE_STORAGE_BUCKET` (optional, defaults to `uploads`)
- `MAX_UPLOAD_FILE_SIZE_MB` (optional, defaults to `10`)
- `ALLOWED_IMAGE_MIME_TYPES` (optional CSV, defaults to `image/jpeg,image/png,image/webp,image/gif`)

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- App: `http://localhost:5173`

Set `VITE_API_URL` in your frontend env file if needed.

## Structure

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
