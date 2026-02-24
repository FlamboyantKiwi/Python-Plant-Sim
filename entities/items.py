from core.asset_loader import AssetLoader
from Assets.asset_data import get_item_data, ItemData
from core.types import ItemCategory

Default_colour = (150, 150, 150)

class Item:
    def __init__(self, item_id: str, count: int = 1):
        self.data: ItemData = get_item_data(item_id)
        self.count = min(count, self.data.max_stack)
        self.image = AssetLoader.get_item_image(self.data)

    # --- PROPERTIES (Proxies to the Data) ---
    # This allows us to do item.name instead of item.data.name
    @property
    def name(self):         return self.data.name
    
    @property
    def stack_size(self):   return self.data.max_stack
    
    @property
    def sell_value(self):   return self.data.sell_price

    @property
    def stackable(self):    return self.data.stackable

    # --- INVENTORY LOGIC ---
    def add_to_stack(self, amount) -> int:
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

    def use(self, player, target_tile, all_tiles, group) -> bool:
        """Default behavior: Do nothing."""
        return False
        
    def copy_one(self):
        """Creates a new instance with count 1 (Useful for UI dragging)"""
        # We create a fresh instance using the ID to ensure clean state
        return ItemFactory.create(self.data.name.lower().replace(" ", "_"), 1)
# --- SUBCLASSES ---
# We only subclass if there is custom BEHAVIOR (methods), not custom DATA.

class ToolItem(Item):
    def use(self, player, target_tile, all_tiles, group):
        if not target_tile: 
            return False
        
        # Get the tool type string (e.g., "hoe")
        t_type = self.data.tool_type 
        
        if not t_type:
            print(f"Error: {self.name} is a tool but has no tool_type defined.")
            return False
        
        # Look up the handler name (e.g., "_use_hoe")
        method_name = f"_use_{t_type.name.lower()}"
        
        if hasattr(self, method_name):
            # Get the method and call it
            method = getattr(self, method_name)
            return method(player, target_tile, all_tiles, group)
            
        print(f"ToolItem Error: Method '{method_name}' not implemented for {self.name}.")
        return False

    def _use_hoe(self, player, tile, all_tiles, group):
        # Can only till tillable ground (Dirt/Grass)
        if not getattr(tile, 'tillable', False):
            print("You can't till this ground!")
            return False
            
        # If it's already tilled, don't waste the action
        if getattr(tile, 'is_tilled', False):
            return False
            
        print(f"Tilled the soil at {tile.grid_x}, {tile.grid_y}!")
        
        # Set the farming flag so seeds know this tile is ready!
        tile.is_tilled = True
        
        # Tell the Level to update the Marching Squares map and refresh the visuals
        if hasattr(tile, 'level'):
            tile.level.till_map_node(tile.grid_x, tile.grid_y)
        else:
            print("Warning: Tile doesn't have a reference to the Level!")
        
        return True

    def _use_watering_can(self, player, tile, all_tiles, group):
        print(f"Watering {tile}...")
        return True

    def _use_axe(self, player, tile, all_tiles, group):
        print("Chop chop")
        return True
    
    def _use_pickaxe(self, player, tile, all_tiles, group):
        print("Breaking stone...")
        return True

class SeedItem(Item):
    def use(self, player, target_tile, all_tiles, group):
        if self.count <= 0: 
            return False
        if not target_tile: 
            return False
        
        # Check if the tile is ready for a seed
        if not getattr(target_tile, 'is_tilled', False):
            print("You must till the dirt with a hoe first!")
            return False
            
        # Check if something is already planted here
        if target_tile.occupant is not None:
            print("Something is already growing here!")
            return False
            
        # Figure out the plant name. 
        # (e.g., If item is "Apple Seed", we just want "Apple" for the Plant class)
        plant_name = self.data.name.replace(" Seeds", "").replace(" Seed", "")
        print(f"Planting {plant_name}...")
        
        target_tile.level.spawn_plant(plant_name, target_tile.grid_x, target_tile.grid_y, group)
        
        # Consume the seed
        self.count -= 1
        return True

class FoodItem(Item):
    def use(self, player, target_tile, all_tiles, group):
        if self.count <= 0: 
            return False
        print(f"Yum! Ate {self.name} for {self.data.energy_gain} energy.")
        # use for energy or sell?
        self.count -= 1
        return True

# --- THE FACTORY ---

CLASS_MAPPING = {
    ItemCategory.TOOL:  ToolItem,
    ItemCategory.SEED:  SeedItem,
    ItemCategory.CROP:  FoodItem,
    ItemCategory.FRUIT: FoodItem,
    ItemCategory.MISC:  Item    } # Default Item


class ItemFactory:
    @staticmethod
    def create(item_id: str, count: int = 1)-> Item:
        """ Creates the correct class instance based on the ItemData category.
        Input: "tomato_seeds"
        Output: SeedItem Instance with correct image and stats."""
        data = get_item_data(item_id)
        
        target_class = CLASS_MAPPING.get(data.category, Item) 
        
        # 3. Instantiate
        return target_class(item_id, count)