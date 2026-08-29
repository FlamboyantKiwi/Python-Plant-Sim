from __future__ import annotations

from typing import TYPE_CHECKING

from src.utils import Log

from .base_item import Item

if TYPE_CHECKING:
    from src.custom_types import CameraGroup, Entity, Interactables, Player, Tile

class FoodItem(Item):
    def use(self, player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
        if self.count <= 0: 
            return False
        Log.info(f"Yum! Ate {self.name} for {self.data.energy_gain} energy.")
        self.count -= 1
        return True