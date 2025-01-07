"""
"Static" route handlers for the application.
"""

# packages
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response

# create router
router = APIRouter()


# /sitemap.xml just dumps static/sitemap.xml
@router.get("/sitemap.xml", response_class=HTMLResponse, tags=["html"])
async def sitemap() -> str:
    """Sitemap route handler that returns the sitemap XML file.

    Returns:
        str: Rendered sitemap template
    """
    with open("static/sitemap.xml", "rt", encoding="utf-8") as sitemap_file:
        return sitemap_file.read()


@router.get("/robots.txt", response_class=HTMLResponse, tags=["static"])
async def robots() -> str:
    """Robots route handler that returns the robots.txt file.

    Returns:
        str: Rendered robots template
    """
    with open("static/robots.txt", "rt", encoding="utf-8") as robots_file:
        return robots_file.read()


@router.get("/ai.txt", response_class=HTMLResponse, tags=["static"])
async def ai() -> str:
    """AI route handler that returns the ai.txt file.

    Returns:
        str: Rendered ai template
    """
    with open("static/ai.txt", "rt", encoding="utf-8") as ai_file:
        return ai_file.read()


# favicon.ico just dumps static/favicon.ico
@router.get("/favicon.ico", response_class=Response, tags=["static"])
async def favicon_png() -> Response:
    """Favicon route handler that returns the favicon icon.

    Returns:
        Response: Rendered favicon template
    """
    with open("static/favicon.ico", "rb") as favicon_file:
        return Response(
            favicon_file.read(),
            media_type="image/x-icon",
        )


# favicon.png just dumps static/favicon.png
@router.get("/favicon.png", response_class=Response, tags=["static"])
async def favicon_ico() -> Response:
    """Favicon route handler that returns the favicon icon.

    Returns:
        Response: Rendered favicon template
    """
    with open("static/favicon.png", "rb") as favicon_file:
        return Response(
            favicon_file.read(),
            media_type="image/png",
        )
