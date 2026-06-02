# Travels Feature — Design Decisions & Implementation Plan

Created: 2026-05-26

## Overview

A showcase page displaying visited and bucketlist countries via an interactive SVG world map, with badge lists categorized by continent. An admin settings page for managing the lists.

---

## Backend Design Decisions

### Database

- **Travel model**: `country_code` (unique constraint) + `status` (VARCHAR with CHECK)
- **No PostgreSQL ENUM** — matches project conventions (no DB enums exist)
- **Check constraint**: `status IN ('visited', 'bucketlist')`
- **Default status**: `bucketlist`
- **Additional columns**: `id` (UUID PK), `created_at`, `updated_at` (auto-timestamps)

```
travel
  id: UUID PK
  country_code: String(2), unique, not null
  status: String(20), CHECK IN ('visited', 'bucketlist')
  created_at: datetime (auto)
  updated_at: datetime (auto)
```

### Module Structure

```
src/travels/
  __init__.py       → exports resolve_travels
  models.py         → Travel ORM model
  schemas.py        → Pydantic schemas
  router.py         → API endpoints (public + admin)
  service.py        → business logic helpers
  exceptions.py     → TravelNotFound, TravelConflict
```

### API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/travels` | None | Returns `{ visited: string[], bucketlist: string[] }` |
| POST | `/admin/travels` | Bearer token | Batch replace: `{ visited: string[], bucketlist: string[] }` |
| DELETE | `/admin/travels/{code}` | Bearer token | Remove country |

> **TODO (cleanup):** DELETE endpoint is not used by the admin page — the batch replace handles removals. Consider removing it later if no other consumer needs it. Keeping it for now as a convenience/utility endpoint (single removal without fetching full state).

**Batch replace semantics**: Backend receives full desired state, diffs against DB, applies INSERT/DELETE/UPDATE as needed. One request, atomic.

- Country codes normalised: uppercased, trimmed, deduplicated
- Lists sorted alphabetically in the response

### Schema Conventions

- `TravelResponse`: `id` (UUID), `country_code` (str), `status` (str), `created_at`, `updated_at` (ISO 8601 UTC)
- `TravelsResponse` (public): `visited: list[str]`, `bucketlist: list[str]`
- `TravelsBatchCreate` (admin): `visited: list[str]`, `bucketlist: list[str]`

### Router Registration

- `main.py`: include `travels_router` at `/travels` prefix and `admin_router` at `/admin/travels` prefix

### Migration

- Auto-generated with Alembic: `alembic revision --autogenerate`
- Follows existing `YYYY-MM-DD_<description>` naming: `2026-05-26_add_travels_table.py`
- CHECK constraint added manually (Alembic didn't auto-detect it)

## Implementation Notes

✅ **All backend files implemented** (2026-05-26):

| File | Status |
|------|--------|
| `src/travels/__init__.py` | ✅ |
| `src/travels/models.py` | ✅ |
| `src/travels/exceptions.py` | ✅ (added — follows project convention) |
| `src/travels/schemas.py` | ✅ |
| `src/travels/service.py` | ✅ |
| `src/travels/router.py` | ✅ |
| `src/main.py` | ✅ (updated) |
| `migrations/env.py` | ✅ (updated — added missing `tags` model import) |
| `migrations/versions/2026-05-26_add_travels_table.py` | ✅ |

**Deviation from plan**: Created `exceptions.py` as a separate file (not in original plan) to match the project's `posts/exceptions.py` convention.

**Bonus fix**: `migrations/env.py` was missing imports for `tags` models, causing Alembic to incorrectly detect `tag` and `post_tags` tables as "removed". Added the missing imports so autogenerate works correctly for all domains.

**Pre-migration required**: Run `alembic upgrade head` before frontend can call the API.

### Bug Fixes (discovered during testing)

| Bug | File | Fix |
|-----|------|-----|
| `DELETE /admin/travels/{code}` used `db.get(Travel, code)` treating `country_code` as UUID PK | `src/travels/router.py` | Query by `country_code` column: `select(Travel).where(Travel.country_code == code)` |
| `batch_replace_travels` only fetched existing records in `all_codes`, so stale records outside that set were never deleted | `src/travels/service.py` | Fetch ALL travels: `select(Travel)` so stale ones are caught in `codes_to_delete` |

### Frontend Bug Fixes (post-implementation)

| Bug | File | Fix |
|-----|------|-----|
| `TravelsMap.tsx` used canvas context with `geoPath()` — paths rendered to canvas, not returned as strings; all 177 features skipped | `src/components/travels/TravelsMap.tsx` | Pass no context to `geoPath(projection)` so it returns SVG path `d` strings |
| SVG `<path>` elements used `setAttribute("fill", "var(--color-primary)")` — CSS custom properties don't resolve in SVG presentation attributes; paths invisible | `src/components/travels/TravelsMap.tsx` | Use `pathEl.style.fill = "var(--color-primary)"` (inline styles resolve CSS variables) |
| `topojson-client` `feature()` return type mismatch — TS inferred `Feature<Point>` instead of `FeatureCollection` | `src/components/travels/TravelsMap.tsx` | Cast to `as any` (runtime confirmed correct `FeatureCollection` with 177 features) |
| Map feature IDs are UN M49 numeric codes (e.g. `840`), not ISO alpha-2 codes (e.g. `US`) — `visited`/`bucketlist` arrays use alpha-2, so no matches | `src/components/travels/TravelsMap.tsx`, `src/lib/countries.ts` | Added `M49_TO_ALPHA2` mapping + `m49ToAlpha2()` helper; map feature IDs through it before checking against visited/bucketlist lists |
| Map hover tooltip uses emoji for country flag — regional indicator symbols render as initials | `src/components/travels/TravelsMap.tsx` | Replaced `codeToFlag()` with `<i className="fi fi-{code}" />` flag-icons SVG; tooltip state stores `code` + `name` separately for rendering |
| Hover tooltip crashes with `Cannot read properties of undefined (reading 'offsetX')` — `handleMouseMove` accessed `e.nativeEvent.offsetX` but native DOM events have `offsetX` directly, not under `nativeEvent` | `src/components/travels/TravelsMap.tsx` | Changed `handleMouseMove` param from `React.MouseEvent` to `MouseEvent`; access `e.offsetX`/`e.offsetY` directly |
| Bucketlist countries invisible — `--color-accent` resolves to same value as `--muted` in both light/dark mode (e.g. light: both `oklch(0.97 0 0)`) | `src/components/travels/TravelsMap.tsx` | Use `color-mix(in oklch, var(--color-primary) 35%, transparent)` for bucketlist fill (semi-transparent primary adapts to both modes) |
| Flags show as country initials (e.g. "US") instead of flag emojis — regional indicator symbols need system emoji fonts that aren't available | `src/lib/countries.ts`, `src/components/travels/TravelsBadges.tsx`, `src/components/ui/combobox.tsx` | Replaced emoji-based flags with `flag-icons` (SVG-based). `TravelsBadges` renders `<span className="fi fi-{code}" />`, combobox labels use `<i class="fi fi-{code}"></i>` via `dangerouslySetInnerHTML` |

---

## Frontend Implementation Notes

✅ **All frontend files implemented** (2026-05-26):

| File | Status |
|------|--------|
| `src/lib/countries.ts` | ✅ Country lookup table (~250 ISO 3166-1 alpha-2 codes), sorted country list helper (flags via flag-icons) |
| `src/lib/api.ts` | ✅ `TravelsResponse` interface, `useTravels()` SWR hook, `saveTravels()`, `deleteTravel()` |
| `src/components/travels/TravelsMap.tsx` | ✅ d3 Natural Earth projection, world-atlas 110m TopoJSON → GeoJSON, hover tooltips, CSS variable colors |
| `src/components/travels/TravelsBadges.tsx` | ✅ Continent-grouped badges, sorted by count descending, empty continents skipped, alphabetical within continent |
| `src/pages/TravelsPage.tsx` | ✅ Public page: SWR fetch, loading/error states, conditional sections for visited/bucketlist |
| `src/pages/admin/TravelsSettingsPage.tsx` | ✅ Two `MultiCombobox` components, auto-move between lists, save with `sonner` toasts, SWR invalidate |
| `package.json` | ✅ Added `world-atlas`, `d3-geo`, `topojson-client` + `@types/d3-geo`, `@types/topojson-client`, `@types/geojson` |

**Deviation from plan**:

- `TravelsMap.tsx` uses `feature()` from `topojson-client` directly (not `topojson.feature`) — matches the package's actual export structure.
- `TravelsMap.tsx` passes no context to `geoPath(projection)` (not a canvas) so it returns SVG path `d` strings for each feature.
- `TravelsBadges.tsx` uses `Map<string, string[]>` instead of `Record<string, string[]>` to avoid TypeScript narrowing issues with index access.
- `TravelsPage.tsx` conditionally renders visited/bucketlist sections (only shows sections that have countries).

**Implementation notes**:

- Country codes in `COUNTRIES` include all ISO 3166-1 alpha-2 codes plus territories (~250 total). Flags are rendered via `flag-icons` CSS classes (`fi fi-{code}`) for reliable SVG rendering across all systems.
- The map uses `world-atlas` 110m resolution (low res, ~50KB gzipped) with Natural Earth projection for a clean, stylized look.
- `world-atlas` feature IDs are UN M49 numeric codes (e.g. `840`), not ISO alpha-2 codes. A `M49_TO_ALPHA2` mapping in `countries.ts` converts them before matching against travels data.
- Map colors use CSS variables (`--color-primary`, `--color-accent`, `--muted`, `--muted-foreground`, `--border`) for dark mode awareness.
- The admin page's `MultiCombobox` components share the same static options (all countries) loaded at component mount — no search API needed for countries.
- Auto-move behavior: selecting a country in one list automatically removes it from the other list, preventing duplicates.
- Save triggers `saveTravels()` (batch replace) then calls `mutate()` to invalidate the SWR cache and refetch.

### Type Declarations

Three `@types/*` packages were installed to satisfy strict TypeScript:

| Package | Purpose |
|---------|--------|
| `@types/d3-geo` | d3-geo projection and path types |
| `@types/topojson-client` | topojson-client function types |
| `@types/geojson` | GeoJSON geometry/feature types |

The `world-atlas` JSON shape doesn't perfectly match `topojson-client`'s expected `Topology` type (the `objects.countries.geometries` array contains mixed `MultiLineString` and `Polygon` types), so the map component uses `as any` casts for the world data loading — this is runtime-safe since `topojson.feature()` handles the shape correctly.

### Test Results

**28 tests** covering all three endpoints, created in `tests/test_travels.py`:

| Category | Tests | Coverage |
|----------|-------|----------|
| **GET /travels** (public) | 6 | Empty response, visited/bucketlist lists, sorting, many countries, no-auth required |
| **POST /admin/travels** (batch replace) | 12 | Empty lists, populating visited/bucketlist, both lists, deduplication, normalization, empty string handling, status replacement, stale removal, auth guards, non-standard codes, large batch (50), state replacement across calls |
| **DELETE /admin/travels/{code}** | 7 | Success, not found, auth guards, case-insensitive, whitespace trimming, doesn't affect other status |
| **Integration** | 1 | Full create → update → delete lifecycle |

All 28 tests pass. Full suite: **92 tests** (28 travels + 64 existing) — no regressions.

**Conftest changes**:
- Added `Travel` model import so `travel` table gets created
- Added `DELETE FROM travel` to `clean_db` fixture
- Made `clean_db` depend on `setup_db` for correct fixture ordering
- Added `follow_redirects=True` to httpx client (trailing slash redirects)

---

## Frontend Design Decisions

### Dependencies to Install

```
world-atlas       # TopoJSON world data (~50KB gzipped, 110m resolution)
d3-geo            # Projection + path generation
topojson-client   # TopoJSON → GeoJSON conversion
flag-icons        # SVG-based country flag icons
```

### Country Data Lookup

- **Static `COUNTRIES` object** in `src/lib/countries.ts`
- All ~250 ISO 3166-1 alpha-2 codes (including territories)
- Shape: `Record<string, { name: string; continent: string }>`
- **Flag icons via flag-icons**: ISO code → CSS class `fi fi-{code}` rendered as SVG (requires `flag-icons` package and CSS import)
- **Continent mapping**: static, no API dependency
- Country names in English only

```ts
// src/lib/countries.ts
export const COUNTRIES: Record<string, { name: string; continent: string }> = {
  FR: { name: "France", continent: "Europe" },
  JP: { name: "Japan", continent: "Asia" },
  // ... all 250+ codes
};

// Flag icons are now rendered via flag-icons CSS class: fi fi-{code.toLowerCase()}
// The codeToFlag helper is kept for compatibility but flags use flag-icons instead
```

### Public Page: TravelsPage

**Layout**:
```
┌─────────────────────────────────────┐
│  <h1>Travels</h1>                    │
│  (no subtitle)                      │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Interactive World Map         │  │
│  │  (Natural Earth, zoomable)    │  │
│  │  Visited = primary color       │  │
│  │  Bucketlist = accent color     │  │
│  │  Neither = muted color         │  │
│  │  Hover = subtle gray highlight │  │
│  │  Tooltip = card-style          │  │
│  │    "Country Name — Status"     │  │
│  └───────────────────────────────┘  │
│                                     │
│  ── Visited Countries ──            │
│  Europe                             │
│  [🇫🇷 France] [🇩🇪 Germany] ...     │
│  Asia                               │
│  [🇯🇵 Japan] [🇹🇭 Thailand] ...     │
│                                     │
│  ── Bucketlist Countries ──         │
│  (continents ordered by count,      │
│   empty continents skipped)         │
└─────────────────────────────────────┘
```

**Map specifications**:
- **Projection**: Natural Earth (`d3.geoNaturalEarth1`)
- **Data**: `world-atlas` 110m resolution (low res)
- **Colors**: CSS variables (`var(--color-primary)`, `var(--color-accent)`, `var(--muted)`) — dark mode aware
- **Borders**: thin strokes (0.5px)
- **Hover**: subtle gray highlight + card-style tooltip (follows cursor, smart positioning) — shows flag icon + country name + status
- **Zoom**: scroll/pinch only, no buttons
- **Padding**: 5-10% around edges
- **Response**: full width, `aspect-video` on mobile
- **Empty state**: map renders normally with no highlights

**Badge specifications**:
- **Custom pill** (not `<Badge>` component) — large, decorative
- Flag icon (via `flag-icons` CSS class) + country name (~16px), padding ~10px 20px
- Countries sorted alphabetically by name within each continent
- Continents ordered by country count (descending), empty continents skipped
- Simple heading per continent (no emoji): `<h3>Europe</h3>`

**Component structure**:
```
src/pages/TravelsPage.tsx       → coordinator, fetches data
src/components/travels/TravelsMap.tsx     → d3 SVG worldmap
src/components/travels/TravelsBadges.tsx  → continent-grouped badges
```

**Data fetching**:
- SWR on component mount (`useTravels()`)
- Default SWR caching (revalidate on focus/reconnect)
- No global state

### Admin Page: TravelsSettingsPage

**Layout**:
```
┌─────────────────────────────────────┐
│  <h1>Travels Settings</h1>          │
│                                     │
│  Countries I've visited (3)         │
│  ┌───────────────────────────────┐  │
│  │  [🇫🇷 France] [🇯🇵 Japan]     │  │
│  │  [Search countries…]          │  │
│  └───────────────────────────────┘  │
│                                     │
│  Countries I want to visit (2)      │
│  ┌───────────────────────────────┐  │
│  │  [🇧🇷 Brazil] [🇮🇸 Iceland]   │  │
│  │  [Search countries…]          │  │
│  └───────────────────────────────┘  │
│                                     │
│  [Save Travels]                     │
└─────────────────────────────────────┘
```

**Combobox specifications**:
- Two `MultiCombobox` components, stacked vertically
- Options: all countries loaded at mount (static, no search API)
- Label format: `<i class="fi fi-fr"></i> France` (SVG flag icon + name, rendered via `dangerouslySetInnerHTML`)
- Search: matches against both country name AND ISO code
- Empty state: "No countries found"
- **Auto-move**: selecting a country in one list removes it from the other
- **No "Clear All" button**

**Save behavior**:
- Single "Save Travels" button at bottom
- Sends batch replace: `{ visited: [...], bucketlist: [...] }`
- Loading state: disabled + "Saving…"
- Success: toast via `sonner` ("Travels saved!")
- Error: toast via `sonner`

**Auth**: handled by `AdminLayout` (redirects to `/login` if no/invalid token)

**Component structure**:
```
src/pages/admin/TravelsSettingsPage.tsx  → full admin page with form
```

### API Integration

```ts
// src/lib/api.ts additions

export interface TravelsResponse {
  visited: string[];
  bucketlist: string[];
}

// Public
export function useTravels() {
  return useSWR<TravelsResponse>(`${API_BASE}/travels`, fetcher);
}

// Admin
export function useAuthToken(): string | null {
  const [token] = useState(() => localStorage.getItem("token"));
  return token;
}

export async function saveTravels(token: string, data: {
  visited: string[];
  bucketlist: string[];
}): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/travels`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Failed to save travels: ${res.status} ${body}`);
  }
}

export async function deleteTravel(token: string, code: string): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/travels/${code}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    throw new Error(`Failed to delete travel: ${res.status}`);
  }
}
```

### Admin Page Data Flow

1. Mount: fetch current travels via SWR (`useAdminTravels()`)
2. Populate comboboxes with current countries
3. User adds/removes countries (local state, auto-move between lists)
4. User clicks "Save Travels"
5. Send batch replace to `POST /admin/travels`
6. On success: toast + SWR invalidate
7. On error: toast with error message

---

## File Structure

### Backend

```
backend/src/travels/
  __init__.py
  models.py
  schemas.py
  router.py
  service.py
backend/migrations/versions/YYYY-MM-DD_add_travels.py
backend/src/main.py  (add travels_router)
```

### Frontend

```
frontend/src/lib/countries.ts           # Country lookup + sorted country list helper (flags via flag-icons)
frontend/src/lib/api.ts                 # Travels API functions
frontend/src/pages/TravelsPage.tsx      # Public page
frontend/src/pages/admin/TravelsSettingsPage.tsx  # Admin page
frontend/src/components/travels/
  TravelsMap.tsx                        # d3 SVG worldmap
  TravelsBadges.tsx                     # Continent-grouped badges
frontend/package.json                   # Add d3-geo, topojson-client, world-atlas, flag-icons
```

---

## Implementation Order

1. ~~**Backend**: Travel model + migration~~ ✅
2. ~~**Backend**: Travels schemas + service~~ ✅
3. ~~**Backend**: Public + admin routers~~ ✅
4. ~~**Backend**: Register router in main.py~~ ✅
5. ~~**Backend**: Tests + bug fixes~~ ✅ (28 tests, all pass, 92 total)
6. ~~**Frontend**: `src/lib/countries.ts` (country lookup + flag generator)~~ ✅
7. ~~**Frontend**: Install d3 deps (`world-atlas`, `d3-geo`, `topojson-client`)~~ ✅
8. ~~**Frontend**: `TravelsMap.tsx` component (d3 SVG map)~~ ✅
9. ~~**Frontend**: `TravelsBadges.tsx` component~~ ✅
10. ~~**Frontend**: `TravelsPage.tsx` (public page, SWR fetch)~~ ✅
11. ~~**Frontend**: API functions in `api.ts`~~ ✅
12. ~~**Frontend**: `TravelsSettingsPage.tsx` (admin page, comboboxes, save)~~ ✅
13. ~~**Frontend**: Replace emoji flags with `flag-icons` (SVG-based)~~ ✅
14. ~~**Frontend**: Map tooltip flag icon → flag-icons (SVG-based)~~ ✅
