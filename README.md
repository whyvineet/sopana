# SOPĀNA

SOPĀNA is a conversational AI learning advisor that builds personalized learning paths based on a learner's goals.

## Prerequisites

- **Python**: 3.11 or higher
- **uv**: Latest version (fast Python package installer)
- **Node.js**: v18 or higher
- **npm**: v9 or higher

---

## Setup & Installation

The project is split into a Python FastAPI backend and a React Vite frontend. You will need to run both concurrently in separate terminal windows.

### 1. Backend Setup

The backend handles all AI orchestration and API routes.

```bash
cd backend
cp .env.example .env
```

**Configure Environment Variables:**
Open `backend/.env` and add your OpenRouter API key. This is the only strictly required key to run the application locally (it will use in-memory storage).

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**Install and Run:**
```bash
# Install dependencies
uv sync

# Start the FastAPI development server
uv run fastapi dev
```
The backend API will be available at: `http://localhost:8000`

### 2. Frontend Setup

The frontend is a React application built with Vite.

```bash
cd frontend
cp .env.example .env
```

**Configure Environment Variables:**
Open `frontend/.env` and ensure it points to your local backend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

**Install and Run:**
```bash
# Install dependencies
npm install

# Start the Vite development server
npm run dev
```
The frontend UI will be available at: `http://localhost:5173`

---

## Optional: Supabase Configuration

By default, SOPĀNA runs entirely in-memory. Sessions will be lost when the backend restarts, and user authentication will be disabled. 

To enable session persistence and authentication, configure a Supabase project and add the following to `backend/.env`:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_SECRET_KEY=your_supabase_service_role_key
SUPABASE_JWKS_URL=your_supabase_jwks_url
```