from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

# Runtime Imports
from src.config import BLOCK_SIZE

# Type-Only Imports
if TYPE_CHECKING:
    from src.custom_types import Group, Num, Level, Entity, Plant, CameraGroup, ToolItem


class Tile(pygame.sprite.Sprite):
    """The Base Class. Holds the factory method and basic visual/position data."""
    def __init__(self, level: Level, x: Num, y: Num, tile_type_key: str, neighbors: list[bool], 
                 group: Group, detail_image: pygame.Surface | None = None) -> None:
        super().__init__(group)
        self.level:Level = level
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

    def plant(self, plant_name:str, camera_group:CameraGroup) -> Plant|None:
        pass
    
    def add_occupant(self, occupant:Entity) -> None:
        self.occupant = occupant
        self.occupant.tile = self
        
    def till(self) -> bool:
        """Default behavior for non-tillable tiles."""
        return False
    
    def water(self, item:ToolItem) -> bool:
        """Default behaviour when watering tiles"""
        return False

    def refresh_terrain(self, new_neighbors: list[bool]) -> None:
        """Generates the base visual. Subclasses will extend this."""
        pass
    