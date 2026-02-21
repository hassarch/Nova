"""NOVA Configuration Loader"""
from pathlib import Path

import yaml

from .schema import NovaConfig

# Configuration paths
CONFIG_DIR = Path.home() / ".nova"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def create_default_config() -> Path:
    """Create default config file in user home directory"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    default_config = NovaConfig()

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(default_config.model_dump(), f, default_flow_style=False, sort_keys=False)

    return CONFIG_FILE


def load_config() -> NovaConfig:
    """Load configuration from file or return defaults"""
    if not CONFIG_FILE.exists():
        return NovaConfig()

    try:
        with open(CONFIG_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
        return NovaConfig(**data)
    except Exception:
        # If config is invalid, return defaults
        return NovaConfig()


def get_config() -> NovaConfig:
    """Get current configuration (convenience function)"""
    return load_config()
