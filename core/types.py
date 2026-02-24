import pygame
from dataclasses import dataclass
from abc import ABC, abstractmethod
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

@dataclass
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
    def __post_init__(self):
        # Runs after __init__ 
        # used to calculate defaults based on other fields
        if self.buy_price and self.sell_price is None:
            self.sell_price = self.buy_price // 2

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

# Config / Factories

@dataclass(frozen=True)
class CropConfig:
    """ Configuration blueprint for a specific crop/tree. 
    Replaces the dictionary logic in CROP_BALANCE."""
    seed_price: int
    crop_price: int
    grow_time: int
    energy: int
    # Optional
    is_tree: bool = False
    regrows: bool = False

    @property
    def stages(self) -> int:
        """ Calculates stage count based on what the plant IS. """
        if self.is_tree: 
            return 5
        return 4 # Default for standard vegetables
    
    def generate_seed_data(self, name: str, image_key: str) -> ItemData:
        """Generates the Seed definition"""
        return ItemData(
            name=f"{name} Seeds",
            description=f"Plant these to grow {name}. Takes {self.grow_time} days.",
            category=ItemCategory.SEED,
            image_key=image_key,
            buy_price=self.seed_price,
            grow_time=self.grow_time
        )
    def generate_crop_data(self, name: str, image_key: str) -> ItemData:
        """Generates the Fruit/Veggie definition"""
        return ItemData(
            name=name,
            description=f"Fresh {name}. Restores {self.energy} energy.",
            category=ItemCategory.CROP,
            image_key=image_key,
            buy_price=self.crop_price,
            energy_gain=self.energy
        )

    def generate_plant_data(self, name: str, harvest_id: str) -> PlantData:
        """Generates the Logic definition"""
        return PlantData(
            name=name,
            grow_time=self.grow_time,
            harvest_item=harvest_id,
            image_stages=self.stages,
            image_rect=SpriteRect(0,0,0,0), # to prevent errors between change-over
            is_tree=self.is_tree,
            regrows=self.regrows
        )

@dataclass(frozen=True)
class ItemIdentity:
    """Helper class to hold the generated text/ID for an item."""
    name: str
    description: str
    item_id: str

@dataclass
class ItemBlueprint(ABC):
    """Abstract Base Class for generating items."""
    sprite_suffix: str
    base_cost: int
    tool_type: ToolType = ToolType.GENERIC
    category: ItemCategory = ItemCategory.TOOL
    stackable: bool = False

    @abstractmethod
    def get_details(self, material: str) -> ItemIdentity:
        """Returns (Item Name, Description, Item ID)"""
        pass

    def generate(self, material: str, multiplier: int) -> tuple[str, 'ItemData']:
        """ Standard generation logic used by ALL subclasses."""
        identity = self.get_details(material)
        price = int(self.base_cost * multiplier)
        
        # Return the ID and the Object
        return identity.item_id, ItemData(name=identity.name, description=identity.description, category=self.category, image_key=f"{material}_{self.sprite_suffix}", 
            buy_price=price, tool_type=self.tool_type, stackable=self.stackable)

# --- SUBCLASSES ---

@dataclass
class ToolBP(ItemBlueprint):
    """Handles Axes, Hoes, Swords."""
    display_suffix: str = ""
    
    def get_details(self, material: str) -> ItemIdentity:
        suffix = self.display_suffix if self.display_suffix else self.sprite_suffix.replace("_", " ").title()
        
        return ItemIdentity(
            name=f"{material.title()} {suffix}",
            description=f"A {material.lower()} quality {suffix.lower()}.",
            item_id=f"{material.lower()}_{self.sprite_suffix.lower()}"
        )

    def generate(self, material: str, multiplier: int):
        # Tools override generate because they have the "Wood is Free" rule
        item_id, data = super().generate(material, multiplier)
        if material == "WOOD": 
            data.buy_price = 0
        return item_id, data

@dataclass
class MaterialBP(ItemBlueprint):
    """Handles raw wood, iron, etc."""
    category: ItemCategory = ItemCategory.MISC
    stackable: bool = True
    
    def get_details(self, material: str) -> ItemIdentity:
        return ItemIdentity(
            name=material.title(),
            description=f"A raw piece of {material.lower()}.",
            item_id=material.lower()
        )

@dataclass
class ArrowBP(ItemBlueprint):
    """Handles arrows."""
    category: ItemCategory = ItemCategory.MISC
    stackable: bool = True

    def get_details(self, material: str) -> ItemIdentity:
        return ItemIdentity(
            name=f"{material.title()} Arrow",
            description=f"A {material.lower()}-tipped arrow.",
            item_id=f"{material.lower()}_{self.sprite_suffix.lower()}"
        )
    
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
        from core.asset_loader import AssetLoader
        
        # 1. Get the heavy Font object from the Loader (cached)
        font = AssetLoader.get_font(self)
        
        # 2. Render the text
        col = custom_colour if custom_colour else self.colour
        return font.render(text, self.antialias, col)