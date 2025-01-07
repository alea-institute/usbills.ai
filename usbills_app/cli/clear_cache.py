"""
CLI task to clear the template cache in redis.
"""

# imports
import asyncio

# project imports
from usbills_app.templates import get_template_renderer
from usbills_app.logger import create_logger

# get logger
LOGGER = create_logger(__name__)


async def clear_cache() -> None:
    """Clear the template cache."""
    try:
        # get template renderer
        renderer = get_template_renderer()
        LOGGER.info("Clearing template cache...")

        # clear the cache
        await renderer.clear_cache()
        LOGGER.info("Successfully cleared template cache")

        # close the renderer
        await renderer.close()
        LOGGER.info("Closed template renderer")

    except Exception as e:
        LOGGER.error("Error clearing cache: %s", str(e))
        raise


def main() -> None:
    """Main entry point for script."""
    asyncio.run(clear_cache())


if __name__ == "__main__":
    main()
