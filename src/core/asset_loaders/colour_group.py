from __future__ import annotations
import pygame
from typing import TYPE_CHECKING, Any

from .config_group import ConfigGroup

if TYPE_CHECKING:
    from src.custom_types import Colour

class ColourGroup(ConfigGroup):
    """Manages game palette and provides debug printing."""
    def __init__(self, manager: Any, raw_data) -> None:
        super().__init__(manager, raw_data=raw_data)
        self.default = pygame.Color(255, 0, 255)

    def load(self) -> None:
        for name, hex_str in self.raw_data.items():
            self.storage[name] = pygame.Color(hex_str)
        self.default = self.storage.get("DEFAULT", pygame.Color(255, 0, 255))

    def get_colour(self, name: Colour, fallback_type: Colour | None = None) -> pygame.Color:
        col = self.storage.get(name)
        if col:
            return col
        if fallback_type:
            col = self.storage.get(fallback_type)
            if col:
                return col
        return self.get_val(name) or self.default