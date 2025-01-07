"""
Template cache using Redis for storing and retrieving templates efficiently.
"""

# imports
from typing import Optional

# packages
import redis.asyncio

# project
from usbills_app.config import get_config
from usbills_app.logger import create_logger

# set up logger
LOGGER = create_logger(__name__)

# get config
APP_CONFIG = get_config()


class TemplateCache:
    """Redis cache for templates."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        prefix: str = "template:",
    ) -> None:
        """Initialize Redis cache connection.

        Args:
            host: Redis host address
            port: Redis port
            db: Redis database number
            prefix: Key prefix for template cache entries
        """
        self.redis = redis.asyncio.Redis(
            host=host, port=port, db=db, socket_keepalive=True, decode_responses=True
        )
        self.prefix = prefix
        LOGGER.info(f"Initialized Redis template cache at {host}:{port} db={db}")

    async def get(self, key: str) -> Optional[str]:
        """Get template from cache.

        Args:
            key: Cache key

        Returns:
            Cached template string or None if not found
        """
        full_key = f"{self.prefix}{key}"
        value = await self.redis.get(full_key)
        if value:
            LOGGER.info(f"Cache hit for key: {key}")
        else:
            LOGGER.warning(f"Cache miss for key: {key}")
        return value

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> None:
        """Set template in cache.

        Args:
            key: Cache key
            value: Template string to cache
            expire: Optional expiration time in seconds
        """
        full_key = f"{self.prefix}{key}"
        await self.redis.set(full_key, value, ex=expire)
        LOGGER.debug(f"Cached template with key: {key}")

    async def delete(self, key: str) -> None:
        """Delete template from cache.

        Args:
            key: Cache key
        """
        full_key = f"{self.prefix}{key}"
        await self.redis.delete(full_key)
        LOGGER.debug(f"Deleted cached template with key: {key}")

    async def clear(self) -> None:
        """Clear all cached templates."""
        keys = await self.redis.keys(f"{self.prefix}*")
        if keys:
            await self.redis.delete(*keys)
        LOGGER.debug("Cleared all cached templates")

    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis.close()
        LOGGER.debug("Closed Redis connection")
