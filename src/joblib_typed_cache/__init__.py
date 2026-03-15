"""Typed version of joblib's cache to support pydantic validation and type checking."""

__all__ = [
    "__version__",
    "Memory",
]

from .core import Memory
from .version import VERSION as __version__
