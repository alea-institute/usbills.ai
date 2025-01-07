"""
Template rendering and caching module.
"""

# standard library imports
import datetime
import json
from pathlib import Path
from typing import Any, Dict, Optional

# third party imports
from jinja2 import Environment, FileSystemLoader

# app imports
from usbills_app.config import PROJECT_PATH, get_config
from usbills_app.logger import create_logger
from usbills_app.templates.minifier import minify_html
from usbills_app.templates.cache import TemplateCache

# set up logger
LOGGER = create_logger(__name__)

# default path from config
DEFAULT_TEMPLATE_PATH = PROJECT_PATH / "templates"

# paths to exclude
EXCLUDED_PATHS = (
    # "stats.html",
    # "leaderboard.html",
)

# get config
APP_CONFIG = get_config()

VALID_CACHE_KEYS = (
    "title",
    "page",
    "limit",
    "offset",
    "start_date",
    "end_date",
    "q",
)


class TemplateRenderer:
    """Class for rendering jinja2 templates with Redis caching."""

    def __init__(
        self, template_path: Path = DEFAULT_TEMPLATE_PATH, cache_enabled: bool = True
    ) -> None:
        """Initialize the template renderer.

        Args:
            template_path: Path to template directory
            cache_enabled: Whether to enable Redis caching
        """
        if not template_path.exists():
            msg = f"Template directory does not exist: {template_path}"
            LOGGER.error(msg)
            raise FileNotFoundError(msg)

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(template_path)), autoescape=True
        )

        # Initialize Redis cache if enabled and not in debug mode
        self.cache = None
        if cache_enabled and not APP_CONFIG.debug:
            self.cache = TemplateCache()

        LOGGER.info(
            "Initialized template renderer with path %s and caching %s",
            template_path,
            "enabled" if self.cache else "disabled",
        )

    async def render(
        self, template_name: str, context: Dict[str, Any], minify: bool = True
    ) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of template to render
            context: Context data for template
            minify: Whether to minify the output

        Returns:
            The rendered template
        """
        # Generate cache key
        cache_key_values = {
            key: value for key, value in context.items() if key in VALID_CACHE_KEYS
        }
        cache_key_string = json.dumps(cache_key_values, sort_keys=True)
        cache_key = f"{template_name}:{hash(cache_key_string)}"

        # Check if path should be excluded from caching
        excluded = any(path in template_name for path in EXCLUDED_PATHS)

        # Try cache first if enabled
        if self.cache and not excluded:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        # Add timestamp if not present
        if "timestamp" not in context:
            context["timestamp"] = datetime.datetime.now().isoformat()

        # Render template
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**context)

            # Minify if requested
            if minify:
                rendered = minify_html(rendered)

            # Cache result if enabled
            if self.cache and not excluded:
                await self.cache.set(cache_key, rendered)

            LOGGER.debug("Successfully rendered template: %s", template_name)
            return rendered

        except Exception as e:
            LOGGER.error("Failed to render template %s: %s", template_name, str(e))
            raise

    async def clear_cache(self) -> None:
        """Clear the template cache."""
        if self.cache:
            await self.cache.clear()

    async def close(self) -> None:
        """Close the cache connection."""
        if self.cache:
            await self.cache.close()


# Global renderer instance
_RENDERER: Optional[TemplateRenderer] = None


def get_template_renderer(
    template_path: Optional[Path] = None, cache_enabled: bool = True
) -> TemplateRenderer:
    """Get or create global template renderer instance.

    Args:
        template_path: Path to template directory
        cache_enabled: Whether to enable Redis caching

    Returns:
        Global template renderer instance
    """
    global _RENDERER

    if _RENDERER is None:
        _RENDERER = TemplateRenderer(
            template_path=template_path or DEFAULT_TEMPLATE_PATH,
            cache_enabled=cache_enabled,
        )

    return _RENDERER
