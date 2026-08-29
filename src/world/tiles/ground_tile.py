from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

# Runtime Imports
from src.config import BLOCK_SIZE, LAYOUT
from src.core.asset_loaders import ASSETS
from src.groups import CameraGroup
from src.utils import Log

from .base_tile import Tile

# Type-Only Imports
if TYPE_CHECKING:
    from src.custom_types import Group, Level, Num, Plant, ToolItem
    
class GroundTile(Tile):
    """Tile containing all farming logic."""
    def __init__(self, level: Level, x: Num, y: Num, tile_type_key: str, neighbors: list[bool], 
                 group: Group, detail_image: pygame.Surface | None = None) -> None:    
        # Call the parent __init__ to set up position and visuals
        super().__init__(level, x, y, tile_type_key, neighbors, group, detail_image)
        self.is_tilled = False
        self.tillable = (tile_type_key in ["GRASS_A", "GRASS_B", "DIRT"])
        self.watered = False
        
    def refresh_terrain(self, new_neighbors: list[bool]) -> None:
        # LAYER 1: Base Dirt Background
        dirt_img = ASSETS.get_image("DIRT_IMAGE")
        self.base_image = dirt_img.copy() if dirt_img else pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        if not dirt_img: 
            self.base_image.fill((139, 69, 19)) # Fallback brown
        
        # LAYER 2: Draw farming overlays (Tilled soil) BEFORE the grass!
        # This allows the grass to curve perfectly over the edges of the tilled dirt.
        if self.is_tilled:
            tilled_img = ASSETS.get_image("tilled_soil")
            if tilled_img:
                self.base_image.blit(tilled_img, tilled_img.get_rect(center=(BLOCK_SIZE//2, BLOCK_SIZE//2)))

        # LAYER 3: Draw the Grass marching squares OVER the dirt and tilled soil
        if any(new_neighbors) and self.tile_type_key != "WATER":
            grass_key = self.tile_type_key if "GRASS" in self.tile_type_key else "GRASS_A"
            # Assumes GRASS_LAYOUT is imported/available!
            grass_overlay = ASSETS.autotile(grass_key, LAYOUT, new_neighbors)
            self.base_image.blit(grass_overlay, (0, 0))

        self.image = self.base_image.copy()

        # LAYER 4: Draw static details (Pebbles, flowers, etc.) ON TOP of everything
        if self.detail_image and not self.is_tilled:
            detail_rect = self.detail_image.get_rect(center=(BLOCK_SIZE // 2, BLOCK_SIZE // 2))
            self.image.blit(self.detail_image, detail_rect)

    def till(self) -> bool:
        """Tills this ground tile if valid and updates the level map nodes."""
        if self.occupant and self.occupant.till():
            pass
            
        if not self.tillable or self.is_tilled:
            return False
            
        self.is_tilled = True
            
        self.level.till_map_node(self.grid_x, self.grid_y)
        Log.success(f"Tilled the soil at {self.grid_x}, {self.grid_y}!")
        return True
    
    def water(self, item:ToolItem) -> bool:
        """Waters this ground tile if it is tilled and not already watered."""
        if not self.is_tilled or self.watered:
            return False
        item.consume_water()
        self.watered = True
        Log.success(f"Watered! {self.grid_x}, {self.grid_y}! (Water left: {item.water_level}/{item.max_water})")
        return True
    
    def plant(self, plant_name:str, camera_group:CameraGroup) -> Plant|None:
        """Validates the tile state, instantiates the plant, and links it."""
        from src.entities.plant import Plant
        
        if not self.is_tilled or self.occupant:
            return None # Must be tilled and unoccupied
        
        # Create plant using level's plant group
        new_plant = Plant(
            plant_name, self.grid_x, self.grid_y, 
            camera_group,   # Pass camera group
            self.level.plant_group) # Pass level's plant group
        
        self.add_occupant(new_plant)
        return new_plant