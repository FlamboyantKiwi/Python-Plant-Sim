from __future__ import annotations
import pygame
from dataclasses import dataclass
from typing import NamedTuple, TYPE_CHECKING

from .enums import ItemCategory, ToolType, EntityState, Direction
from .geometry import SpriteRect, AnimationGrid

if TYPE_CHECKING:
    from custom_types import Colour

@dataclass(frozen=True)
class CropVisualData:
    """Holds ONLY the rendering coordinates for crops, no gameplay stats."""
    container: SpriteRect
    fruit: SpriteRect
    world_art: SpriteRect
    is_tree: bool = False

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
    colour: Colour = "TEXT"
    bold: bool = False
    italic: bool = False
    antialias: bool = True

    def render(self, text: str, custom_colour: Colour | None = None) -> pygame.Surface:
        """Asks AssetLoader for the cached font, resolves the colour, then renders."""
        # Local import avoids circular dependency errors at startup
        from core.assets import ASSETS
        
        # Get the heavy Font object from the Loader (cached)
        font = ASSETS.font(self)
        
        # Render the text
        col = custom_colour if custom_colour else self.colour
        
        if isinstance(col, str):
            col = ASSETS.colour(col)

        return font.render(text, self.antialias, col)