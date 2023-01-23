"""Simple yet powerful dependency injection framework!"""

from snake_di._container import Container
from snake_di._provider import AsyncProvider, Provider

__version__ = "0.0.2"
__all__ = ["Provider", "AsyncProvider", "Container"]
