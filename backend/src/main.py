from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.config import settings
from src.media.admin_router import router as admin_media_router
from src.posts.admin_router import router as admin_posts_router
from src.posts.router import router as posts_router
from src.social_links.router import admin_router as admin_social_links_router
from src.social_links.router import router as social_links_router
from src.tags.router import router as tags_router
from src.travels.router import admin_router as admin_travels_router
from src.travels.router import router as travels_router

SHOW_DOCS_IN = {"dev"}
app_kwargs: dict = {"title": "whoisrgj.com API"}
if settings.ENVIRONMENT not in SHOW_DOCS_IN:
    app_kwargs["openapi_url"] = None

app = FastAPI(**app_kwargs)

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(admin_posts_router)
app.include_router(admin_media_router)
app.include_router(tags_router)
app.include_router(travels_router)
app.include_router(admin_travels_router)
app.include_router(social_links_router)
app.include_router(admin_social_links_router)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.get("/")
async def index():
    return "whoisrgj.com API"
