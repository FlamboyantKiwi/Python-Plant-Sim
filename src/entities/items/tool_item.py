from __future__ import annotations
from typing import TYPE_CHECKING, Any
from src.core import Log
from src.core import ToolType
from src.world import Tile
from .base_item import Item

if TYPE_CHECKING:
    from src.entities import Player, Entity
    from src.groups import CameraGroup
    from src.custom_types import Interactables

def _use_hoe_strategy(player: Player, target: Tile | Entity, interactables: Interactables, group: CameraGroup) -> bool:
    """Tills the soil if it is a valid ground tile."""
    # Normalise target to the tile 
    tile = target if isinstance(target, Tile) else target.tile

    if not tile:
        Log.error("You can't use a hoe here!")
        return False
    if not tile.till():
        Log.error(f"You can't use a Hoe at {tile.grid_x}, {tile.grid_y}")
    # Success
    return True
  
def _use_water_strategy(player: Player, target: Tile | Entity, interactables: Interactables, group: CameraGroup) -> bool:
    """Waters the target tile using the player's active watering can."""
    active_item = player.active_item
    if not isinstance(active_item, ToolItem) or not active_item.has_water():
        Log.error("Watering can is empty or invalid!")
        return False
    
    tile = target if isinstance(target, Tile) else target.tile
    if not tile:
        Log.error("Can't water here")
        return False
    if not tile.water(active_item):
        Log.error(f"Can't water {type(tile).__name__} at {tile.grid_x}, {tile.grid_y}")
        return False
    # Success
    return True    

def _use_axe_strategy(player: Player, target: Tile | Entity, interactables: Interactables, group: CameraGroup) -> bool:
    Log.info("Chop chop")
    return True

def _use_pickaxe_strategy(player: Player, target: Tile | Entity, interactables: Interactables, group: CameraGroup) -> bool:
    Log.info("Breaking stone...")
    return True

def _use_generic_strategy(player: Player, target: Tile | Entity, interactables: Interactables, group: CameraGroup) -> bool:
    """Fallback for tools with no specific logic yet."""
    return False

class ToolItem(Item):
    """Handles logic for persistent, non-consumable tools using the Strategy Pattern."""
    
    # Strategy registry mapping ToolTypes directly to decoupled functions
    STRATEGIES = {
        ToolType.HOE: _use_hoe_strategy,
        ToolType.WATER: _use_water_strategy,
        ToolType.AXE: _use_axe_strategy,
        ToolType.PICKAXE: _use_pickaxe_strategy,
    }

    def __init__(self, item_id: str, count: int = 1, preloaded_data: Any = None):
        super().__init__(item_id, count, preloaded_data)
        self.max_water = 10
        if getattr(self, 'tool_type', None) == ToolType.WATER:
            self.max_water = 10
            self.water_level = 10

    def use(self, player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
        if not target: 
            return False

        t_type = self.tool_type
        if not t_type:
            return _use_generic_strategy(player, target, interactables, group)

        strategy_func = self.STRATEGIES.get(t_type, _use_generic_strategy)
        return strategy_func(player, target, interactables, group)
    
    def has_water(self) -> bool:
        """Safely checks if the watering can has available water."""
        return self.water_level is not None and self.water_level > 0

    def consume_water(self) -> None:
        """Safely decrements the water level."""
        if self.water_level is not None and self.water_level > 0:
            self.water_level -= 1
            
    def refill(self):
        if self.water_level is not None:
            self.water_level = self.max_water