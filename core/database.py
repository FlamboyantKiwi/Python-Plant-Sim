from __future__ import annotations
import sqlite3
import os
from typing import TYPE_CHECKING, Any

# Runtime Imports: These are needed to instantiate the data objects
from core.types import ItemData, ItemCategory, ToolType, PlantData, ShopData, SpriteRect

# Type Checking Imports
if TYPE_CHECKING:
    from custom_types import Num

class DatabaseManager:

    TABLES = {
        "items": [
            "id TEXT PRIMARY KEY", "name TEXT NOT NULL", "description TEXT",
            "category TEXT NOT NULL", "image_key TEXT NOT NULL",
            "buy_price INTEGER DEFAULT 0", "sell_price INTEGER",
            "stackable BOOLEAN DEFAULT 1", "max_stack INTEGER DEFAULT 99",
            "energy_gain INTEGER DEFAULT 0", "grow_time INTEGER DEFAULT 0", "tool_type TEXT"
        ],
        "plants": [
            "id TEXT PRIMARY KEY", "name TEXT NOT NULL", "grow_time INTEGER",
            "harvest_item TEXT NOT NULL", "image_stages INTEGER",
            "is_tree BOOLEAN", "regrows BOOLEAN",
            "rect_x INTEGER", "rect_y INTEGER", "rect_w INTEGER", "rect_h INTEGER"
        ],
        "shops": [
            "id TEXT PRIMARY KEY", "store_name TEXT NOT NULL"
        ],
        "shop_items": [
            "shop_id TEXT", "item_id TEXT",
            "FOREIGN KEY(shop_id) REFERENCES shops(id)"
        ]
    }

    VIEWS = {
        "view_seeds": "SELECT id, name, description, buy_price, grow_time FROM items WHERE category = 'seed'",
        "view_tools": "SELECT id, name, description, buy_price, tool_type FROM items WHERE category = 'tool'",
        "view_produce": "SELECT id, name, sell_price, energy_gain FROM items WHERE category IN ('crop', 'fruit')"
    }

    def __init__(self, db_path: str = "assets/data/gamedata.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row 
        self.conn.execute("PRAGMA foreign_keys = ON;")

        self.cursor = self.conn.cursor()

    def insert_record(self, table_name: str, data: dict[str, Any]) -> None:
        """ Dynamically builds and executes an INSERT OR REPLACE query. """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        
        query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)

    def setup_tables(self) -> None:
        """Dynamically generates and executes all SQL schema queries."""
        
        # Build and run Table queries
        for table_name, columns in self.TABLES.items():
            column_str = ", ".join(columns)
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_str})"
            self.cursor.execute(query)

        # Build and run View queries
        for view_name, select_stmt in self.VIEWS.items():
            query = f"CREATE VIEW IF NOT EXISTS {view_name} AS {select_stmt}"
            self.cursor.execute(query)

        self.conn.commit()
    
    # --- PRIVATE HELPERS ---

    def _row_to_item(self, row: sqlite3.Row) -> ItemData:
        """Translates a database row into an ItemData object."""
        return ItemData(
            name=row['name'], 
            description=row['description'],
            category=ItemCategory(row['category']), 
            image_key=row['image_key'],
            buy_price=row['buy_price'], 
            sell_price=row['sell_price'],
            stackable=bool(row['stackable']), 
            max_stack=row['max_stack'],
            energy_gain=row['energy_gain'], 
            grow_time=row['grow_time'],
            tool_type=ToolType(row['tool_type']) if row['tool_type'] else None 
        )

    def _row_to_plant(self, row: sqlite3.Row) -> PlantData:
        """Translates a database row into a PlantData object."""
        return PlantData(
            name=row['name'], 
            grow_time=row['grow_time'],
            harvest_item=row['harvest_item'], 
            image_stages=row['image_stages'],
            image_rect=SpriteRect(row['rect_x'], row['rect_y'], row['rect_w'], row['rect_h']), 
            is_tree=bool(row['is_tree']), 
            regrows=bool(row['regrows'])
        )

    # --- PUBLIC GETTERS ---
    
    def get_item_data(self, item_id: str) -> ItemData | None:
        self.cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        return self._row_to_item(row) if (row := self.cursor.fetchone()) else None

    def get_plant_data(self, plant_id: str) -> PlantData | None:
        self.cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
        return self._row_to_plant(row) if (row := self.cursor.fetchone()) else None

    def get_items_by_category(self, category: ItemCategory) -> list[ItemData]:
        """Returns a list of all items that match a specific category."""
        self.cursor.execute("SELECT * FROM items WHERE category = ?", (category.value,))
        return [self._row_to_item(row) for row in self.cursor.fetchall()]

    def get_shop_data(self, shop_id: str) -> ShopData | None:
        self.cursor.execute("SELECT store_name FROM shops WHERE id = ?", (shop_id,))
        if not (shop_row := self.cursor.fetchone()):
            return None
            
        self.cursor.execute("SELECT item_id FROM shop_items WHERE shop_id = ?", (shop_id,))
        # Fetchall gives us rows, we just want the first column of each row
        items_list = [row[0] for row in self.cursor.fetchall()]
        
        return ShopData(store_name=shop_row['store_name'], items_ids=items_list)
    
    def close(self) -> None:
        self.conn.close()