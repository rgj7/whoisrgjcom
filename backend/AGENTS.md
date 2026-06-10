# whoisrgj.com Backend — AGENTS.md

Machine-readable project context for AI coding agents.

## Companion docs

- **[FASTAPI.md](./.agents/skills/fastapi/SKILL.md)** — FastAPI best practices, anti-patterns, async rules, testing patterns, and quick-reference table. Read before writing or modifying any route, dependency, schema, or test.
- **[pytest-patterns.md](./.agents/skills/pytest-patterns/SKILL.md)** — Python testing with pytest: fixtures, parametrization, mocking, test organization, coverage, and CI/CD patterns. Read before writing or modifying tests.

## Stack

| Layer          | Choice                                  |
|----------------|-----------------------------------------|
| Runtime        | Python 3.14                             |
| Framework      | FastAPI (async-first)                   |
| ORM            | SQLAlchemy 2.0 async (`AsyncSession`)   |
| Migrations     | Alembic (async template)                |
| Primary DB     | PostgreSQL (asyncpg)                    |
| Auth           | PyJWT (HS256), bcrypt for passwords     |
| Object storage | Google Cloud Storage via `google-cloud-storage` |
| Images         | Pillow → optimized WebP uploads         |
| Package mgr    | uv (pyproject.toml + uv.lock)           |
| Linting        | ruff (check + format, replaces black/isort) |
| Testing        | pytest + pytest-asyncio + httpx         |

## Project layout

```
src/
├── main.py              # FastAPI app, CORS, router mounts, /health
├── config.py            # BaseSettings (DB, environment, CORS, media/GCS config)
├── constants.py         # Environment enum (prod | dev)
├── models.py            # SQLAlchemy DeclarativeBase + naming convention
├── database.py          # Async engine, session factory, get_db dependency
├── auth/                # Authentication domain
│   ├── config.py        # AuthConfig (JWT_SECRET, JWT_ALG, JWT_EXP_MINUTES)
│   ├── models.py        # User ORM model
│   ├── schemas.py       # UserCreate, UserResponse, LoginRequest, LoginResponse
│   ├── service.py       # hash_password, verify_password, create_user, get_user_by_*
│   ├── dependencies.py  # get_current_user, CurrentUser alias, create_access_token
│   ├── auth_utils.py    # decode_token (PyJWT)
│   ├── exceptions.py    # InvalidCredentials, Unauthorized, Forbidden
│   └── router.py        # GET /auth/me, POST /auth/login
├── posts/               # Blog posts domain
│   ├── models.py        # Post ORM model (includes `tags` relationship)
│   ├── schemas.py       # PostCreate/PostUpdate accept `tags`; PostResponse returns sorted tags
│   ├── router.py        # Public published post reads
│   ├── admin_router.py  # Admin CRUD on /admin/posts/
│   └── exceptions.py    # PostNotFound, PostSlugConflict
├── tags/                # Tag system (many-to-many with posts)
│   ├── models.py        # Tag ORM model + post_tags join table
│   ├── schemas.py       # TagResponse (id, name)
│   ├── router.py        # GET /admin/tags/?search= (prefix match, case-insensitive)
│   └── service.py       # resolve_tags(), set_post_tags()
├── travels/             # Travel map domain
│   ├── models.py        # Travel ORM model (country_code + status)
│   ├── schemas.py       # TravelsResponse: {visited: string[], bucketlist: string[]}
│   ├── router.py        # Public GET /travels/, admin POST/DELETE
│   ├── service.py       # resolve_travels(), batch_replace_travels()
│   └── exceptions.py    # TravelNotFound
├── social_links/        # Public/admin social links domain
│   ├── models.py        # SocialLink ORM model
│   ├── schemas.py       # Batch replace payload and response models
│   ├── router.py        # Public GET /social-links/, admin POST /admin/social-links/
│   └── service.py       # resolve_social_links(), batch_replace_social_links()
├── media/               # Admin image upload/delete domain
│   ├── models.py        # Media ORM model (GCS object metadata)
│   ├── schemas.py       # MediaResponse (`url` aliases `public_url`)
│   ├── admin_router.py  # POST /admin/media/images, DELETE /admin/media/{id}
│   ├── service.py       # upload byte-limit validation + WebP optimization
│   ├── storage.py       # GCS client, public/CDN URL generation, object delete
│   └── exceptions.py    # Upload too large, unsupported media type, not found
└── scripts/
    └── create_admin.py  # CLI to create the admin user

tests/
├── conftest.py          # PostgreSQL test DB, session/clean setup, httpx client
├── test_auth.py         # Auth token flow
├── test_health.py       # /health
├── test_media.py        # Upload/delete, URL generation, validation
├── test_posts.py        # Public/admin post CRUD and auth guards
├── test_tags.py         # Tag search and post tag behavior
└── test_travels.py      # Public/admin travel behavior
```

## Auth flow

- **Login**: `POST /auth/login` → returns `{access_token, token_type: "bearer"}`
- **Current user**: `GET /auth/me` → returns `UserResponse` (requires auth)
- **Protected routes**: `Authorization: Bearer <token>` header → `HTTPBearer` scheme → `decode_token` → `get_user_by_id`
- **Token payload**: `{"sub": "<user_uuid>", "exp": <datetime>}`
- **Password hashing**: bcrypt with `gensalt()` (default rounds)
- **Token expiry**: configurable via `AUTH_JWT_EXP_MINUTES` (default 60)
- **Note**: No self-registration — users are created via `scripts/create_admin.py` CLI or directly in the DB.

## API surface

| Method | Path                        | Auth     | Description                              |
|--------|-----------------------------|----------|------------------------------------------|
| GET    | `/`                         | Public   | API index string                          |
| GET    | `/health`                   | Public   | Container health check (`{"status":"ok"}`) |
| GET    | `/auth/me`                  | Required | Get current user info                    |
| POST   | `/auth/login`               | Public   | Get JWT token                            |
| GET    | `/posts/`                   | Public   | List published posts (paginated, includes tags) |
| GET    | `/posts/slug/{slug}`        | Public   | Get published post by slug (includes tags) |
| GET    | `/posts/{post_id}`          | Public   | Get published post by UUID (includes tags) |
| GET    | `/admin/posts/`             | Required | List all posts (paginated, incl. drafts) |
| GET    | `/admin/posts/{post_id}`    | Required | Get post by UUID (any status)            |
| POST   | `/admin/posts/`             | Required | Create post (accepts `tags: string[]`)   |
| PUT    | `/admin/posts/{post_id}`    | Required | Update post (partial, optional `tags`)   |
| DELETE | `/admin/posts/{post_id}`    | Required | Delete post                              |
| GET    | `/admin/tags/?search=`      | Public*  | Search tags (prefix match, case-insensitive) |
| GET    | `/travels/`                 | Public   | Return `{visited, bucketlist}` country-code lists |
| POST   | `/admin/travels/`           | Required | Atomically replace all travel rows       |
| DELETE | `/admin/travels/{country_code}` | Required | Delete one travel country code       |
| GET    | `/social-links/`            | Public   | Return ordered public social links       |
| POST   | `/admin/social-links/`      | Required | Atomically replace all social links      |
| POST   | `/admin/media/images`       | Required | Upload image → optimized WebP in GCS + media row |
| DELETE | `/admin/media/{media_id}`   | Required | Delete media row + best-effort GCS object delete |

\* `GET /admin/tags/` currently has an `/admin` prefix but does not require auth in the router.

> All `/admin/posts/` endpoints require auth but do **not** check ownership — any authenticated user can create, update, or delete any post. (TODO: add ownership guard if needed.)
>
> Public `/posts/` endpoints only return posts where `published=True`.
>
> Tag names are normalized: lowercased, trimmed, deduplicated. Responses return sorted `tags: list[str]`.
>
> Travel country codes are uppercased/trimmed and returned alphabetically in `visited` and `bucketlist` lists.
>
> Social links are batch-replaced and returned ordered by `sort_order`.

## Media/image behavior

- Accepted source image formats: JPEG, PNG, WEBP. GIF and invalid images return 415.
- Uploads are read in 64 KiB chunks and capped by `MEDIA_MAX_UPLOAD_BYTES` (default 5 MiB); oversized uploads return 413.
- Images are EXIF-transposed, resized to max width `MEDIA_MAX_WIDTH` (default 1600), metadata-stripped, and saved as WebP (`image/webp`, quality 85, method 6).
- GCS object names use `media/posts/YYYY/MM/{uuid}.webp`.
- Public URLs default to `https://storage.googleapis.com/{bucket}/{object_name}`; set `MEDIA_PUBLIC_BASE_URL` for CDN/proxy URLs. Object names are URL-quoted in both modes.
- GCS client uses Application Default Credentials and requires `GCS_BUCKET_NAME` for uploads/deletes.
- Uploaded objects get `Cache-Control: public, max-age=31536000, immutable`.
- If DB commit fails after upload, the uploaded GCS object is deleted best-effort.
- Deleting media deletes the GCS object best-effort before deleting the row.

## Running tests

Run backend tests from the `backend/` directory with `uv run` and the root `.env.dev` file:

```bash
uv run --env-file ../.env.dev pytest
```

To run a single test file:

```bash
uv run --env-file ../.env.dev pytest tests/test_media.py
```

## Conventions

### Naming
- **Tables**: singular (`user`, `post`, `tag`, `travel`, `social_link`, `media`)
- **Columns**: `lower_case_snake`
- **Dates**: `_at` suffix for `datetime` (`created_at`, `updated_at`), `_date` suffix for `date`
- **PKs**: UUID (`uuid.uuid4` default, PostgreSQL `UUID` type)
- **Migrations**: `YYYY-MM-DD_slug` (set in `alembic.ini`)

### Dependencies
- `Annotated[T, Depends(...)]` form, never default-arg `Depends(...)`
- `DbSession = Annotated[AsyncSession, Depends(get_db)]` for DB access
- `CurrentUser = Annotated[User, Depends(get_current_user)]` for auth

### Pydantic
- `populate_by_name=True` / `from_attributes=True` on ORM-backed response models
- `@field_serializer` for custom serialization (no `json_encoders`)
- `exclude_unset=True` on update schemas for partial updates
- UUID response fields are serialized as strings; datetimes are serialized with UTC fallback when naive.

### Errors
- Domain-specific exceptions in `{domain}/exceptions.py`
- DB integrity errors caught in router → `HTTPException` with proper status
- `IntegrityError` → rollback + 409 conflict
- Media storage cleanup is best-effort and should not mask primary DB errors.

### Docs
- OpenAPI docs (`/docs`, `/redoc`) visible only in `dev` environment
- Disabled in `production` via `openapi_url = None`

## Config (env vars)

| Variable            | Source          | Required | Default       | Description                    |
|---------------------|-----------------|----------|---------------|--------------------------------|
| `DATABASE_URL`      | `src.config`    | Yes      | —             | Full async SQLAlchemy database URL |
| `ENVIRONMENT`       | `src.config`    | No       | `prod`        | `dev` or `prod`                |
| `AUTH_JWT_SECRET`   | `auth.config`   | Yes      | —             | JWT signing secret             |
| `AUTH_JWT_ALG`      | `auth.config`   | No       | `HS256`       | JWT algorithm                  |
| `AUTH_JWT_EXP_MINUTES` | `auth.config`| No       | `60`          | Token lifetime in minutes      |
| `CORS_ORIGINS`      | `src.config`    | No       | `[]`          | Allowed CORS origins           |
| `GCS_BUCKET_NAME`   | `src.config`    | For media upload/delete | `""` | GCS bucket for media objects |
| `MEDIA_PUBLIC_BASE_URL` | `src.config` | No       | `""`        | CDN/proxy base URL for returned media URLs |
| `MEDIA_MAX_UPLOAD_BYTES` | `src.config` | No      | `5242880`     | Max accepted upload size       |
| `MEDIA_MAX_WIDTH`   | `src.config`    | No       | `1600`        | Max optimized image width      |

## Migrations and deployment notes

- Alembic autogenerate imports every domain model in `migrations/env.py`; add new model imports there or migrations will miss new tables.
- The Docker image uses `backend/entrypoint.sh`, which runs `uv run alembic upgrade head` before starting `uvicorn src.main:app --host 0.0.0.0 --port 8000`.
- Production compose (`docker-compose-prod.yml`) runs the backend image `ghcr.io/rgj7/whoisrgjcom-backend:latest`, waits for Postgres health, exposes port 8000 internally, and Caddy depends on backend/frontend health.
- Backend health check in production uses `GET http://localhost:8000/health`.
- Production also includes `gcsproxy` for the media bucket; align `MEDIA_PUBLIC_BASE_URL` and CORS/proxy domains with the frontend/blog domain.

## TODO / open questions

- [ ] Post ownership: should only the post creator be able to update/delete?
- [ ] Refresh tokens: currently single-token flow; add refresh if session > 60min needed
- [ ] Password reset flow
- [ ] Rate limiting on `/auth/login`
- [ ] Consider whether `/admin/tags/` should require auth (currently public despite prefix)
- [ ] Decide canonical media URL path/domain for production (`MEDIA_PUBLIC_BASE_URL` vs raw GCS URL)
