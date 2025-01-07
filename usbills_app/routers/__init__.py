"""
Routers for the application.
"""

# imports
from typing import List

# packages
from fastapi import APIRouter

# project
from usbills_app.routers.index import router as index_router
from usbills_app.routers.static import router as static_router
from usbills_app.routers.bills import router as bills_router
from usbills_app.routers.search import router as search_router
from usbills_app.routers.api import router as api_router


def get_router_modules() -> List[APIRouter]:
    """Get list of API router modules to load.

    Returns:
        List[APIRouter]: List of FastAPI router instances
    """
    # Import and return router modules here
    return [
        api_router,
        index_router,
        static_router,
        bills_router,
        search_router,
    ]
