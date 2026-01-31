import os
from redis import Redis
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis = Redis.from_url(REDIS_URL, decode_responses=True)

# Test connection on startup
try:
    redis.ping()
    logger.info("✓ Redis cache connected successfully")
except Exception as e:
    logger.warning(f"⚠ Redis cache unavailable: {str(e)}. Using in-memory fallback.")
    redis = None  # type: ignore

def set_cache(key: str, value: str, ttl: int = 7200):  # 2 hours
    if redis:
        try:
            redis.set(key, value, ex=ttl)
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

def get_cache(key: str) -> str | None:
    if redis:
        try:
            return redis.get(key)
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
    return None
