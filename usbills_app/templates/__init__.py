"""
Package for template rendering, caching, and minification.
"""

# relative imports
from .renderer import TemplateRenderer, get_template_renderer
from .minifier import minify_html, minify_css
from .cache import TemplateCache

__all__ = [
    "TemplateRenderer",
    "get_template_renderer",
    "minify_html",
    "minify_css",
    "TemplateCache",
]
