from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

# Runtime Imports
from src.settings import BLOCK_SIZE
from .base_tile import Tile
# Type-Only Imports
if TYPE_CHECKING:
    from src.custom_types import Group, Num, Level

class WaterTile(Tile):
    """Tile representing water. Blocks movement."""
    def __init__(self, level: Level, x: Num, y: Num, tile_type_key: str, neighbors: list[bool], 
                 group: Group, detail_image: pygame.Surface | None = None) -> None:
        super().__init__(level, x, y, tile_type_key, neighbors, group, detail_image)
        self._base_obstructed = True
        
        
    def refresh_terrain(self, new_neighbors: list[bool]) -> None:
        # A simple, static block of water.
        self.base_image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.base_image.fill((56, 220, 245)) # Cyan Water
        self.image = self.base_image.copy()

