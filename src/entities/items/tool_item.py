from __future__ import annotations
from typing import TYPE_CHECKING, Any
from enum import Enum
from src.core import Log
from src.core.types import ToolType
from src.world.tiles import Tile
from .base_item import Item

if TYPE_CHECKING:
    from src.entities import Player, Entity
    from src.groups import CameraGroup
    from src.custom_types import Interactables

def _use_hoe_strategy(player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
    """Tills the soil if it is a valid ground tile."""
    # Ensure we are targeting a Tile, not an Entity
    if not isinstance(target, Tile):
        Log.error("You can't use a hoe on this!")
        return False

    if not target.tillable or target.is_tilled:
        Log.error("You can't till this ground!")
        return False                  

    Log.success(f"Tilled the soil at {target.grid_x}, {target.grid_y}!")
    target.is_tilled = True

    if not target.level:
        Log.error("Warning: Tile doesn't have a reference to the Level!")
        return False
        
    target.level.till_map_node(target.grid_x, target.grid_y)
    return True

def _use_water_strategy(player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
    if not isinstance(target, Tile):
        Log.error("You can only water soil tiles!")
        return False

    if not target.is_tilled:
        Log.error("You can only water tilled soil!")
        return False
        
    if target.watered:
        Log.error("This tile is already watered!")
        return False

    active_item = player.inventory.get_active_item()
    if not isinstance(active_item, ToolItem) or not active_item.has_water():
        Log.error("Watering can is empty or invalid! Press 'R' to refill.")
        return False
        
    target.watered = True
    active_item.consume_water()
    
    Log.success(f"Watered tile at {target.grid_x}, {target.grid_y}! (Water left: {active_item.water_level}/{active_item.max_water})")
    return True

def _use_axe_strategy(player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
    Log.info("Chop chop")
    return True

def _use_pickaxe_strategy(player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
    Log.info("Breaking stone...")
    return True

def _use_generic_strategy(player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
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