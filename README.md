# Sports Analytics System

A sports team selection and performance analytics project with a FastAPI backend and a React frontend.

The project currently supports player roster management and performance record logging. The backend exposes REST APIs, stores data with SQLAlchemy, and defaults to SQLite for local development. A PostgreSQL service is available through Docker Compose.

## What Has Been Done So Far

- Built a FastAPI backend with player and performance routes.
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
- Replaced the Streamlit frontend with a proper React + Vite frontend.
- Added a React dashboard with roster summary cards, searchable player table, player registration, performance logging, delete confirmation, API status, and toast messages.
- Added a mock data seed script for local SQLite or PostgreSQL.
- Added pytest coverage for basic player creation and retrieval.
- Cleaned generated files such as logs, cache folders, local database output, `node_modules`, and React build output.

## Project Structure

```text
.
|-- app/
|   |-- api/              # FastAPI routers
|   |-- core/             # App settings and security
|   |-- db/               # SQLAlchemy engine/session setup
|   |-- ml/               # Machine learning models and predictors
|   |-- models/           # SQLAlchemy models
|   |-- schemas/          # Pydantic request/response models
|   |-- services/         # Business logic layer
|   |-- deps.py           # Dependency injection (Auth/DB)
|   `-- main.py           # FastAPI app entrypoint
|-- alembic/              # Database migration files
|-- frontend/             # React + Vite frontend
|-- scripts/
|   |-- seed_mock_data.py # Adds mock players and performance records
|   `-- train_model.py    # Trains the ML selection model
|-- tests/                # Pytest tests
|-- .env.example          # PostgreSQL environment example
|-- docker-compose.yml    # Local PostgreSQL service
|-- requirements.txt      # Python dependencies
`-- pytest.ini
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

## Frontend Setup

Install frontend dependencies:

```powershell
cd frontend
npm install
```

The easiest way to run the full app on Windows is from the project root:

```powershell
cd D:\SPORTS_EL
.\scripts\start_dev.ps1
```

This starts FastAPI on port `8000`, waits for `/health`, then starts the React development server on port `5173`.

If you prefer separate terminals, run the backend first:

```powershell
cd D:\SPORTS_EL
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then run the React development server:

```powershell
cd D:\SPORTS_EL\frontend
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:5173
```

Keep the FastAPI server running while using the React app. The Vite dev server proxies `/players` and `/performances` to `http://127.0.0.1:8000`.

If you see Vite proxy errors like `ECONNREFUSED`, the frontend is running but the backend is not reachable. Start the backend in another terminal:

```powershell
cd D:\SPORTS_EL
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

You can confirm the backend is up with:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
```

## Database Requirements

The app needs one of these database options:

- SQLite for quick local development. This is the default and creates `sports_analytics.db`.
- PostgreSQL for shared/team setup. Use the Docker Compose service in this repo.

Required PostgreSQL values:

```text
POSTGRES_USER=sports_user
POSTGRES_PASSWORD=sports_password
POSTGRES_DB=sports_analytics
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

FastAPI reads the database connection from `DATABASE_URL`. Copy the example file:

```powershell
Copy-Item .env.example .env
```

The PostgreSQL `DATABASE_URL` should be:

```text
DATABASE_URL=postgresql+psycopg://sports_user:sports_password@127.0.0.1:5432/sports_analytics
```

Start PostgreSQL:

```powershell
docker compose up -d
```

Then start the backend. Tables are created automatically on startup by `Base.metadata.create_all(bind=engine)`.

## Mock Player Data

After PostgreSQL is running and `.env` contains the PostgreSQL `DATABASE_URL`, seed mock players and performance records:

```powershell
cd D:\SPORTS_EL
.\venv\Scripts\Activate.ps1
python -m scripts.seed_mock_data
```

This adds sample data for:

- Lionel Messi
- Aitana Bonmati
- Virat Kohli
- LeBron James
- Harmanpreet Singh
- Zach Hyman

The seed script is idempotent for player name and team. Running it again will not duplicate those players or their first performance records.

Your teammate needs:

- Python dependencies installed from `requirements.txt`
- PostgreSQL running on port `5432`
- `.env` configured with `DATABASE_URL`
- backend running on `http://127.0.0.1:8000`
- frontend running on `http://127.0.0.1:5173`
- mock data loaded with `python -m scripts.seed_mock_data`

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

## Environment Variables

In addition to database credentials, you should configure the following security settings in your `.env` file:
- `SECRET_KEY`: Used for signing JWT tokens. Change this to a random secret string in production.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default 30).

## API Reference

### Auth

**Register**
```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"username":"test","email":"test@test.com","password":"test123"}'
```

**Login**
```bash
curl -X POST http://localhost:8000/auth/login -d "username=test&password=test123"
```

### Selection

**Generate a Team**
```bash
curl -X POST http://localhost:8000/selection -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"sport":"Football","team_size":4,"position_limits":{"GK":1,"DEF":1,"MID":1,"FWD":1}}'
```

### Analytics

**Get Player Metrics**
```bash
curl http://localhost:8000/players/1/metrics
```

**View Leaderboard**
```bash
curl "http://localhost:8000/analytics/leaderboard?metric=goals&sport=Football&top_n=5"
```

