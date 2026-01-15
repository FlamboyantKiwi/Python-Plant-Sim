from abc import ABC, abstractmethod
from core.helper import get_image, load_image
from core.asset_loader import AssetLoader
from Assets.asset_data import get_item_data, ItemData
from copy import copy

Default_colour = (150, 150, 150)

class Item:
    def __init__(self, item_id: str, count: int = 1):
        # 1. Load the Static Data (The Definition)
        self.data: ItemData = get_item_data(item_id)
        
        # 2. Set Variable State (The Inventory Instance)
        # Cap count at stack size immediately
        self.count = min(count, self.data.max_stack)
        
        # 3. Auto-Load Image based on Data
        self.image = AssetLoader.get_item_image(self.data)

    # --- PROPERTIES (Proxies to the Data) ---
    # This allows you to do item.name instead of item.data.name
    @property
    def name(self): return self.data.name
    
    @property
    def stack_size(self): return self.data.max_stack
    
    @property
    def sell_value(self): return self.data.sell_value

    # --- INVENTORY LOGIC ---
    def add_to_stack(self, amount):
        space = self.stack_size - self.count
        to_add = min(amount, space)
        self.count += to_add
        return amount - to_add # Returns leftover amount

    def remove_from_stack(self, amount):
        if amount >= self.count:
            taken = self.count
            self.count = 0
            return taken
        self.count -= amount
        return amount

    def use(self, player, target_tile, all_tiles):
        """Default behavior: Do nothing."""
        return False
        
    def copy_one(self):
        """Creates a new instance with count 1 (Useful for UI dragging)"""
        # We create a fresh instance using the ID to ensure clean state
        return ItemFactory.create(self.data.name.lower().replace(" ", "_"), 1)
# --- SUBCLASSES ---
# We only subclass if there is custom BEHAVIOR (methods), not custom DATA.

class ToolItem(Item):
    TOOL_DISPATCH = {
        "hoe":   "_use_hoe",
        "water": "_use_water",
        "axe":   "_use_axe",
        "pick":  "_use_pickaxe"
    }
    def use(self, player, target_tile, all_tiles):
        if not target_tile: return False
        
        # Get the tool type string (e.g., "hoe")
        t_type = self.data.tool_type 
        
        if not t_type:
            print(f"Error: {self.name} is a tool but has no tool_type defined.")
            return False
        
        # Look up the handler name (e.g., "_use_hoe")
        handler_name = self.TOOL_DISPATCH.get(t_type)
        
        if handler_name:
            # Dynamically get the method from 'self' and call it
            handler_func = getattr(self, handler_name)
            return handler_func(player, target_tile, all_tiles)
            
        print(f"No handler defined for tool type: {t_type}")
        return False

    def _use_hoe(self, tile):
        print(f"Hoeing {tile}...")
        return True

    def _use_water(self, tile):
        print(f"Watering {tile}...")
        return True

    def _use_axe(self, tile):
        print("Chop chop")
        return True
    
    def _use_pickaxe(self, player, tile, all_tiles):
        print("Breaking stone...")
        return True

class SeedItem(Item):
    def use(self, player, target_tile, all_tiles):
        if not target_tile: return False
        
        print(f"Planting {self.name} which takes {self.data.grow_time} days.")
        # Logic: check if tile is tilled -> place plant -> reduce count
        self.count -= 1
        return True

class FoodItem(Item):
    def use(self, player, target_tile, all_tiles):
        print(f"Yum! Ate {self.name} for {self.data.energy_gain} energy.")
        # use for energy or sell?
        self.count -= 1
        return True

# --- THE FACTORY ---

CLASS_MAPPING = {
    "tool": ToolItem,
    "seed": SeedItem,
    "crop": FoodItem,
    "food": FoodItem, # Allow alias
    "misc": Item}      # Default

class ItemFactory:
    @staticmethod
    def create(item_id: str, count: int = 1):
        """ Creates the correct class instance based on the ItemData category.
        Input: "tomato_seeds"
        Output: SeedItem Instance with correct image and stats."""
        data = get_item_data(item_id)
        
        target_class = CLASS_MAPPING.get(data.category, Item) 
        
        # 3. Instantiate
        return target_class(item_id, count)