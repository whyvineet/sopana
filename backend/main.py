from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SOPĀNA",
    description="AI-Powered Personalized Learning Path Recommender",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "service": "SOPĀNA API"}

@app.get("/")
def main():
    return {"message": "Hello World"}
