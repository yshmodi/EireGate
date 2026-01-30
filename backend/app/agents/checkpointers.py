# backend/app/agents/checkpointer.py
"""
Production-ready PostgreSQL checkpointer for LangGraph using Supabase.
Uses langgraph-checkpoint-postgres + psycopg.

Required in .env:
DATABASE_URL=postgresql://postgres.mkdbpelgkwbecgvcfeyv:password@aws-1-eu-west-1.pooler.supabase.com:5432/postgres

- Tables are created automatically on first use.
- Connection is validated on import.
"""

import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import psycopg
import warnings

from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

warnings.filterwarnings("ignore", category=UserWarning, module="psycopg")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not set in .env\n"
        "Example: DATABASE_URL=postgresql://postgres.mkdbpelgkwbecgvcfeyv:password@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
    )

# Validate URL format
parsed = urlparse(DATABASE_URL)
if not (
    parsed.scheme in ("postgresql", "postgres")
    and parsed.username
    and parsed.password
    and parsed.hostname
    and parsed.path.lstrip("/")
):
    raise ValueError(
        f"Invalid DATABASE_URL format.\n"
        f"Expected: postgresql://user:password@host:port/dbname\n"
        f"Received: {DATABASE_URL}"
    )

# Initialize saver by creating a psycopg connection directly
try:
    # Create connection using psycopg
    conn = psycopg.connect(DATABASE_URL, autocommit=True)

    # Test the connection
    with conn.cursor() as cur:
        cur.execute("SELECT 1")

        #Ensure public schema exists (usually default but good to check)
        cur.execute("CREATE SCHEMA IF NOT EXISTS public;")

    # Create the checkpointer with the connection
    checkpointer = PostgresSaver(conn)

    print("✓ PostgreSQL connection established successfully (Supabase checkpointer ready)")
    print("Tables will be created in 'public' schema on first checkpoint")
except Exception as e:
    raise RuntimeError(
        f"Failed to initialize PostgreSQL checkpointer (Supabase):\n"
        f"Error: {str(e)}\n\n"
        f"Checklist:\n"
        f"1. Correct DATABASE_URL in .env? (check password, host, port)\n"
        f"2. Supabase project online? (Check dashboard status)\n"
        f"3. Using Session Pooler connection string? (aws-X-region.pooler.supabase.com)\n"
        f"4. Installed packages: langgraph-checkpoint-postgres psycopg[binary]\n"
        f"5. Firewall / Supabase network restrictions? (allow your IP if needed)"
    )

# Optional: Async version (uncomment if you later use async def endpoints)
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
# async def get_async_checkpointer():
#     saver = await AsyncPostgresSaver.from_conn_string(DATABASE_URL)
#     return saver
