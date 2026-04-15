from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.database import engine, Base
from app.routers import auth, users, goals, schedule, ai, subscription

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TimeMaster API",
    description="Vaqt menejment ilovasi — AI yordamida kun tartibi va maslahat",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(schedule.router)
app.include_router(ai.router)
app.include_router(subscription.router)

@app.get("/")
def root():
    return {"app": "TimeMaster", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/demo")
def demo():
    demo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo.html")
    return FileResponse(demo_path, media_type="text/html")

@app.get("/manifest.json")
def manifest():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "manifest.json")
    return FileResponse(path, media_type="application/manifest+json")

@app.get("/sw.js")
def sw():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sw.js")
    return FileResponse(path, media_type="application/javascript")
