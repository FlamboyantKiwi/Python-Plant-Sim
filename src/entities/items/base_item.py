from __future__ import annotations
import pygame
from src.core.asset_loaders import ASSETS
from src.core.types import ItemCategory
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.entities import Player, Entity
    from src.groups import CameraGroup
    from src.custom_types import Interactables
    from world.tiles import Tile

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
        from .item_factory import create_item
        return create_item(self.item_id, 1)
    