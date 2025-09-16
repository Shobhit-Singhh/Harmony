# app/main.py

from fastapi import FastAPI
from app.core.config import Base, engine
from app.api import user_routes
from app.models import user_models

app = FastAPI(title="Harmony API")

Base.metadata.create_all(bind=engine)

app.include_router(user_routes.router, prefix="/api")