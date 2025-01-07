"""
Main FastAPI application module.
"""

# imports
from typing import Optional

# packages
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# project
from usbills_app.config import AppConfig, get_config, STATIC_PATH
from usbills_app.logger import create_logger
from usbills_app.routers import get_router_modules

# create logger
LOGGER = create_logger(__name__)


def create_app(app_config: Optional[AppConfig] = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        app_config (Optional[AppConfig]): App configuration object.
            If None, loads from config file.

    Returns:
        FastAPI: Configured FastAPI application
    """
    # Get app config if not provided
    if app_config is None:
        app_config = get_config()

    # Create FastAPI app
    app = FastAPI(
        title=app_config.app_name,
        version=app_config.app_version,
        debug=app_config.debug,
        contact={
            "name": "ALEA Institute",
            "url": "https://aleainstitute.ai",
            "email": "hello@aleainstitute.ai",
        },
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # log it
    LOGGER.info(f"App created with config: {app_config}")

    # add static mount and log it
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
    LOGGER.info(f"Static files mounted at: {STATIC_PATH}")

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=app_config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # log the cors setup
    LOGGER.info(f"CORS configured with origins: {app_config.cors_origins}")

    # Include all routers from router modules
    for router in get_router_modules():
        app.include_router(router)
        LOGGER.info(f"Router included: {router}")

    # log final
    LOGGER.info("App created and configured.")

    return app


# default app instance for WSGI servers
app = create_app()
