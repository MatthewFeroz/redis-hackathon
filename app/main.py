"""
FastAPI application entry point.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.redis_client import close_redis, get_redis, seed_faq_vectors
from app.routes_chat import router as chat_router
from app.routes_plumber import router as plumber_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await get_redis()
    await r.ping()
    print("✓ Redis connected")
    await seed_faq_vectors()
    print("✓ FAQ vectors seeded")
    yield
    await close_redis()
    print("✓ Redis disconnected")


app = FastAPI(title="Plumbly", version="1.0.0", lifespan=lifespan)

app.include_router(chat_router)
app.include_router(plumber_router)

# Mount SvelteKit build assets if available
sveltekit_app_dir = os.path.join("dashboard-app", "build", "_app")
if os.path.isdir(sveltekit_app_dir):
    app.mount("/_app", StaticFiles(directory=sveltekit_app_dir), name="sveltekit")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health():
    r = await get_redis()
    await r.ping()
    return {"status": "healthy", "redis": "connected"}
