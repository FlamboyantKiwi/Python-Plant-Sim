from __future__ import annotations
import pygame
from src.core.assets import ASSETS
from src.core.types import ItemCategory, ToolType
from src.core import Log
from typing import TYPE_CHECKING, Any
from src.world.tile import Tile

if TYPE_CHECKING:
    from src.entities import Player, Entity
    from src.groups import CameraGroup
    from src.custom_types import Interactables

class Item:
    """ Base class for an inventory item. 
    Manages stack counts and proxies core data from the SQLite database. """
    def __init__(self, item_id: str, count: int = 1, preloaded_data: Any = None) -> None:
        # OPTIMIZATION: Use preloaded data from the factory if available
        self.data:Any  = preloaded_data or ASSETS.item(item_id)
        self.item_id: str = item_id
        self.count:int = min(count, self.max_stack)
        self.image: pygame.Surface = ASSETS.item_image(self.data)  

        self.water_level: int | None = None
        self.max_water: int | None = None

    # --- PROPERTIES (Proxies to the Data) ---
    def __getattr__(self, attr_name: str) -> Any:
        """ Magic Proxy: Routes missing attribute requests (like .name or .buy_price)
        directly to the underlying ItemData object."""
        # SAFETY CHECK: Ignore Python's internal dunder methods and prevent recursion on 'data'
        if attr_name.startswith('__') and attr_name.endswith('__') or attr_name == 'data':
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr_name}'")
        try:
            return getattr(self.data, attr_name)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' and its data have no attribute '{attr_name}'")

    @property
    def max_stack(self) -> int:
        if not getattr(self.data, 'stackable', True):
            return 1
        return getattr(self.data, 'max_stack', 99)

    # --- INVENTORY LOGIC ---
    def add_to_stack(self, amount: int) -> int:
        """Adds to the current stack and returns any leftover amount."""
        to_add = min(amount, self.max_stack - self.count)
        self.count += to_add
        return amount - to_add

    def remove_from_stack(self, amount: int) -> int:
        """Removes from the stack and returns the actual amount successfully removed."""
        if amount >= self.count:
            taken = self.count
            self.count = 0
            return taken
            
        self.count -= amount
        return amount

    def use(self, player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
        """Default behavior for unusable items. Returns True if action succeeded."""
        return False
        
    def copy_one(self) -> Item:
        """Creates a new instance with a count of 1 (Useful for UI dragging)."""
        return create_item(self.item_id, 1)


# --- INDEPENDENT TOOL STRATEGY FUNCTIONS ---
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


# --- SUBCLASSES ---
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

class SeedItem(Item):
    """Handles planting logic and consumes 1 stack count upon success."""
    def use(self, player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
        if self.count <= 0 or not isinstance(target, Tile): 
            return False
        
        if not target.is_tilled or target.occupant:
            Log.error("Ground not ready or occupied.")
            return False
            
        plant_id = self.item_id.replace("_seeds", "")
        Log.info(f"Planting {plant_id}...")
        
        target.level.spawn_plant(plant_id, target.grid_x, target.grid_y, group)
        self.count -= 1
        return True

class FoodItem(Item):
   def use(self, player: Player, target: Tile | Entity | None, interactables: Interactables, group: CameraGroup) -> bool:
        if self.count <= 0: 
            return False
        Log.info(f"Yum! Ate {self.name} for {self.data.energy_gain} energy.")
        self.count -= 1
        return True

# --- THE FACTORY ---

_LOGIC_MAP = {
    ItemCategory.TOOL:  ToolItem,
    ItemCategory.SEED:  SeedItem,
    ItemCategory.FRUIT: FoodItem,
    ItemCategory.CROP:  FoodItem,
    ItemCategory.MISC:  Item
}

def create_item(item_id: str, count: int = 1) -> Item:
    """ The unified way to spawn items using the Database and Logic Mapping. """
    data = ASSETS.item(item_id)
    
    # Use the Category from the Unified Enum to pick the class
    target_class = _LOGIC_MAP.get(data.category, Item)
    
    return target_class(item_id, count, preloaded_data=data)