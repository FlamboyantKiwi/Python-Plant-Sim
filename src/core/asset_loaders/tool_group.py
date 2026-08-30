from __future__ import annotations

from enum import Enum

import pygame

from .sprite_group import SpriteGroup


class ToolGroup(SpriteGroup):
    ITEM_SIZE: int = 36

    def load(self) -> None:
        sheet = self.get_sheet("main")
        if not sheet or not self.raw_data:
            return
        materials = self.raw_data.get("materials", [])
        layout = self.raw_data.get("layout", [])
        for r_idx, mat in enumerate(materials):
            mat_str = mat.value if isinstance(mat, Enum) else mat
            self.storage[mat_str] = {}
            for c_idx, tool in enumerate(layout):
                self.storage[mat_str][tool] = sheet.get_image(
                    c_idx * self.TILE_SIZE,
                    r_idx * self.TILE_SIZE + 2,
                    self.TILE_SIZE, self.TILE_SIZE,
                    (self.ITEM_SIZE, self.ITEM_SIZE))

    def get(self, key: str) -> pygame.Surface | None:
        if "_" not in key:
            return None
        material, tool_name = key.upper().split("_", 1)
        return self.storage.get(material, {}).get(tool_name)