from __future__ import annotations
import pygame
from dataclasses import dataclass
from typing import NamedTuple, TYPE_CHECKING, TypeVar, Generic

if TYPE_CHECKING:
    from src.custom_types import Colour
    from src.core.states import GameState

from .enums import ItemCategory, ToolType, EntityState, Direction
from .geometry import SpriteRect, AnimationGrid


class EntityConfig(NamedTuple):
    """Blueprint for registering a new entity type."""
    sheets: list[str]   # List of filenames (e.g. ["Fox", "Cat"])
    animations: dict[EntityState, AnimationGrid]
    frame_size: int = 32
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
    def calculate_sell_price(self) -> int:
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

    def get_stage_index(self, current_age: float, is_harvested:bool = False) -> int:
        """Calculates the correct image index based on age and harvest state."""

        # --- TREES (5 Frames) ---
        if self.is_tree:
            if is_harvested: return 3 # Stump / Empty branches
            if current_age >= self.grow_time: return 4 # Mature with fruit
            # Growing stages: 0, 1, 2, 3
            stage = int((current_age / self.grow_time) * 4)
            return min(stage, 3)
            
        # --- REGROWING CROPS (4 Frames) ---
        # e.g., Red Pepper
        if self.regrows:
            if is_harvested: return 2 # Returns to the 'no-fruit' stage after harvest
            if current_age >= self.grow_time: return 3 # Mature (Wait for player input)
            # Growing stages: 0, 1, 2
            stage = int((current_age / self.grow_time) * 3)
            return min(stage, 2)
            
        # --- SINGLE HARVEST CROPS (4 Frames) ---
        # e.g., Onion, Beet, Mushroom
        if is_harvested: return 3 # Harvested/Dead/Empty ground
        if current_age >= self.grow_time: return 2 # Mature (Wait for player input)
        # Growing stages: 0, 1
        stage = int((current_age / self.grow_time) * 2)
        return min(stage, 1)

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
        from src.core.asset_loaders import ASSETS
        
        # Get the heavy Font object from the Loader (cached)
        font = ASSETS.font(self)
        
        # Render the text
        col = custom_colour if custom_colour else self.colour
        
        if isinstance(col, str):
            col = ASSETS.colour(col)

        return font.render(text, self.antialias, col)
    
T = TypeVar("T", bound="GameState")

class StateStack(Generic[T]):
    def __init__(self):
        self._stack: list[T] = []

    def push(self, state: T) -> None:
        if self._stack:
            self._stack[-1].exit_state()
        self._stack.append(state)
        state.enter_state()

    def pop(self) -> T | None:
        if not self._stack:
            return None
        top = self._stack.pop()
        top.exit_state()
        if self._stack:
            self._stack[-1].enter_state()
        return top

    def change(self, state: T) -> None:
        while self._stack:
            self._stack.pop().exit_state()
        self._stack.append(state)
        state.enter_state()

    def peek(self) -> T | None:
        return self._stack[-1] if self._stack else None

    def update(self, dt) -> None:
        if not self._stack:
            return
        
        current = self._stack[-1]
        current.update(dt, is_paused=False)

        # Cascade updates downwards until a state suppresses them
        idx = len(self._stack) - 1
        while idx > 0 and not self._stack[idx].suppress_update:
            idx -= 1
            self._stack[idx].update(dt, is_paused=True)

    def draw(self, screen: pygame.Surface) -> None:
        if not self._stack:
            return

        start_idx = len(self._stack) - 1
        while start_idx > 0 and self._stack[start_idx].transparent:
            start_idx -= 1
        
        for i in range(start_idx, len(self._stack)):
            self._stack[i].draw(screen)

    def __len__(self):
        return len(self._stack)
    
