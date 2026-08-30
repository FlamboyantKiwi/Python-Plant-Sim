from __future__ import annotations

from src.core import ASSETS, ItemCategory

from .base_item import Item
from .food_item import FoodItem
from .seed_item import SeedItem
from .tool_item import ToolItem

LOGIC_MAP = {
    ItemCategory.TOOL: ToolItem,
    ItemCategory.SEED: SeedItem,
    ItemCategory.FRUIT: FoodItem,
    ItemCategory.CROP: FoodItem,
    ItemCategory.MISC: Item,
}

class ItemFactory:
    """The unified factory for spawning data-driven items."""
    @classmethod
    def create(cls, item_id: str, count: int = 1) -> Item:
        data = ASSETS.item(item_id)
        
        # Use the Category from the Unified Enum to pick the class
        target_class = LOGIC_MAP.get(data.category, Item)
        
        return target_class(item_id, count, preloaded_data=data)