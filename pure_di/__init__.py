"""Simple yet powerful dependency injection framework!"""

from pure_di._container import Container
from pure_di._provider import AsyncProvider, Provider

__version__ = "0.0.1"
__all__ = ["Provider", "AsyncProvider", "Container"]
