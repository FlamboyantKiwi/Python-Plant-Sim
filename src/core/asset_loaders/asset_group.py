from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from src.utils import Log

if TYPE_CHECKING:
    from src.core.asset_loaders import AssetLoader

class AssetGroup(ABC):
    """Universal Base Class. Automatically gives every subclass its own unique STORAGE dictionary."""
    def __init__(self, manager: AssetLoader, raw_data:Any = None) -> None:
        self.manager = manager
        self.storage: dict[Any, Any] = {}
        self.raw_data = raw_data

    @abstractmethod
    def load(self) -> None:
        pass

    def debug_print(self) -> None:
        Log.info(f"\n--- {self.__class__.__name__} ({len(self.storage)} items loaded) ---")

    def print_line_break(self) -> None:
        Log.divider()

    def clean_up(self) -> None:
        pass