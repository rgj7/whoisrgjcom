# Tag Feature — Design Decisions & Notes

Created: 2026-05-23
Completed: 2026-05-23

## Overview

Added a tag system to the PostForm so posts can have many tags. Users add/remove tags via a text input, see existing tags in a searchable dropdown, and create new tags on the fly.

---

## Backend Design Decisions

### Database

- **Many-to-many**: `Tag` model + `post_tags` join table (not a JSON column on Post)
- **Tag model**: minimal — `id` (UUID PK), `name` (String(50), unique)
- **Join table**: `post_tags(post_id, tag_id)` with composite PK

### Tag Resolution

- **Case-insensitive**: names lowercased on insert; `ilike` for search
- **Deduplication**: set comprehension — "Python", "PYTHON" → "python"
- **Whitespace trimming**: `strip()` on all tag names
- **Batch insert**: single `db.add_all()` call for new tags
- **Tag reuse**: existing tags matched by lowercase name across posts
- **Replace-all on update**: DELETE + INSERT in `set_post_tags()` (no merge)

### API

- `GET /admin/tags/?search=` — prefix match, case-insensitive, sorted by name. Returns **all** tags when no query (needed so frontend can resolve names → UUIDs).
- `POST /admin/posts/` — accepts `tags: string[]` in payload
- `PUT /admin/posts/{id}` — accepts `tags: string[]`, replaces all associations

### Schema Conventions

- `PostResponse.tags`: lowercased, sorted alphabetically
- `PostBase` normalizes Tag ORM → strings via `@field_validator`
- `PostUpdate.tags`: optional (`list[str] | None`) for partial updates
- `TagResponse`: `id` + `name`, with `__hash__`/`__eq__` for set ops

### Structure

Dedicated `src/tags/` sub-module:

| File | Exports |
|------|---------|
| `__init__.py` | `resolve_tags`, `set_post_tags` |
| `models.py` | `Tag` ORM + `post_tags` Table |
| `schemas.py` | `TagResponse` |
| `router.py` | `GET /admin/tags/` |
| `service.py` | `resolve_tags()` (create-or-lookup), `set_post_tags()` (replace) |

### Posts Integration

- `src/posts/models.py`: added `tags` relationship with `lazy="selectin"`
- `src/posts/admin_router.py`: imports `tag_service`, handles tags in create/update
- `src/posts/router.py`: public endpoints auto-include tags via `PostResponse`
- `src/main.py`: includes `tags_router`

### Migration

`2026-05-23_add_tags.py` — creates `tag` table + `post_tags` table

### Tests

`tests/test_tags.py` — 20+ test cases covering:
- Tag search (empty→all, prefix match, case-insensitive, sorted)
- Create with tags (normalization, dedup, no-tags, whitespace trimming)
- Update tags (replace, remove all, other fields unchanged)
- Tag resolution (existing reuse, mixed existing/new, case-insensitive uniqueness)
- Public endpoints (posts list, by ID, by slug all include tags)
- Auth guard (401 on unauthenticated operations)

---

## Frontend Design Decisions

### Tag Input UX

- **Pattern**: Combobox + Command (search-as-you-type) via `cmdk`
- **Adding tags**: click dropdown item or press Enter for new tags
- **Badges**: rendered inside combobox trigger, each with × remove button
- **After select**: input clears for next tag
- **Duplicates**: already-selected tags hidden from dropdown
- **Whitespace**: trimmed on Enter
- **Search delay**: 300ms debounce before API query

### Bug Fixes (lessons learned)

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| UUID showed instead of tag name | Backend returned empty list on no query | Returns all tags; frontend loads tags before rendering |
| Duplicate badge lists | Redundant badge block below combobox | Removed duplicate |
| Initial tags not normalized | PostForm didn't map names → UUIDs | `PostForm` resolves tag names → UUIDs at init |
| Badge lookup missed search results | `MultiCombobox` only checked `options` | Checks both `options` and `searchOptions` |
| Broken dedup in `onCreateNew` | Stale name-vs-UUID comparison | Removed stale check |

### Component Files

| File | Purpose |
|------|---------|
| `src/components/ui/command.tsx` | cmdk wrapper components |
| `src/components/ui/popover.tsx` | Radix Popover primitives |
| `src/components/ui/combobox.tsx` | `Combobox` + `MultiCombobox` (search-as-you-type, debounced, badges) |
| `src/pages/admin/PostForm.tsx` | Tag input state; maps tag names ↔ UUIDs |
| `src/pages/admin/CreatePostPage.tsx` | Fetches existing tags on mount, `tagsLoaded` guard |
| `src/pages/admin/EditPostPage.tsx` | Fetches existing tags on mount, `tagsLoaded` guard, preloads post tags |
| `src/lib/api.ts` | `Tag` interface, `searchTags()` function, `tags: string[]` on Post |

### Dependencies

- `cmdk` ^1.1.1 — command menu primitives (MultiCombobox)

### Styling Note

The `CommandDialog` component uses a `.command-dialog` CSS class with `@layer components` in `globals.css` instead of inline Tailwind nested selectors. This avoids a CSS parser bug in `bun-plugin-tailwind` that rejects attribute selectors containing `>` (e.g., `[&_[cmdk-group>div]]`).

### API Integration Flow

1. `GET /admin/tags?search=` — fetch existing tags for dropdown (empty → all tags)
2. User adds/removes tags via MultiCombobox badges
3. `tags: string[]` sent in create/update payloads
4. Edit flow: existing tags loaded from post response, displayed as badges
5. Frontend resolves tag names → UUIDs before sending to backend
