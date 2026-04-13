import pygame
from core.assets import ASSETS
from core.types import ItemCategory
from typing import Any

class Item:
    """ Base class for an inventory item. 
    Manages stack counts and proxies core data from the SQLite database. """
    def __init__(self, item_id: str, count: int = 1, preloaded_data: Any = None):
        # OPTIMIZATION: Use preloaded data from the factory if available
        self.data = preloaded_data or ASSETS.item(item_id)
        self.count:int = min(count, self.data.max_stack)
        self.image: pygame.Surface = ASSETS.item_image(self.data)
        self.item_id: str = item_id

    # --- PROPERTIES (Proxies to the Data) ---
    def __getattr__(self, attr_name: str):
        """ Magic Proxy: Routes missing attribute requests (like .name or .buy_price)
        directly to the underlying ItemData object."""
        # SAFETY CHECK: Ignore Python's internal dunder methods and prevent recursion on 'data'
        if attr_name.startswith('__') and attr_name.endswith('__') or attr_name == 'data':
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr_name}'")
        try:
            return getattr(self.data, attr_name)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' and its data have no attribute '{attr_name}'")

    # --- INVENTORY LOGIC ---
    def add_to_stack(self, amount: int) -> int:
        """Adds to the current stack and returns any leftover amount."""
        to_add = min(amount, self.stack_size - self.count)
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

    def use(self, player, target_tile, all_tiles, group: pygame.sprite.AbstractGroup) -> bool:
        """Default behavior for unusable items (e.g., Wood, Stone). Returns True if action succeeded."""
        return False
        
    def copy_one(self) -> 'Item':
        """Creates a new instance with a count of 1 (Useful for UI dragging)."""
        return create_item(self.item_id, 1)
    
# --- SUBCLASSES ---
# We only subclass if there is custom BEHAVIOR (methods), not custom DATA.
class ToolItem(Item):
    """Handles logic for persistent, non-consumable tools (Hoe, Axe, Sword)."""
    def use(self, player, target_tile, all_tiles, group: pygame.sprite.AbstractGroup) -> bool:
        if not target_tile: 
            return False
        
        t_type = self.tool_type
        if not t_type:
            return self._use_generic(player, target_tile, all_tiles, group)
        
        # Dynamically build the method name (e.g., _use_hoe)
        method_name = f"_use_{t_type.name.lower()}"
        use_func = getattr(self, method_name, self._use_generic)
        
        return use_func(player, target_tile, all_tiles, group)
    
    def _use_generic(self, player, target_tile, all_tiles, group: pygame.sprite.AbstractGroup) -> bool:
        """Fallback for tools with no specific logic yet."""
        return False

    def _use_hoe(self, player, tile, all_tiles, group: pygame.sprite.AbstractGroup) -> bool:
        """Tills the soil if it is valid ground."""
        if not getattr(tile, 'tillable', False) or getattr(tile, 'is_tilled', False):
            print("You can't till this ground!")
            return False
            
        print(f"Tilled the soil at {tile.grid_x}, {tile.grid_y}!")
        tile.is_tilled = True
        
        if not hasattr(tile, 'level'):
            print("Warning: Tile doesn't have a reference to the Level!")
            return False
        tile.level.till_map_node(tile.grid_x, tile.grid_y)            
            
        return True

    def _use_water(self, player, tile, all_tiles, group: pygame.sprite.AbstractGroup):
        print(f"Watering {tile.grid_x}, {tile.grid_y}...")
        return True

    def _use_axe(self, player, tile, all_tiles, group: pygame.sprite.AbstractGroup):
        print("Chop chop")
        return True
    
    def _use_pickaxe(self, player, tile, all_tiles, group: pygame.sprite.AbstractGroup):
        print("Breaking stone...")
        return True

class SeedItem(Item):
    """Handles planting logic and consumes 1 stack count upon success."""
    def use(self, player, target_tile, all_tiles, group: pygame.sprite.AbstractGroup):
        if self.count <= 0 or not target_tile: 
            return False
        
        # Check if the tile is ready for a seed
        if not getattr(target_tile, 'is_tilled', False) or target_tile.occupant:
            print("Ground not ready or occupied.")
            return False
            
        # Figure out the plant name. 
        plant_id = self.item_id.replace("_seeds", "")
        print(f"Planting {plant_id}...")
        
        target_tile.level.spawn_plant(plant_id, target_tile.grid_x, target_tile.grid_y, group)
        # Consume the seed
        self.count -= 1
        return True

class FoodItem(Item):
    def use(self, player, target_tile, all_tiles, group: pygame.sprite.AbstractGroup):
        if self.count <= 0: 
            return False
        print(f"Yum! Ate {self.name} for {self.data.energy_gain} energy.")
        # use for energy or sell?
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