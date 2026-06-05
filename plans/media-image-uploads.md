# Media Image Uploads Plan

## Goal

Add admin-only image uploads for blog posts. Uploaded images are validated and optimized by the FastAPI backend, stored in a public Google Cloud Storage bucket, tracked in Postgres, and returned to the TipTap editor as public URLs.

## Decisions Locked

- **Uploader access:** admin-only, authenticated with existing JWT bearer auth.
- **Storage:** Google Cloud Storage public bucket.
- **Upload flow:** browser → FastAPI → Pillow optimization → GCS → Postgres media row → TipTap image URL.
- **Serving:** public GCS URLs, not proxied through backend.
- **Endpoint:** `POST /admin/media/images`.
- **Request format:** `multipart/form-data` with field name `file`.
- **Response format:** structured media object containing `url` plus metadata.
- **Image processing:** inspect real image contents with Pillow; do not trust browser MIME alone.
- **Accepted inputs:** JPEG, PNG, WebP.
- **Rejected inputs:** GIF, SVG, all other types.
- **Max input size:** 5MB.
- **Output format:** optimized WebP only; do not store originals.
- **Resize:** max width 1600px, preserve aspect ratio.
- **Metadata stripping:** strip EXIF/metadata during conversion.
- **Bucket object path:** `media/posts/YYYY/MM/{uuid}.webp`.
- **Public URL v1:** `https://storage.googleapis.com/{bucket}/{object_name}`.
- **Cache-Control:** `public, max-age=31536000, immutable`.
- **DB source of truth:** create a dedicated `media` table.
- **Delete behavior:** no automatic deletion from editor removals; provide admin-only manual delete endpoint.
- **DB failure after upload:** attempt best-effort GCS object deletion, then return error.
- **Alt text:** not part of upload endpoint; belongs in TipTap image node attributes.
- **Bucket provisioning:** manual for v1.
- **Frontend v1 scope:** post editor upload only; no media library page yet.

## Backend Implementation Checklist

**Last completed step:** 10. Backend Tests

### 1. Dependencies ✅ Completed

Add backend dependencies in `backend/pyproject.toml`:

- `google-cloud-storage`
- `pillow`

Then update `backend/uv.lock` with `uv lock` or equivalent project workflow.

Completed changes:

- Added `google-cloud-storage` to `backend/pyproject.toml`.
- Added `pillow` to `backend/pyproject.toml`.
- Regenerated `backend/uv.lock` with `cd backend && uv lock`.

### 2. Configuration ✅ Completed

Extend `backend/src/config.py` with:

- `GCS_BUCKET_NAME: str`
- Optional constants/settings if desired:
  - `MEDIA_MAX_UPLOAD_BYTES = 5 * 1024 * 1024`
  - `MEDIA_MAX_WIDTH = 1600`

Deployment authentication approach:

- Backend runs on a Google Compute Engine VM.
- Prefer the VM's attached service account and Application Default Credentials over a downloadable JSON service account key.
- Do not mount `gcs-service-account.json` in production.
- Do not set `GOOGLE_APPLICATION_CREDENTIALS` in production.

Deployment environment variables:

```yaml
backend:
  environment:
    GCS_BUCKET_NAME: whoisrgjcom-media-prod
```

Completed changes:

- Added `GCS_BUCKET_NAME` to `backend/src/config.py`.
- Added `MEDIA_MAX_UPLOAD_BYTES = 5 * 1024 * 1024` to `backend/src/config.py`.
- Added `MEDIA_MAX_WIDTH = 1600` to `backend/src/config.py`.
- Added required `GCS_BUCKET_NAME` environment variable to the production backend service.

Production follow-up:

- Remove any production `gcs-service-account.json` volume mount from `docker-compose-prod.yml` if still present.
- Remove any production `GOOGLE_APPLICATION_CREDENTIALS` environment variable from `docker-compose-prod.yml` if still present.

### 3. Media Model ✅ Completed

Create `backend/src/media/models.py` with a `Media` SQLAlchemy model.

Suggested columns:

- `id UUID primary key`
- `object_name String(500), unique, nullable=False`
- `public_url String(1000), nullable=False`
- `content_type String(100), nullable=False` — should be `image/webp`
- `size_bytes Integer, nullable=False`
- `width Integer, nullable=False`
- `height Integer, nullable=False`
- `created_by UUID foreign key user.id, nullable=False`
- `created_at datetime server_default=func.now()`

Consider indexes on:

- `created_at`
- `created_by`

Completed changes:

- Created `backend/src/media/__init__.py`.
- Created `backend/src/media/models.py` with the `Media` SQLAlchemy model.
- Added unique `object_name`, public URL, WebP content type metadata, image dimensions, creator FK, and `created_at` fields.
- Added indexes for `created_at` and `created_by`.
- Verified the new model file with `cd backend && uv run ruff check src/media/models.py`.

### 4. Migration ✅ Completed

Create an Alembic migration for the `media` table.

Also ensure tests import the `Media` model so metadata creation includes it.

Completed changes:

- Created `backend/migrations/versions/2026-06-04_add_media_table.py`.
- Migration creates the `media` table, `created_by` foreign key, `object_name` unique constraint, and indexes on `created_at` and `created_by`.
- Updated `backend/migrations/env.py` to import `Media` so Alembic metadata sees the model.
- Updated `backend/tests/conftest.py` to import `Media` so test metadata creation includes the table.
- Updated test DB cleanup to delete `media` rows before `user` rows.
- Verified changed migration/test files with `cd backend && uv run ruff check migrations/versions/2026-06-04_add_media_table.py migrations/env.py tests/conftest.py`.

### 5. Schemas ✅ Completed

Create `backend/src/media/schemas.py`:

- `MediaResponse`
  - `id`
  - `url`
  - `object_name`
  - `content_type`
  - `size_bytes`
  - `width`
  - `height`
  - `created_at`

Use serializers consistent with existing schema style.

Completed changes:

- Created `backend/src/media/schemas.py`.
- Added `MediaResponse` with `id`, `url`, `object_name`, `content_type`, `size_bytes`, `width`, `height`, and `created_at`.
- Mapped ORM `public_url` to response field `url` with `Field(validation_alias="public_url")`.
- Added UUID and datetime serializers consistent with existing response schemas.
- Verified the schema with `cd backend && uv run ruff check src/media/schemas.py` and a small `MediaResponse.model_validate(...)` smoke test.

### 6. Image Processing Service ✅ Completed

Create `backend/src/media/service.py`.

Responsibilities:

1. Read uploaded bytes with size guard.
2. Open with Pillow.
3. Verify it is a valid image.
4. Confirm format is one of JPEG/PNG/WebP.
5. Normalize image mode for WebP output.
6. Resize if width exceeds 1600px.
7. Strip metadata by creating/saving a clean image.
8. Save as WebP to bytes.
9. Return optimized bytes plus width/height/size metadata.

Recommended errors:

- `413 Payload Too Large` for >5MB.
- `415 Unsupported Media Type` for unsupported/invalid image types.
- `400 Bad Request` for unreadable image data if not using `415`.

Completed changes:

- Created `backend/src/media/exceptions.py` with upload-specific HTTP exceptions.
- Created `backend/src/media/service.py`.
- Added chunked upload reading with a max-size guard using `settings.MEDIA_MAX_UPLOAD_BYTES`.
- Added Pillow validation that verifies real image contents and accepts only JPEG, PNG, and WebP.
- Added image normalization, EXIF orientation handling, max-width resize, metadata stripping, and WebP output.
- Added `OptimizedImage` return metadata containing bytes, content type, size, width, and height.
- Verified changed files with `cd backend && uv run ruff check src/media/service.py src/media/exceptions.py`.
- Smoke-tested PNG optimization to WebP and invalid SVG rejection.

### 7. GCS Storage Service ✅ Completed

In `backend/src/media/service.py` or `backend/src/media/storage.py`:

- Instantiate a GCS client using Application Default Credentials.
- Get bucket from `settings.GCS_BUCKET_NAME`.
- Upload optimized bytes to object name.
- Set:
  - `content_type="image/webp"`
  - `cache_control="public, max-age=31536000, immutable"`
- Return public URL:

```text
https://storage.googleapis.com/{bucket}/{object_name}
```

Also implement object delete helper for:

- DB rollback cleanup after failed insert.
- `DELETE /admin/media/{id}`.

Completed changes:

- Created `backend/src/media/storage.py`.
- Added cached GCS client creation using Application Default Credentials.
- Added configured bucket lookup via `settings.GCS_BUCKET_NAME`.
- Added `upload_image_object(...)` to upload optimized bytes with `content_type="image/webp"` and `Cache-Control: public, max-age=31536000, immutable`.
- Added `build_public_url(...)` for `https://storage.googleapis.com/{bucket}/{object_name}` public URLs.
- Added `delete_object(...)` for rollback cleanup and future manual delete endpoint support.
- Verified with `cd backend && uv run ruff check src/media/storage.py` and a public URL smoke test.

### 8. Router ✅ Completed

Create `backend/src/media/admin_router.py`.

Endpoints:

#### `POST /admin/media/images`

- Requires `CurrentUser`.
- Accepts `file: UploadFile = File(...)`.
- Optimizes image.
- Generates object name: `media/posts/YYYY/MM/{uuid}.webp`.
- Uploads to GCS.
- Inserts `Media` row.
- On DB failure, deletes uploaded GCS object best-effort.
- Returns `MediaResponse`.

#### `DELETE /admin/media/{id}`

- Requires `CurrentUser`.
- Loads media row.
- Deletes GCS object best-effort or fails loudly depending desired strictness.
- Deletes DB row.
- Returns `204 No Content`.

Optional later endpoint, not required for v1 UI:

#### `GET /admin/media`

- Paginated list for future media library.

Completed changes:

- Created `backend/src/media/admin_router.py`.
- Added `POST /admin/media/images` with `CurrentUser`, multipart `file`, image optimization, object name generation, GCS upload, media DB insert, and DB-failure GCS cleanup.
- Added `DELETE /admin/media/{media_id}` with `CurrentUser`, media lookup, best-effort GCS object deletion, and DB row deletion.
- Added `MediaNotFound` to `backend/src/media/exceptions.py`.
- Added object name generation in the format `media/posts/YYYY/MM/{uuid}.webp`.
- Verified changed files with `cd backend && uv run ruff check src/media/admin_router.py src/media/exceptions.py`.
- Smoke-tested router import and registered route paths with required test env vars.

### 9. Register Router ✅ Completed

Update `backend/src/main.py`:

```python
from src.media.admin_router import router as admin_media_router
...
app.include_router(admin_media_router)
```

Completed changes:

- Imported `admin_media_router` in `backend/src/main.py`.
- Registered the admin media router with `app.include_router(admin_media_router)`.
- Verified with `cd backend && uv run ruff check src/main.py`.
- Smoke-tested that `/admin/media/images` and `/admin/media/{media_id}` are present in the FastAPI app routes.

### 10. Backend Tests ✅ Completed

Add tests for:

- Unauthenticated upload returns 401/403.
- Non-image upload rejected.
- Unsupported image type rejected.
- Oversized upload rejected.
- Valid JPEG/PNG/WebP returns media object.
- Returned object has `image/webp` content type.
- DB row is created.
- Delete endpoint removes row and calls object delete.

Use mocking for GCS client/upload/delete so tests do not require real Google credentials.

Completed changes:

- Added `backend/tests/test_media.py` coverage for unauthenticated image uploads, invalid/non-image uploads, unsupported GIF uploads, oversized uploads, valid JPEG/PNG/WebP uploads, and media deletion.
- Mocked `upload_image_object(...)` and `delete_object(...)` in `src.media.admin_router` so tests do not require real Google credentials or a real GCS bucket.
- Verified valid uploads return a structured media object with public URL, object name, `image/webp` content type, optimized dimensions, size, and creation timestamp.
- Verified upload creates a matching `media` table row.
- Verified delete removes the `media` row and calls object deletion with the stored object name.
- Fixed the DB-row assertion to use SQLAlchemy Core mappings when selecting through `test_engine.connect()`.
- Verified with `cd backend && uv run --env-file ../.env pytest tests/test_media.py`.

## Frontend Implementation Checklist

### 1. API Types and Upload Function ✅ Completed

Update `frontend/src/lib/api.ts`:

```ts
export interface MediaUploadResponse {
  id: string;
  url: string;
  object_name: string;
  content_type: string;
  size_bytes: number;
  width: number;
  height: number;
  created_at: string;
}
```

Add:

```ts
export async function uploadPostImage(
  token: string,
  file: File,
  onProgress?: (event: { progress: number }) => void,
  signal?: AbortSignal,
): Promise<MediaUploadResponse>
```

Notes:

- `fetch` does not provide upload progress natively.
- For true upload progress, use `XMLHttpRequest`.
- Simpler v1 option: use `fetch`, emit basic progress states like 10% before request and 100% after response.
- If preserving TipTap progress UI matters, use XHR.

Completed changes:

- Added `MediaUploadResponse` to `frontend/src/lib/api.ts`.
- Added `UploadProgressEvent` to type basic upload progress callbacks.
- Added `uploadPostImage(...)` using `multipart/form-data` field `file`, bearer auth, abort signal forwarding, and basic `10%`/`100%` progress events around the `fetch` request.
- Verified with `cd frontend && bunx biome check src/lib/api.ts`.

### 2. Thread Auth Token to Editor ✅ Completed

Current flow:

- `CreatePostPage` / `EditPostPage` pass `authToken` to `PostForm`.
- `PostForm` does not pass it to `SimpleEditor` yet.

Update:

- `SimpleEditor` props to accept `authToken?: string`.
- `PostForm` passes `authToken={authToken}`.

Completed changes:

- Updated `SimpleEditor` to accept an optional `authToken` prop.
- Updated `PostForm` to pass its existing `authToken` prop into `SimpleEditor`.
- Verified with `cd frontend && bunx biome check src/components/tiptap-templates/simple/simple-editor.tsx src/pages/admin/PostForm.tsx`.

### 3. Replace Stub Upload Handler ✅ Completed

Current stub:

- `frontend/src/lib/tiptap-utils.ts`
- `handleImageUpload()` simulates upload and returns placeholder URL.

Options:

1. Replace `handleImageUpload` with an authenticated upload function that accepts token.
2. Keep utility generic and create an upload callback inside `SimpleEditor` that closes over `authToken`.

Recommended:

- Keep `handleImageUpload` as a helper factory or move real upload into `api.ts`.
- In `SimpleEditor`, configure `ImageUploadNode` with:

```ts
upload: async (file, onProgress, signal) => {
  if (!authToken) throw new Error("Not authenticated");
  const media = await uploadPostImage(authToken, file, onProgress, signal);
  return media.url;
}
```

Completed changes:

- Updated `SimpleEditor` to import `uploadPostImage(...)` from `frontend/src/lib/api.ts`.
- Replaced the `ImageUploadNode` stub `handleImageUpload` callback with an authenticated upload callback that closes over `authToken`.
- The upload callback now throws `Not authenticated` when no token is available, uploads the file through `POST /admin/media/images`, forwards progress and abort signal arguments, and returns the uploaded media URL to TipTap.
- Left the generic demo `handleImageUpload(...)` helper in `frontend/src/lib/tiptap-utils.ts` unused for now rather than removing shared template utility code.
- Verified with `cd frontend && bunx biome check src/components/tiptap-templates/simple/simple-editor.tsx`.

### 4. Frontend Validation ✅ Completed

Keep existing `MAX_FILE_SIZE = 5 * 1024 * 1024`.

Optionally restrict accept string to:

```ts
accept: "image/jpeg,image/png,image/webp"
```

Backend remains authoritative.

Completed changes:

- Kept the existing `MAX_FILE_SIZE = 5 * 1024 * 1024` limit in `frontend/src/lib/tiptap-utils.ts`.
- Restricted `ImageUploadNode` browser file selection to `image/jpeg,image/png,image/webp` in `frontend/src/components/tiptap-templates/simple/simple-editor.tsx`.
- Verified with `cd frontend && bunx biome check src/components/tiptap-templates/simple/simple-editor.tsx`.

### 5. User Feedback ✅ Completed

Use `sonner` toast notifications for image upload feedback.

Existing app support:

- `frontend/src/App.tsx` already renders `<Toaster />` from `sonner` near the root.
- Admin pages such as `frontend/src/pages/admin/SettingsPage.tsx` already use `toast.success(...)` and `toast.error(...)`.

Update `frontend/src/components/tiptap-templates/simple/simple-editor.tsx`:

- Import `toast` from `sonner`.
- Replace `onError: console.error(...)` with `toast.error(...)`.
- Optionally use `onSuccess` with `toast.success(...)` after the uploaded URL is inserted.
- Keep backend/API error messages visible where useful, but avoid exposing noisy implementation details if the error is not an `Error` instance.

Completed changes:

- Confirmed `frontend/src/App.tsx` already renders `<Toaster />` from `sonner`.
- Confirmed existing admin usage pattern in `frontend/src/pages/admin/SettingsPage.tsx`.
- Imported `toast` from `sonner` in `frontend/src/components/tiptap-templates/simple/simple-editor.tsx`.
- Replaced upload error console-only feedback with `toast.error(...)`.
- Added `toast.success("Image uploaded")` on upload success.
- Verified with `cd frontend && bunx biome check src/components/tiptap-templates/simple/simple-editor.tsx`.

## Deployment Checklist

### 1. Create GCS Bucket ✅ Completed

Manual setup in Google Cloud:

- Name: `whoisrgjcom-media-prod` or chosen bucket name.
- Location: choose appropriate region/multi-region.
- Public access: allow public reads for uploaded objects.
- Uniform bucket-level access: recommended.

Completed changes:

- Created GCS bucket `whoisrgjcom-media-prod`.

### 2. VM Service Account ✅ Completed

Use the Google Compute Engine VM's attached service account instead of a downloadable JSON key.

Recommended setup:

- Create or choose a dedicated service account, e.g. `whoisrgjcom-media-uploader`.
- Attach that service account to the Compute Engine VM running the backend.
- Grant least privilege on bucket `whoisrgjcom-media-prod`:
  - upload objects
  - delete objects
  - read object metadata if needed

A practical role may be `Storage Object Admin` scoped to the specific bucket.

Completed changes:

- Created/configured the VM service account for media uploads.
- Granted the service account `Storage Object Admin` access for GCS object operations.
- Attached the service account to the Google Compute Engine VM running the backend.
- Configured VM access scopes to allow Cloud API access while relying on IAM for permissions.

The backend should rely on Application Default Credentials via the GCE metadata server:

```py
from google.cloud import storage

client = storage.Client()
```

### 3. Avoid Service Account Keys ✅ Completed

Do not use a downloadable `.json` service account key for production on GCE.

- Do not generate a long-lived JSON key unless deploying outside Google Cloud.
- Do not mount `./secrets/gcs-service-account.json` into the backend container.
- Do not set `GOOGLE_APPLICATION_CREDENTIALS` in production.
- If a key was already created for this, delete/disable it in IAM after confirming VM service account auth works.

Completed changes:

- Confirmed production will use GCE metadata-server credentials instead of a downloadable JSON key.
- Confirmed no production service account JSON key is required for GCS uploads.

### 4. Docker Compose Prod ✅ Completed

Update `docker-compose-prod.yml` backend service:

- remove any GCS credential JSON volume mount
- remove any `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- keep/add `GCS_BUCKET_NAME`

Also update `.env.prod` with bucket name if using env interpolation.

Completed changes:

- Removed production GCS credential JSON volume mount.
- Removed production `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
- Confirmed production backend uses `GCS_BUCKET_NAME` for bucket selection.

### 5. Deploy

- Build/publish updated backend and frontend images.
- Pull on VM.
- Run Alembic migration.
- Restart compose stack.
- Test upload from admin editor.

## Implementation Decisions Made During Build

- **Upload progress:** use `fetch` for upload requests with approximate progress updates instead of `XMLHttpRequest` real upload progress.
  - Current behavior reports initial progress before the request and 100% after the response succeeds.
- **GCS IAM role:** use bucket-scoped `Storage Object Admin` for the VM service account in v1.
  - Production uses the GCE VM attached service account and Application Default Credentials via the metadata server.
  - Production does not use a downloadable JSON service account key.
- **Delete behavior:** `DELETE /admin/media/{id}` performs best-effort GCS object deletion and then removes the DB row.
  - GCS delete failures are swallowed so a missing/unreachable object does not block DB cleanup.
- **Media listing:** do not add `GET /admin/media` in v1.
  - Frontend v1 remains scoped to post editor upload only, with no media library page yet.

## Suggested v1 Acceptance Criteria

- Admin can upload JPEG/PNG/WebP from the TipTap editor.
- Uploaded image appears in the editor and persists in saved post JSON as a public URL.
- Public post page renders the uploaded image without requiring auth.
- Images in GCS are WebP, max width 1600px, and have long-lived immutable cache headers.
- Media metadata is stored in Postgres.
- Invalid, oversized, unsupported, or unauthenticated uploads are rejected.
