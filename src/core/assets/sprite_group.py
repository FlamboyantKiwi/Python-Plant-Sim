from __future__ import annotations
from typing import Any
from src.core import SpriteSheet, Log
from .base_group import AssetGroup

class SpriteGroup(AssetGroup):
    """Parent for Sheet-based assets (Tiles, Tools, Plants)."""
    SCALE_FACTOR: int = 2
    TILE_SIZE: int = 32

    def __init__(self, manager: Any, **sheet_files: str) -> None:
        super().__init__(manager)
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