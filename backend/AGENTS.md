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
| Package mgr    | uv (pyproject.toml + uv.lock)           |
| Linting        | ruff (check + format, replaces black/isort) |
| Testing        | pytest + pytest-asyncio + httpx         |

## Project layout

```
src/
├── main.py              # FastAPI app factory, router mounts
├── config.py            # Global BaseSettings (DATABASE_URL, ENVIRONMENT, CORS_ORIGINS)
├── constants.py         # Shared enums (Environment: prod | dev)
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
│   ├── schemas.py       # PostBase, PostCreate, PostUpdate (tags: list[str] | None), PostResponse (tags: list[str]), PaginatedPosts
│   ├── router.py        # Public: GET /posts/ (paginated, published), GET /posts/slug/{slug}, GET /posts/{post_id}
│   ├── admin_router.py  # Admin: CRUD on /admin/posts/ (list, get, create, update, delete)
│   └── exceptions.py    # PostNotFound, PostSlugConflict
├── tags/                # Tag system (many-to-many with posts)
│   ├── models.py        # Tag ORM model + post_tags join table
│   ├── schemas.py       # TagResponse (id, name)
│   ├── router.py        # GET /admin/tags/?search= (prefix match, case-insensitive)
│   └── service.py       # resolve_tags() (create-or-lookup), set_post_tags() (replace associations)
└── scripts/             # Utility scripts
    └── create_admin.py  # CLI to create the admin user

tests/
├── __init__.py
├── conftest.py          # Fixtures: PostgreSQL test DB, session/clean setup
├── test_auth.py         # Auth: /auth/me, /auth/login, token flow
└── test_posts.py        # Posts: public list/get, admin CRUD, auth guards, validation
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
| GET    | `/`                         | Public   | Health check                             |
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
| GET    | `/admin/tags/?search=`      | Required | Search tags (prefix match, case-insensitive) |

> All `/admin/posts/` endpoints require auth but do **not** check ownership — any authenticated user can create, update, or delete any post. (TODO: add ownership guard if needed.)
>
> Public `/posts/` endpoints only return posts where `published=True`.
>
> Tag names are normalized: lowercased, trimmed, deduplicated. Responses return sorted `tags: list[str]`.

> All `/admin/posts/` endpoints require auth but do **not** check ownership — any authenticated user can create, update, or delete any post. (TODO: add ownership guard if needed.)
>
> Public `/posts/` endpoints only return posts where `published=True`.

## Running tests

Run backend tests from the `backend/` directory with `uv run` and the root `.env` file:

```bash
uv run --env-file ../.env pytest
```

To run a single test file:

```bash
uv run --env-file ../.env pytest tests/test_media.py
```

## Conventions

### Naming
- **Tables**: singular (`user`, `post`)
- **Columns**: `lower_case_snake`
- **Dates**: `_at` suffix for `datetime` (`created_at`, `updated_at`), `_date` suffix for `date`
- **PKs**: UUID (`uuid.uuid4` default, PostgreSQL `UUID` type)
- **Migrations**: `YYYY-MM-DD_slug` (set in `alembic.ini`)

### Dependencies
- `Annotated[T, Depends(...)]` form, never default-arg `Depends(...)`
- `DbSession = Annotated[AsyncSession, Depends(get_db)]` for DB access
- `CurrentUser = Annotated[User, Depends(get_current_user)]` for auth

### Pydantic
- `populate_by_name=True` on all response models
- `@field_serializer` for custom serialization (no `json_encoders`)
- `exclude_unset=True` on update schemas for partial updates

### Errors
- Domain-specific exceptions in `{domain}/exceptions.py`
- DB integrity errors caught in router → `HTTPException` with proper status
- `IntegrityError` → rollback + 409 conflict

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
| `CORS_ORIGINS`        | `src.config`  | No       | `["http://localhost:3000", "https://blog.whoisrgj.com"]` | Allowed CORS origins |


## TODO / open questions

- [ ] Post ownership: should only the post creator be able to update/delete?
- [ ] Refresh tokens: currently single-token flow; add refresh if session > 60min needed
- [ ] Password reset flow
- [ ] Rate limiting on `/auth/login`
- [ ] Deployment target (Docker? cloud provider?)
