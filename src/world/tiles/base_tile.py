from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

# Runtime Imports
from src.settings import BLOCK_SIZE
from src.core.asset_loaders import ASSETS
from src.core.asset_loaders.asset_data import LAYOUT

# Type-Only Imports
if TYPE_CHECKING:
    from src.custom_types import Group, Num, Level, Entity


class Tile(pygame.sprite.Sprite):
    """The Base Class. Holds the factory method and basic visual/position data."""
    def __init__(self, level: Level, x: Num, y: Num, tile_type_key: str, neighbors: list[bool], 
                 group: Group, detail_image: pygame.Surface | None = None) -> None:
        super().__init__(group)
        self.level = level
        self.grid_x = int(x // BLOCK_SIZE)
        self.grid_y = int(y // BLOCK_SIZE)
        self.position = (x, y)
        self.tile_type_key = tile_type_key
        self.detail_image = detail_image
        
        self.occupant: Entity|None = None 
        
        # Unified Tile Attributes
        self._base_obstructed = False
        self.tillable: bool = False
        self.is_tilled: bool = False
        self.watered: bool = False

        # Generate initial visual
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.refresh_terrain(neighbors)
        self.rect = self.image.get_rect(topleft=self.position)

    @classmethod
    def create(cls, level: Level, x: Num, y: Num, tile_type_key: str, neighbors: list[bool], 
               group: Group, detail_image: pygame.Surface | None = None) -> Tile:
        """THE FACTORY: Looks at the key and returns the correct subclass!"""
        from .water_tile import WaterTile
        from .ground_tile import GroundTile
        
        if tile_type_key == "WATER":
            return WaterTile(level, x, y, tile_type_key, neighbors, group, detail_image)
        else:
            return GroundTile(level, x, y, tile_type_key, neighbors, group, detail_image)

    def refresh_terrain(self, new_neighbors: list[bool]) -> None:
        """Generates the base visual. Subclasses will extend this."""
        pass
    