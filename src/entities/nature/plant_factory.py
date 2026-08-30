from __future__ import annotations

from typing import TYPE_CHECKING

from .plant import Plant

if TYPE_CHECKING:
    from src.custom_types import Group

class PlantFactory:
    """Factory for spawning procedural plants and trees."""
    
    @staticmethod
    def create(plant_id: str, grid_x: int, grid_y: int, *groups: Group) -> Plant:
        # Currently routes to the universal Plant class.
        # Expandable later via a _LOGIC_MAP if subclassing Trees vs Crops.
        return Plant(plant_id, grid_x, grid_y, *groups)