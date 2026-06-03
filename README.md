# whoisrgj.com - personal site

> Currently a work in-progress

A web app utilizing FastAPI + React, serving as my personal site over at [whoisrgj.com](https://www.whoisrgj.com).

This replaces a previous version ([old repo here](https://github.com/rgj7/whoisrgj_blog)). I've learned some lessons and updated my tooling since then.

- Using Pi Coding Agent with extensions
- Trying different models
    - Qwen3.6 27B/31B ran locally using Llama.cpp on a 4090 GPU
    - Codex 5.3/5.5
- Using AGENTS.md and agent skills more effieciently
- Learning/trying various approaches
    - Plan Driven
    - Spec Driven

## Features

- Public personal site with blog, dev, gaming, and travel sections
- Admin dashboard for managing posts and travel data
- Rich text post editor using TipTap
- Various integrations to third-party APIs (i.e. RAWG, TMDB)

## Stack

- *Backend*: Python 3.14, FastAPI, SQLAlchemy (async), asyncpg, Alembic, PostgreSQL, Pydantic, JWT auth
- *Frontend*: React 19 + Bun, React Router, Tailwind CSS, Shadcn/Radix UI, TipTap, SWR, Motion, D3/TopoJSON
- *Infrastructure*: Docker Compose, Caddy
- *Tooling*: uv, Ruff, pytest/pytest-asyncio, pre-commit, Biome