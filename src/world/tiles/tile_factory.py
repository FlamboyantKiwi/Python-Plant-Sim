from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .base_tile import Tile
from .ground_tile import GroundTile
from .water_tile import WaterTile

if TYPE_CHECKING:
    from src.custom_types import Group, Level, Num

# Route tile keys to their specific behavior classes
_TILE_MAP = {
    "WATER": WaterTile,
    "GRASS_A": GroundTile,
    "GRASS_B": GroundTile,
    "DIRT": GroundTile,
}

def create_tile(level: Level, x: Num, y: Num, tile_type_key: str, 
                neighbors: list[bool], group: Group, 
                detail_image: pygame.Surface | None = None) -> Tile:
    """Spawns the correct tile subclass based on the provided key."""
    
    # Grab the mapped class, defaulting to GroundTile if not explicitly listed
    target_class = _TILE_MAP.get(tile_type_key, GroundTile)
    
    return target_class(level, x, y, tile_type_key, neighbors, group, detail_image)