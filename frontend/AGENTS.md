# Frontend — Project Context

## Tech Stack

- **Runtime**: Bun (v1.3.13+) — serves as both bundler and dev server
- **Framework**: React 19 + TypeScript (strict mode)
- **Styling**: Tailwind CSS v4 + shadcn/ui (New York style, neutral base, CSS variables)
- **Routing**: React Router DOM v7
- **Data Fetching**: SWR (with 5s request timeout)
- **Rich Text Editor**: Tiptap v3 (starter-kit + multiple extensions) — see `.agents/skills/tiptap/SKILL.md` for guidance
- **Icons**: Lucide React
- **Animations**: motion (Framer Motion)
- **Build**: Custom `build.ts` via `Bun.build()` with `bun-plugin-tailwind`

## Architecture

### Monorepo structure

```
whoisrgjcom/
├── backend/          # FastAPI (Python 3.14+, SQLAlchemy, asyncpg)
├── frontend/         # This directory — React/Bun app
└── docker-compose.yml # PostgreSQL 17
```

The frontend is a **client-side SPA** served by Bun's static file server (`src/index.ts`). The backend runs separately on port 8000.

### Entry points

| File | Purpose |
|------|---------|
| `src/index.ts` | Bun dev/production server — serves `index.html` as catch-all, `/health` healthcheck |
| `src/frontend.tsx` | React entry — wraps `<App />` in `<BrowserRouter>` + `<StrictMode>` |
| `src/index.html` | HTML shell with `<div id="root">` |
| `build.ts` | Production build — scans `src/**/*.html` entrypoints, minifies, outputs to `dist/` |

### Routing (App.tsx)

```
/login                          → LoginPage
/dashboard                      → AdminLayout → DashboardPage
/dashboard/posts                → AdminLayout → PostsPage
/dashboard/posts/new            → AdminLayout → CreatePostPage
/dashboard/posts/:id/edit       → AdminLayout → EditPostPage
/dashboard/settings             → AdminLayout → SettingsPage
/                               → HomePage
/travels                        → TravelsPage
/dev                            → DevPage
/gaming                         → GamingPage
/posts/:slug                    → PostPage
/* (catch-all)                  → AnimatedNavbar + ThemeToggle + nested Routes
```

Admin routes are protected: `AdminLayout` checks for a `token` in localStorage and validates it via `GET /auth/me`.

### API layer (`src/lib/api.ts`)

- **Base URL**: `http://<hostname>:8000` (port 8000, configurable via `API_BASE`)
- **Auth**: Bearer token stored in localStorage (`token` key) after login
- **Data fetching**: All SWR hooks use `revalidateOnFocus: false`, `dedupingInterval: 0`
- **Timeout**: 5s per request via AbortController

**Key API functions:**
- `login(username, password)` → `{ access_token, token_type }`
- `getMe(token)` → `CurrentUser`
- `usePosts(page, limit)` → `PaginatedPosts` (public)
- `useAdminPosts(page, limit)` → `PaginatedPosts` (admin)
- `usePostBySlug(slug)` → `Post`
- `usePostById(id)` → `Post`
- `useAdminPostById(id)` → `Post`
- `deleteAdminPost(token, id)`
- `updateAdminPost(token, id, data)`

**Key types:**
- `Post` — `{ id, title, slug, content: JSONContent, excerpt, published, tags: string[], created_at, updated_at }`
- `PaginatedPosts` — `{ items, total, page, limit, pages }`
- `Tag` — `{ id: string, name: string }`
- `CurrentUser` — `{ id, username, email, is_superuser, created_at }`
- `PostFormData` — extends PostCreate with `tags: string[]`

### Tiptap setup

> **Companion**: For Tiptap-specific guidance (extensions, editor config, best practices), see `.agents/skills/tiptap/SKILL.md`.

**Editor (admin)**: Full Tiptap editor with extensions for headings, lists, code blocks, images, links, text alignment, highlights, subscript/superscript, etc.

**Renderer (public)**: `src/lib/tiptap-renderer.tsx` — server-side/static rendering using `@tiptap/static-renderer`. Custom `CodeBlockNoRender` node + highlight.js for syntax highlighting.

Post content is stored as Tiptap JSON (`JSONContent`), not HTML.

### Component organization

| Directory | Purpose |
|-----------|---------|
| `src/components/ui/` | shadcn/ui primitives (button, card, input, sidebar, etc.) |
| `src/components/ui/command.tsx` | cmdk wrapper components (Combobox primitives) |
| `src/components/ui/popover.tsx` | Radix Popover primitives |
| `src/components/ui/combobox.tsx` | `Combobox` + `MultiCombobox` (search-as-you-type, debounced, badges) |
| `src/components/tiptap-ui*/` | Tiptap editor UI buttons and primitives |
| `src/components/tiptap-icons/` | Icon components for Tiptap toolbar |
| `src/components/tiptap-node/` | Custom Tiptap nodes (blockquote, code-block, heading, horizontal-rule, image, image-upload, list, paragraph) |
| `src/components/tiptap-templates/` | Pre-built editor templates (simple) |
| `src/components/` | App-level components (AnimatedNavbar, ThemeToggle) |
| `src/hooks/` | Custom React hooks (10 hooks) |
| `src/layouts/` | Layout wrappers (AdminLayout, DefaultLayout, LoginLayout) |
| `src/pages/` | Route components |
| `src/pages/admin/` | Admin-only pages (PostForm has tag input with searchable Combobox) |
| `src/lib/` | Utilities, API layer, Tiptap renderer |

### Path aliases

- `@/*` → `./src/*` (tsconfig + bunfig.toml alias)
- shadcn/ui: `@/components/ui/*`, `@/lib/utils`, `@/hooks/*`

### CSS architecture

```
src/index.css          → imports variables, animations, globals.css, highlight.js theme, Tiptap node styles
src/styles/_variables.css  → Tailwind CSS variables (CSS custom properties)
src/styles/_keyframe-animations.css  → Keyframe animations
styles/globals.css     → Tailwind directives (@tailwind base/components/utilities)
```

## Development

```bash
bun install          # Install dependencies
bun dev              # Start dev server with HMR
bun start            # Production server
bun build            # Build to dist/
bun lint             # Run Biome check
bun format           # Run Biome format --write
```

## Code Quality

- **Linting/Formatting**: Biome (recommended rules, React + TS support)
- **Pre-commit**: Husky + Biome (`bunx biome check --staged --fix`)
- **TypeScript**: Strict mode, `verbatimModuleSyntax`, `noUncheckedIndexedAccess`, `noImplicitOverride`
- **Module resolution**: Bundler mode, `allowImportingTsExtensions: true`

## Key Dependencies

| Package | Version | Role |
|---------|---------|------|
| react | ^19 | UI framework |
| react-dom | ^19 | DOM rendering |
| react-router-dom | ^7.15.1 | Routing |
| @tiptap/react | ^3.23.6 | Rich text editor |
| @tiptap/static-renderer | ^3.23.6 | Server-side rendering |
| swr | ^2.4.1 | Data fetching |
| tailwindcss | ^4.1.11 | Styling |
| @radix-ui/* | various | UI primitives (shadcn) |
| lucide-react | ^1.16.0 | Icons |
| motion | ^12.38.0 | Animations |
| lowlight | ^3.3.0 | Syntax highlighting |
| highlight.js | (via lowlight) | Code block highlighting |
| cmdk | ^1.1.1 | Command menu primitives (MultiCombobox) |

## Backend Integration

The backend is a FastAPI app with:
- PostgreSQL (async via asyncpg)
- SQLAlchemy ORM
- Alembic migrations
- JWT auth (PyJWT)
- bcrypt for password hashing

API runs on port 8000. Frontend connects via relative host (`window.location.hostname:8000`).

## Notes for Agents

- For Tiptap-specific guidance (extensions, editor config, best practices), read `.agents/skills/tiptap/SKILL.md` before working on editor-related code.

- Don't import from `node_modules` directly — use path aliases (`@/`)
- Tiptap content is JSON, not HTML. Use `renderPostContent()` from `@/lib/tiptap-renderer` to render
- Admin pages require a valid Bearer token in localStorage
- The `bun-plugin-tailwind` is used in both `build.ts` and `bunfig.toml` static config
- SWR hooks have `dedupingInterval: 0` — data is never cached between requests
- The `frontend.tsx` uses `import.meta.hot.data.root` for HMR root reuse (Bun-specific pattern)

### Tag Input (MultiCombobox)

- `src/components/ui/combobox.tsx` — `MultiCombobox` component: search-as-you-type with 300ms debounce, badge display with × remove, auto-hide duplicates
- `src/pages/admin/PostForm.tsx` — uses `MultiCombobox` for tag input; maps tag names ↔ UUIDs
- `src/pages/admin/CreatePostPage.tsx` / `EditPostPage.tsx` — fetch existing tags on mount, use `tagsLoaded` guard before rendering
- Tag names are trimmed on Enter; backend normalizes (lowercase, dedup)
- Styling: `.command-dialog` uses `@layer components` in `globals.css` (avoids `bun-plugin-tailwind` nested selector bug)
- API: `GET /admin/tags?search=` returns existing tags; send `tags: string[]` in create/update payloads
