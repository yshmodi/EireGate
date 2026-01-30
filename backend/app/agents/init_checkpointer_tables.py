# Run this script once to create LangGraph checkpoint tables in Supabase
# python -m app.agents.init_checkpointer_tables

import os
from dotenv import load_dotenv
import psycopg
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

print("Connecting to:", DATABASE_URL)

try:
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    saver = PostgresSaver(conn)

    # This forces table creation (internal method)
    saver.setup()  # <-- This is the key line (creates tables if missing)

    print("✓ Tables created successfully:")
    print("  - checkpoints")
    print("  - checkpoints_parent")
    print("  - writes")
    print("  - writes_parent")

except Exception as e:
    print(f"Failed to create tables: {str(e)}")
    print("Checklist:")
    print("1. DATABASE_URL correct? (pooler port 5432 or 6543)")
    print("2. Password correct? (yashmodi242)")
    print("3. Supabase allows your IP? (Network restrictions → Add your IP)")
    raise

finally:
    if 'conn' in locals():
        conn.close()
