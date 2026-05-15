from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.config import settings
from src.posts.router import router as posts_router

SHOW_DOCS_IN = {"dev"}
app_kwargs: dict = {"title": "whoisrgj.com API"}
if settings.ENVIRONMENT not in SHOW_DOCS_IN:
    app_kwargs["openapi_url"] = None

app = FastAPI(**app_kwargs)

app.include_router(auth_router)
app.include_router(posts_router)


@app.get("/")
async def index():
    return "whoisrgj.com API"
