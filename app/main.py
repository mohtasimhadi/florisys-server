# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from app.core.config import settings
from app.routers.plots import router as plots_router
from app.services.plots import init_indexes

app = FastAPI(title="Florisys Backend")

origins = [str(o) for o in settings.cors_origins] or [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.mount("/files", StaticFiles(directory=settings.files_dir), name="files")

@app.on_event("startup")
async def on_startup():
    await init_indexes()

@app.get("/health")
async def health():
    return {"ok": True}

app.include_router(plots_router)
