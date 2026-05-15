#!/usr/bin/env python3
"""Create a superadmin user.

Usage:
    uv run scripts/create_superadmin.py --username admin --email admin@example.com --password secret123
"""

import argparse
import asyncio
import sys


from src.auth.models import User  # noqa: F401
from src.auth.schemas import UserCreate
from src.auth.service import create_user, get_user_by_username
from src.database import async_session, engine
from src.models import Base
from src.posts.models import Post  # noqa: F401


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create a superadmin user")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--email", required=True, help="Email address")
    parser.add_argument("--password", required=True, help="Password (min 8 chars)")
    args = parser.parse_args()

    if len(args.password) < 8:
        print("Error: Password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Check if user already exists
        existing = await get_user_by_username(db, args.username)
        if existing:
            print(f"User '{args.username}' already exists.", file=sys.stderr)
            sys.exit(1)

        data = UserCreate(
            username=args.username,
            email=args.email,
            password=args.password,
            is_superuser=True,
        )
        user = await create_user(db, data)
        print(f"Superadmin created: {user.username} ({user.email})")


if __name__ == "__main__":
    asyncio.run(main())
