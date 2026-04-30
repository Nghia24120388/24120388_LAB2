from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import auth, map, poi
from app.core.firebase_config import initialize_firebase

app = FastAPI(
    title="OpenStreetMap API",
    description="A Google Maps-like application using OpenStreetMap APIs",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if os.path.exists("../frontend"):
    app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(map.router, prefix="/map", tags=["map"])
app.include_router(poi.router, prefix="/poi", tags=["poi"])

@app.get("/")
async def root():
    return {"message": "OpenStreetMap API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "OpenStreetMap API"}

@app.on_event("startup")
async def startup_event():
    initialize_firebase()
