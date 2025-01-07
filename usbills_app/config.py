"""
App configuration module
"""

# imports
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, List, Dict

# defaults
APP_PATH = Path(__file__).parent
PROJECT_PATH = APP_PATH.parent
STATIC_PATH = PROJECT_PATH / "static"
DEFAULT_CONFIG_PATH = PROJECT_PATH / "config.json"


@dataclass
class AppConfig:
    """
    App configuration class
    """

    # basic app config
    debug: bool = field(default=False)
    log_level: str = field(default="INFO")
    log_file: str = field(default="usbills.log")
    api_host: str = field(default="0.0.0.0")
    app_port: int = field(default=8000)
    app_name: str = field(default="usbills.ai")
    app_version: str = field(default="1.0.0")
    cors_origins: List[str] = field(
        default_factory=lambda: [
            "http://localhost",
            "http://localhost:8000",
            # API is free and open
            "*",
        ]
    )

    # database config
    db_proto: str = field(default="postgresql+asyncpg")
    db_host: str = field(default="localhost")
    db_port: int = field(default=5432)
    db_user: str = field(default="fbs")
    db_password: str = field(default="fbs")
    db_name: str = field(default="fbs")
    db_pool_size: int = field(default=8)

    # solr config
    solr_proto: str = field(default="http")
    solr_host: str = field(default="localhost")
    solr_port: int = field(default=8983)
    solr_core: str = field(default="fbs")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the AppConfig to a dictionary.

        Returns:
            Dict[str, Any]: The AppConfig as a dictionary.
        """
        return asdict(self)  # type: ignore

    def to_json(self) -> str:
        """
        Convert the AppConfig to a JSON string.

        Returns:
            str: The AppConfig as a JSON string.
        """
        return json.dumps(self.to_dict(), indent=4, default=str)


def get_config(config_path: Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    """
    Get the app configuration.

    Args:
        config_path (Path): The path to the configuration file. Defaults to DEFAULT_CONFIG_PATH.

    Returns:
        Dict[str, Any]: The app configuration.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "rt", encoding="utf-8") as config_file:
        json_data = json.load(config_file)

    # return the app config
    return AppConfig(**json_data)


if __name__ == "__main__":
    # print the app configuration
    app_config = get_config()
    print(app_config)
