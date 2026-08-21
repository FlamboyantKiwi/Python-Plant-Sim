from __future__ import annotations
from typing import Any, Generator
import pygame
from .spritesheet import SpriteSheet
from .. import Log
from .asset_group import AssetGroup

class SpriteGroup(AssetGroup):
    """Parent for Sheet-based assets (Tiles, Tools, Plants)."""
    SCALE_FACTOR: int = 2
    TILE_SIZE: int = 32

    def __init__(self, manager: Any, raw_data:Any = None, **sheet_files: str) -> None:
        super().__init__(manager, raw_data=raw_data)
        self.sheet_files = sheet_files
        self.loaded_sheets: dict[str, SpriteSheet] = {}

    def get_sheet(self, key: str = "main") -> SpriteSheet | None:
        if key in self.loaded_sheets:
            return self.loaded_sheets[key]
        filename = self.sheet_files.get(key)
        if not filename:
            Log.error(f"[FATAL] {self.__class__.__name__} asked for '{key}', but it wasn't provided in AssetLoader!")
            return None
        try:
            sheet = SpriteSheet(f"{filename}.png")
            self.loaded_sheets[key] = sheet
            Log.success(f"[{self.__class__.__name__}] Successfully loaded sheet: {filename}.png")
            return sheet
        except Exception as e:
            Log.error(f"Failed to load sheet '{filename}' for {self.__class__.__name__}: {e}")
            return None

    def debug_print(self) -> None:
        super().debug_print()
        self.print_line_break()
        
    def _iter_rows(self, sheet_key: str, order_list: list) -> Generator[tuple[str, int, int, SpriteSheet], None, None]:
        """Yields (name, current_y, row_h, sheet) for iterating evenly spaced spritesheet rows."""
        sheet = self.get_sheet(sheet_key)
        if not sheet or not order_list:
            return
            
        row_h = sheet.sheet.get_height() // len(order_list)
        for i, name in enumerate(order_list):
            yield name, i * row_h, row_h, sheet

    def _get_tight_strip(self, sheet: SpriteSheet, x: int, y: int, w: int, h: int) -> tuple[pygame.Surface | None, pygame.Rect | None]:
        """Extracts a subsurface and crops out empty vertical space using the bounding rect."""
        padded_strip = sheet.get_image(x, y, w, h)
        bounds = padded_strip.get_bounding_rect()
        
        if bounds.h <= 0:
            return None, None
            
        tight_strip = padded_strip.subsurface((0, bounds.y, w, bounds.h))
        return tight_strip, bounds