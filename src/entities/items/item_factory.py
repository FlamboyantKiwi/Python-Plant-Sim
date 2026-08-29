from __future__ import annotations

from src.core import ASSETS, ItemCategory

from .base_item import Item
from .food_item import FoodItem
from .seed_item import SeedItem
from .tool_item import ToolItem

_LOGIC_MAP = {
    ItemCategory.TOOL: ToolItem,
    ItemCategory.SEED: SeedItem,
    ItemCategory.FRUIT: FoodItem,
    ItemCategory.CROP: FoodItem,
    ItemCategory.MISC: Item,
}

def create_item(item_id: str, count: int = 1) -> Item:
    """ The unified way to spawn items using the Database and Logic Mapping. """
    data = ASSETS.item(item_id)
    
    # Use the Category from the Unified Enum to pick the class
    target_class = _LOGIC_MAP.get(data.category, Item)
    
    return target_class(item_id, count, preloaded_data=data)