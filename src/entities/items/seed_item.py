from __future__ import annotations
from typing import TYPE_CHECKING
from src.core import Log
from src.world.tiles import Tile
from .base_item import Item

if TYPE_CHECKING:
    from src.entities import Player, Entity
    from src.groups import CameraGroup
    from src.custom_types import Interactables

class SeedItem(Item):
    """Handles planting logic and consumes 1 stack count upon success."""
    def use(self, player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
        if self.count <= 0 or not isinstance(target, Tile): 
            return False                  
              
        plant_id = self.item_id.replace("_seeds", "")
        if target.plant(plant_id, group):
            Log.info(f"Planting {plant_id}...")
            self.count -= 1
            return True
        return False