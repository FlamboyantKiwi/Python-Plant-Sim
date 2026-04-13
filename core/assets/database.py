from __future__ import annotations
from typing import TYPE_CHECKING
from .base import AssetGroup
from core.database import DatabaseManager
from core.types import ItemData, ItemCategory, PlantData, SpriteRect, ShopData

if TYPE_CHECKING:
    from core.assets import AssetLoader

class DatabaseGroup(AssetGroup):
    """Manages the SQLite connection and handles fallback logic for missing data."""
    def __init__(self, manager: AssetLoader) -> None:
        super().__init__(manager)
        self.db = DatabaseManager()
        self.missing_ids = set()

    def load(self) -> None: pass

    def clean_up(self) -> None:
        """Closes the SQLite connection when the game exits."""
        self.db.close()
    
    def _log_missing(self, entity_type: str, entity_id: str) -> None:
        """Helper to log missing IDs exactly once without repeating code."""
        if entity_id not in self.missing_ids:
            print(f"[{self.__class__.__name__}] VALUE ERROR: Missing {entity_type} ID '{entity_id}'! Using Fallback.")
            self.missing_ids.add(entity_id)

    def get_item(self, item_id: str) -> ItemData:
        """Safely fetches an item, returning a glitch item if it's missing."""
        data = self.db.get_item_data(item_id)
        if data is not None:
            return data
            
        self._log_missing("Item", item_id)
            
        return ItemData(
            name="Glitch Item",
            description=f"Error: '{item_id}' is missing from DB.",
            category=ItemCategory.MISC,
            image_key=item_id, 
            buy_price=0, sell_price=0
        )

    def get_plant(self, plant_id: str) -> PlantData:
        data = self.db.get_plant_data(plant_id)
        if data is not None:
            return data
            
        self._log_missing("Plant", plant_id)
            
        return PlantData(
            name="Glitch Plant", 
            grow_time=1, 
            harvest_item="error", 
            image_stages=1, 
            image_rect=SpriteRect(0,0,16,16), 
            is_tree=False, 
            regrows=False
        )

    def get_shop(self, shop_id: str) -> ShopData:
        data = self.db.get_shop_data(shop_id)
        if data is not None:
            return data
            
        self._log_missing("Shop", shop_id)
            
        return ShopData(
            store_name="Glitch Mart", 
            items_ids=[]
        )

    def debug_print(self) -> None:
        super().debug_print()
        try:
            # Query the database to see exactly how much data is loaded!
            items_cnt = self.db.cursor.execute("SELECT COUNT(*) FROM items").fetchone()[0]
            plants_cnt = self.db.cursor.execute("SELECT COUNT(*) FROM plants").fetchone()[0]
            shops_cnt = self.db.cursor.execute("SELECT COUNT(*) FROM shops").fetchone()[0]
            print(f" Loaded: {items_cnt} Items, {plants_cnt} Plants, {shops_cnt} Shops")
        except Exception:
            print(" Database connection unavailable.")
            
        if self.missing_ids:
            print(f"MISSING IDs ({len(self.missing_ids)}):")
            for key in sorted(self.missing_ids):
                print(f"  [X] {key}")
        self.print_line_break()
