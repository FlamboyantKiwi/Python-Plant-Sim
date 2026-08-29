from __future__ import annotations

from typing import Any

import pygame

from src.types import TextConfig
from src.utils import Log

from .asset_group import AssetGroup


class FontGroup(AssetGroup):
    """Internal helper class to manage font caching."""
    def __init__(self, manager: Any, raw_data:Any = None) -> None:
        super().__init__(manager, raw_data=raw_data)

    def load(self) -> None:
        pass

    def get_font(self, config: TextConfig) -> pygame.font.Font:
        key = (config.name, config.size, config.bold, config.italic)
        if key not in self.storage:
            if not pygame.font.get_init():
                pygame.font.init()
            self.storage[key] = pygame.font.SysFont(
                config.name, config.size, config.bold, config.italic
            )
        return self.storage[key]

    def debug_print(self) -> None:
        super().debug_print()
        for key in self.storage:
            name, size, bold, italic = key
            styles = []
            if bold:
                styles.append("Bold")
            if italic:
                styles.append("Italic")
            style_str = " + ".join(styles) if styles else "Normal"
            Log.info(f" Name: {name:<20} | Size: {size:<3} | Style: {style_str}")
        self.print_line_break()