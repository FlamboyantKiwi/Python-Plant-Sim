import pygame
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


# ============ ENUMS ============ #
class EntityState(Enum):
    WALK = "Walk"
    IDLE = "Idle"
    RUN = "Run"

class Direction(Enum):
    DOWN = "Down"
    RIGHT = "Right"
    LEFT = "Left"
    UP = "Up"
DOWN, RIGHT, LEFT, UP = Direction.DOWN, Direction.RIGHT, Direction.LEFT, Direction.UP

class ItemType(Enum):
    # --- Tools ---
    TOOL         = ("tool", "generic")
    HOE          = ("tool", "hoe")
    WATERING_CAN = ("tool", "water")
    AXE          = ("tool", "axe")
    PICKAXE      = ("tool", "pick")
    SWORD        = ("tool", "sword")
    SCYTHE       = ("tool", "scythe") 
    ROD          = ("tool", "rod")
    # Combat
    DAGGER       = ("tool", "dagger")
    BOW          = ("tool","bow")
    STAFF        = ("tool","staff")
    # Misc
    HAMMER       = ("tool","hammer")
    SHOVEL       = ("tool","shovel")

    # --- Consumables ---
    SEED         = ("seed", "none")
    FRUIT        = ("fruit", "none")
    CROP         = ("crop", "none")
    
    # --- Resources ---
    WOOD         = ("misc", "none")
    STONE        = ("misc", "none")
    GENERIC      = ("misc", "none")

    def __init__(self, category: str, use_id: str):
        self.category = category
        self.use_id = use_id

class ItemCategory(Enum):
    SEED = "seed"
    TOOL = "tool"
    CROP = "crop"
    FRUIT = "fruit" 
    MISC = "misc"

class ToolType(Enum):
    # Farming
    HOE = "hoe"
    WATER = "water"
    # Gathering
    AXE = "axe"
    PICKAXE = "pick"
    ROD = "rod"
    # Combat
    SWORD = "sword"
    DAGGER = "dagger"
    BOW = "bow"
    STAFF = "staff"
    # Misc
    HAMMER = "hammer"
    SCYTHE = "scythe"
    SHOVEL = "shovel"
    # Fallback
    GENERIC = "generic"
    
class Material(Enum):
    WOOD = "WOOD"
    COPPER = "COPPER"
    IRON = "IRON"
    GOLD = "GOLD"

class Quality(Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"

class FontType(Enum):
    HUD = "HUD"
    SLOT = "SLOT"

# ============ GEOMETRY ============ #
@dataclass(frozen=True)
class SpriteRect:
    """Defines a basic region on a sprite sheet."""
    x: int
    y: int
    w: int
    h: int

@dataclass(frozen=True)
class ScaleRect(SpriteRect):
    """Defines a region containing multiple tiles of a specific size."""
    tile_w: int
    tile_h: int

@dataclass(frozen=True)
class RectPair:
    """ Used for Fruits.
    a: The Fruit Strip (3 frames: Gold, Silver, Bronze)
    b: The Container (Crate/Basket) """
    a: SpriteRect
    b: SpriteRect

@dataclass(frozen=True)
class CropVisualData:
    """Holds ONLY the rendering coordinates for crops, no gameplay stats."""
    container: SpriteRect
    fruit: SpriteRect
    world_art: SpriteRect
    is_tree: bool = False

@dataclass
class AnimationGrid(dict):
    """ A dictionary-like object that auto-slices a SpriteRect into directions.
        It behaves exactly like dict[Direction, SpriteRect]."""
    def __init__(self, rect: SpriteRect, directions: list[Direction]|None = None, is_vertical: bool = True):
        super().__init__() # Initialize the underlying dict
        if directions is None:
            for d in Direction:
                self[d] = rect
            return
        count = len(directions)
        
        if count == 0: # Empty List: Default to DOWN
            self[Direction.DOWN] = rect
            return
        
        # Calculate slice dimensions
        step_h = rect.h // count if is_vertical else rect.h
        step_w = rect.w // count if not is_vertical else rect.w
        
        # Slice and populate self
        for i, direction in enumerate(directions):
            new_x = rect.x + (i * step_w if not is_vertical else 0)
            new_y = rect.y + (i * step_h if is_vertical else 0)
            
            # This assigns the key/value into the dictionary itself
            self[direction] = SpriteRect(new_x, new_y, step_w, step_h)
    @classmethod
    def non_directional(cls, rect:SpriteRect, assign_to_all:bool = True):
        """Creates an animation entry for non-directional actions (e.g., Death).
        
        assign_to_all: 
            If True, maps the SAME rect to Down, Up, Left, Right.
            (Useful if you want the same anim to play regardless of facing).
            If False, maps only to Direction.DOWN. """
        instance = cls(rect, [], True) # Empty init
        
        if assign_to_all:
            # Map the same rectangle to all directions so lookups never fail
            for d in Direction:
                instance[d] = rect
        else:
            # Just map to Down (default)
            instance[Direction.DOWN] = rect
            
        return instance

class EntityConfig(NamedTuple):
    """Blueprint for registering a new entity type."""
    folder: str         # Folder name (e.g. "Player")
    sheets: list[str]   # List of filenames (e.g. ["Fox", "Cat"])
    animations: dict[EntityState, AnimationGrid]
    def get_animation(self, state:EntityState) -> dict[Direction, SpriteRect]:
        return self.animations.get(state, {})

@dataclass(frozen=True)
class ItemData:
    """ The Master Schematic for any item in the game."""
    name: str
    description: str
    category: ItemCategory
    image_key: str 
    buy_price: int
    # optional Fields
    
    sell_price: int|None = None
    stackable: bool = True
    max_stack: int = 99
    
    # Gameplay Stats
    energy_gain: int = 0        # For eating
    grow_time: int = 0          # For seeds (days)
    tool_type: ToolType|None = None
    @property
    def get_sell_price(self) -> int:
        """Dynamically calculates sell price if one wasn't explicitly set."""
        if self.sell_price is not None:
            return self.sell_price
        return self.buy_price // 2

@dataclass
class PlantData:
    name:str
    grow_time:int       # Total days to reach harvest
    harvest_item:str    # The Item ID produced (e.g., "apple")

    image_stages: int          # Count of frames (needed for math)
    image_rect: SpriteRect     # The sprite sheet location (needed for drawing)

    is_tree: bool = False # True = Tree behavior (collision?), False = Crop (walkable)
    regrows: bool = False # True = Returns to previous stage after harvest (like berries)

    def get_stage_index(self, current_age: float) -> int:
        """Calculates the correct image index based on age."""
        #Prevent division by 0
        if self.grow_time <= 0:
            return self.image_stages - 1
        # Ready to Harvest?
        if current_age >= self.grow_time:   
            return self.image_stages - 1

        # Calculate percentage of growth
        growth_percent = current_age / self.grow_time
        growing_stage_count = self.image_stages - 1
        
        stage = int(growth_percent * growing_stage_count)
        
        # Clamp to ensure we don't exceed the second-to-last stage
        return min(stage, growing_stage_count - 1)

@dataclass(frozen=True)
class ShopData:
    store_name:str # Title show at top of store (e.g. General Store)
    items_ids:list[str] # list of items that can be sold here

    
@dataclass
class TextConfig:
    """Defines the styling for a specific type of text."""
    size: int = 20
    name: str = "arial"
    colour: tuple = (255, 255, 255)
    bold: bool = False
    italic: bool = False
    antialias: bool = True

    def render(self, text: str, custom_colour=None) -> pygame.Surface:
        """Convenience method: Asks AssetLoader for the cached font, then renders."""
        # Local import avoids circular dependency errors at startup
        from core.asset_loader import ASSETS
        
        # 1. Get the heavy Font object from the Loader (cached)
        font = ASSETS.get_font(self)
        
        # 2. Render the text
        col = custom_colour if custom_colour else self.colour
        return font.render(text, self.antialias, col)