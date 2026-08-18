# SOPĀNA

**Personalized Learning, One Step at a Time.**

## Tech Stack

### Frontend

* React.js
* Vite
* JavaScript
* Tailwind CSS

### Backend

* Python 3.11
* FastAPI
* `uv`

---

## Project Structure

```text
.
├── frontend/
└── backend/
```

The frontend and backend are maintained as separate applications within the repository.

---

## Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend is built using React, Vite, and Tailwind CSS.

---

## Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Synchronize the Python environment and dependencies:

```bash
uv sync
```

Start the FastAPI development server:

```bash
uv run fastapi dev
```

FastAPI will start the development server using the application's configured entry point.

---

## Environment Variables

The frontend uses an environment variable to determine the FastAPI backend URL.

Create a `.env` file inside the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

This variable is used by the frontend when communicating with the backend.

### Important

Do not commit `.env` files to Git if they contain secrets or environment-specific configuration.

Keep only non-sensitive configuration values in `.env.example`.

---

## Frontend–Backend Connectivity

The frontend currently performs a basic connectivity check against the FastAPI backend.

The backend exposes:

```http
GET /api/v1/health
```

The frontend uses:

```text
VITE_API_BASE_URL
```

to construct the request URL.

Expected response:

```json
{
  "status": "ok",
  "service": "SOPĀNA API"
}
```

This verifies that the React frontend can successfully communicate with the FastAPI backend.

---

## Running Both Applications

Run the backend in one terminal:

```bash
cd backend
uv run fastapi dev
```

Run the frontend in another terminal:

```bash
cd frontend
npm run dev
```

Once both servers are running, open the frontend URL provided by Vite.

The SOPĀNA interface should indicate whether the backend is connected successfully.
