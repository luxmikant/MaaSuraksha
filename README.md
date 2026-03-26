# MaaSuraksha

MaaSuraksha is a maternal health screening and tracking web application for mothers and ASHA workers.  
It combines a Flask backend, SQLite database, and an ML risk model to provide early pregnancy risk awareness and daily health logging.

## Features

- Pregnancy risk screening with `Low Risk`, `Mid Risk`, and `High Risk` outputs
- Daily tracker for mood, sleep, water intake, and symptoms
- ASHA dashboard with recent alerts
- Login and signup with role-based access (`patient`, `asha`)
- Bilingual UI support (English/Hindi)
- Light/Dark theme toggle

## Tech Stack

- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: Python + Flask
- Database: SQLite (local) or PostgreSQL/Neon (production)
- ML: scikit-learn model serialized with `joblib` (`maternal_risk_model.pkl`)

## Project Structure

```text
MaaSuraksha/
├── app.py
├── requirements.txt
├── render.yaml
├── vercel.json
├── maasuraksha.db
├── maternal_risk_model.pkl
├── index.html
├── login.html
├── form.html
├── tracker.html
├── dashboard.html
├── css/
├── js/
│   ├── api-config.js
│   ├── api-config.example.js
│   ├── main.js
│   └── translations.js
├── scripts/
│   └── migrate_sqlite_to_postgres.py
├── assets/
├── maternal-risk-prediction.ipynb
└── ARCHITECTURE_REFERENCE.md
```

## Prerequisites

- Python 3.9+ recommended
- `pip`

## Installation

1. Open terminal in project root (`MaaSuraksha`).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
python app.py
```

The app runs at: `http://127.0.0.1:5000`

## Default Seeded Users

The backend seeds these accounts automatically:

- Patient: `mother1` / `mother123`
- ASHA: `asha1` / `asha123`

You can also create new users from `login.html`.

## Main Pages

- `/` or `/index.html` – Home page
- `/login.html` – Login/Signup
- `/form.html` – Pregnancy screening form
- `/tracker.html` – Daily tracker form and timeline
- `/dashboard.html` – ASHA alerts dashboard

## API Endpoints

### Authentication

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Screening and Alerts

- `POST /api/predict` – Returns maternal risk level and stores screening entry
- `GET /api/alerts` – Returns latest prediction alerts

### Daily Tracker

- `POST /api/tracker` – Save tracker entry
- `GET /api/tracker` – Fetch latest tracker logs

## Production Deployment (Render Backend + Vercel Frontend + Neon DB)

### 1) Create Neon database

- Create a Neon project and copy the PostgreSQL connection string.
- Keep SSL enabled (`sslmode=require`).

### 2) Deploy backend to Render

- Create a new **Web Service** from this repo.
- Render can use `render.yaml` automatically.
- Set required environment variables in Render:
  - `DATABASE_URL` = your Neon connection string
  - `SECRET_KEY` = strong random secret
  - `FLASK_ENV` = `production`
  - `PGSSLMODE` = `require`
  - `FRONTEND_ORIGIN` = your Vercel app URL (for CORS)
- Start command used:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
```

### 3) Migrate SQLite data to Neon (one-time)

Run this locally after `DATABASE_URL` is set:

```bash
python scripts/migrate_sqlite_to_postgres.py
```

Optional env override for sqlite file:

```bash
set SQLITE_PATH=maasuraksha.db
```

### 4) Configure frontend API base URL

For split deployment, frontend must call Render backend.

Edit `js/api-config.js`:

```js
window.MAASURAKSHA_API_BASE = "https://your-render-service.onrender.com";
```

Then deploy frontend to Vercel.

### 5) Deploy frontend to Vercel

- Import the same repo in Vercel.
- Framework preset: **Other** (static site).
- `vercel.json` handles static routing.
- After deployment, update `FRONTEND_ORIGIN` on Render to the final Vercel URL.

### 6) Post-deploy checklist

- Open Vercel URL and verify pages load.
- Test login/signup.
- Test screening (`/api/predict`) and tracker (`/api/tracker`).
- Confirm rows are written in Neon tables: `users`, `predictions`, `daily_tracker`.

## Database Tables

- `users` – username, password, role
- `predictions` – screening inputs + risk output + timestamp
- `daily_tracker` – daily well-being logs + timestamp

## Important Note

This tool is for **screening support only** and is **not a medical diagnosis system**.

## Future Improvements

- Better feature mapping from form fields to trained ML model inputs
- Password hashing and stronger auth security
- Automated tests (unit/integration)
- Deployment hardening (HTTPS, monitoring, CI/CD)

