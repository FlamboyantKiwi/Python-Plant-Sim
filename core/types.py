from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

# ============ ENUMS ============ #
class EntityState(Enum):
    WALK = "Walk"; IDLE = "Idle"; RUN = "Run"

class Direction(Enum):
    DOWN = "Down"; RIGHT = "Right"; LEFT = "Left"; UP = "Up"
DOWN, RIGHT, LEFT, UP = Direction.DOWN, Direction.RIGHT, Direction.LEFT, Direction.UP

class ItemCategory(Enum):
    SEED = "seed"
    TOOL = "tool"
    CROP = "crop"
    FRUIT = "fruit" # If you treat fruit distinct from crop
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
    DAGGER = "dagger" # Can also cover KNIFE
    BOW = "bow"
    STAFF = "staff"   # Magic?
    
    # Misc
    HAMMER = "hammer"
    SCYTHE = "scythe"
    SHOVEL = "shovel"
    
    # Fallback
    GENERIC = "generic"

class FontType(Enum):
    HUD = "HUD"
    SLOT = "SLOT"

# ============ GEOMETRY ============ #
@dataclass(frozen=True)
class SpriteRect:
    """Defines a basic region on a sprite sheet."""
    x: int; y: int; w: int; h: int

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
        
        # 1. Calculate slice dimensions
        step_h = rect.h // count if is_vertical else rect.h
        step_w = rect.w // count if not is_vertical else rect.w
        
        # 2. Slice and populate self
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

@dataclass
class ItemData:
    """ The Master Schematic for any item in the game."""
    name: str
    description: str
    category: ItemCategory
    image_key: str 
    
    #Economy
    buy_price: int
    sell_price: int|None = None

    # Inventory Flags
    stackable: bool = True
    max_stack: int = 99
    
    # Gameplay Stats
    energy_gain: int = 0        # For eating
    grow_time: int = 0          # For seeds (days)
    tool_type: ToolType|None = None  # "hoe", "water", etc.
def __post_init__(self):
    # Runs after __init__ 
    # used to calculate defaults based on other fields
    if self.sell_price == None:
        self.sell_price = self.buy_price // 2
@dataclass(frozen=True)
class ShopData:
    store_name:str # Title show at top of store (e.g. General Store)
    items_ids:list[str] # list of items that can be sold here
