# Sports Analytics System

A sports team selection and performance analytics project with a FastAPI backend and a React frontend.

The project currently supports player roster management and performance record logging. The backend exposes REST APIs, stores data with SQLAlchemy, and defaults to SQLite for local development. A PostgreSQL service is also available through Docker Compose.

## What Has Been Done So Far

- Built a FastAPI backend with routes for players and performance records.
- Added SQLAlchemy models, Pydantic schemas, database setup, and Alembic migration scaffolding.
- Added player CRUD endpoints:
  - `POST /players/`
  - `GET /players/`
  - `GET /players/{player_id}`
  - `PUT /players/{player_id}`
  - `DELETE /players/{player_id}`
- Added performance endpoints:
  - `POST /performances/`
  - `GET /performances/`
- Added a proper React frontend using Vite.
- Removed the Streamlit frontend path and removed `streamlit` from Python dependencies.
- Added a React dashboard with:
  - roster summary cards
  - searchable player table
  - add-player form
  - performance logging form
  - delete confirmation modal
  - API connection status and toast messages
- Added pytest coverage for basic player creation and retrieval.
- Cleaned generated files such as logs, cache folders, local database output, `node_modules`, and React build output.

## Project Structure

```text
.
├── app/
│   ├── api/              # FastAPI routers
│   ├── core/             # App settings
│   ├── db/               # SQLAlchemy engine/session setup
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic request/response models
│   └── main.py           # FastAPI app entrypoint
├── alembic/              # Database migration files
├── frontend/             # React + Vite frontend
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── tests/                # Pytest tests
├── docker-compose.yml    # Local PostgreSQL service
├── requirements.txt      # Python dependencies
└── pytest.ini
```

## Backend Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

By default, the app uses:

```text
sqlite:///./sports_analytics.db
```

To use another database, create a `.env` file and set:

```text
DATABASE_URL=postgresql+psycopg://sports_user:sports_password@localhost:5432/sports_analytics
```

## Optional PostgreSQL

Start PostgreSQL with Docker Compose:

```powershell
docker compose up -d
```

The provided service uses:

```text
POSTGRES_USER=sports_user
POSTGRES_PASSWORD=sports_password
POSTGRES_DB=sports_analytics
PORT=5432
```

## Frontend Setup

Install frontend dependencies:

```powershell
cd frontend
npm install
```

Run the React development server:

```powershell
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/players` and `/performances` to `http://localhost:8000`, so keep the FastAPI server running while using the React app.

## Production Frontend Build

Build the React app:

```powershell
cd frontend
npm run build
```

FastAPI is configured to serve the built frontend from:

```text
frontend/dist
```

After building, open:

```text
http://127.0.0.1:8000
```

## Run Tests

```powershell
.\venv\Scripts\python.exe -m pytest
```

Current test coverage checks basic player creation and retrieval with an in-memory SQLite database.

## Notes

- `node_modules`, `frontend/dist`, logs, test cache, and local database files are generated artifacts and are ignored.
- `frontend/package-lock.json` is kept so frontend installs are reproducible.
- The current frontend is React only; Streamlit is no longer part of the project.
