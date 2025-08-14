# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.responses import Response

from app.core.config import settings
from app.routers.plots import router as plots_router
from app.routers.beds import router as beds_router
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

# Add explicit headers for static file responses (WebGL-friendly)
@app.middleware("http")
async def add_file_headers(request: Request, call_next):
    response: Response = await call_next(request)
    if request.url.path.startswith("/files/"):
        # CORS and cross-origin resource policy for WebGL textures
        origin = request.headers.get("Origin")
        response.headers.setdefault("Access-Control-Allow-Origin", origin or origins[0])
        response.headers.setdefault("Cross-Origin-Resource-Policy", "cross-origin")
        # Helpful for range-based clients (OpenLayers GeoTIFF)
        response.headers.setdefault("Accept-Ranges", "bytes")
        # Reduce caching surprises in dev
        response.headers.setdefault("Cache-Control", "no-store")
    return response

# Serve GeoTIFF files
app.mount("/files", StaticFiles(directory=settings.files_dir), name="files")

@app.on_event("startup")
async def on_startup():
    await init_indexes()

@app.get("/health")
async def health():
    return {"ok": True}

# API routers
app.include_router(plots_router)
app.include_router(beds_router)
