# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Base, engine
from app.api import user_routes
from app.models import user_models

app = FastAPI(title="Harmony API")

# ✅ Add CORS middleware here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your frontend
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# DB setup
Base.metadata.create_all(bind=engine)

# Routes
app.include_router(user_routes.router, prefix="/api")
