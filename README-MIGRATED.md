# Isle Be There - Tech Stack Migration

## Overview

This project has been migrated from Flask+Jinja+Bootstrap to FastAPI+Vue.js+Tailwind CSS.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication with python-jose
- **PostgreSQL** - Database

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vite** - Next-generation build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Pinia** - Intuitive, type safe, light and flexible Store for Vue
- **Axios** - HTTP client

## Getting Started

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your database URL and JWT secret

# Run the server
uvicorn main:app --reload
```

The API will be available at http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env
# Set VITE_API_URL=http://localhost:8000

# Run development server
npm run dev
```

The app will be available at http://localhost:5173

### Production Build

```bash
cd frontend
npm run build
```

The build output will be in the `dist` folder.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Listings
- `GET /api/listings` - List all listings
- `GET /api/listings/{id}` - Get listing details
- `POST /api/listings` - Create listing (authenticated)
- `PUT /api/listings/{id}` - Update listing
- `DELETE /api/listings/{id}` - Delete listing

### Bookings
- `GET /api/bookings` - List user bookings
- `GET /api/bookings/{id}` - Get booking details
- `POST /api/bookings` - Create booking
- `PUT /api/bookings/{id}` - Update booking
- `DELETE /api/bookings/{id}` - Cancel booking

### Reviews
- `GET /api/reviews` - List reviews
- `POST /api/reviews` - Create review
- `PUT /api/reviews/{id}` - Update review
- `DELETE /api/reviews/{id}` - Delete review

## Project Structure

```
isle-be-there/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Security, auth
│   │   └── models/       # Database models
│   ├── main.py           # App entry
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/    # Vue components
    │   ├── views/         # Page components
    │   ├── services/      # API services
    │   └── stores/       # Pinia stores
    ├── package.json
    └── vite.config.js
```
