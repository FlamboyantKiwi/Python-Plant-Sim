# core/database.py
import sqlite3
import os
from core.types import ItemData, ItemCategory, ToolType, PlantData, ShopData, SpriteRect

class DatabaseManager:
    def __init__(self, db_path: str = "assets/data/gamedata.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row 
        self.conn.execute("PRAGMA foreign_keys = ON;")

        self.cursor = self.conn.cursor()

    def insert_record(self, table_name: str, data: dict) -> None:
        """ Dynamically builds and executes an INSERT OR REPLACE query.
        :param table_name: The name of the SQL table (e.g., 'items')
        :param data: A dictionary where keys are column names and values are the data.
        """
        # Get the column names (e.g., "id, name, description")
        columns = ", ".join(data.keys())
        
        # Create the exact number of placeholders needed (e.g., "?, ?, ?")
        placeholders = ", ".join(["?"] * len(data))
        
        # Extract the actual values into a tuple
        values = tuple(data.values())
        
        # Build the final SQL string
        query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Execute it
        self.cursor.execute(query, values)

    def setup_tables(self) -> None:
        """Creates all necessary tables for the game."""
        # 1. Items Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT,
                category TEXT NOT NULL, image_key TEXT NOT NULL,
                buy_price INTEGER DEFAULT 0, sell_price INTEGER,
                stackable BOOLEAN DEFAULT 1, max_stack INTEGER DEFAULT 99,
                energy_gain INTEGER DEFAULT 0, grow_time INTEGER DEFAULT 0, tool_type TEXT
            )
        ''')
        
        # 2. Plants Table (Notice the rect columns!)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS plants (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, grow_time INTEGER,
                harvest_item TEXT NOT NULL, image_stages INTEGER,
                is_tree BOOLEAN, regrows BOOLEAN,
                rect_x INTEGER, rect_y INTEGER, rect_w INTEGER, rect_h INTEGER
            )
        ''')
        
        # 3. Shops Tables (Two tables: one for the shop, one for the inventory list)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shops (
                id TEXT PRIMARY KEY, store_name TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                shop_id TEXT, item_id TEXT,
                FOREIGN KEY(shop_id) REFERENCES shops(id)
            )
        ''')

        # --- Create Virtual Views for easy reading in VS Code ---
        
        # 1. A View that only shows Seeds
        self.cursor.execute('''
            CREATE VIEW IF NOT EXISTS view_seeds AS 
            SELECT id, name, description, buy_price, grow_time 
            FROM items WHERE category = 'seed'
        ''')
        
        # 2. A View that only shows Tools
        self.cursor.execute('''
            CREATE VIEW IF NOT EXISTS view_tools AS 
            SELECT id, name, description, buy_price, tool_type 
            FROM items WHERE category = 'tool'
        ''')
        
        # 3. A View that only shows Crops/Fruit
        self.cursor.execute('''
            CREATE VIEW IF NOT EXISTS view_produce AS 
            SELECT id, name, sell_price, energy_gain 
            FROM items WHERE category IN ('crop', 'fruit')
        ''')

        self.conn.commit()

    # --- GETTERS ---
    
    def get_item_data(self, item_id: str) -> ItemData | None:
        self.cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        if row := self.cursor.fetchone():
            return ItemData(
                name=row['name'], description=row['description'],
                category=ItemCategory(row['category']), image_key=row['image_key'],
                buy_price=row['buy_price'], sell_price=row['sell_price'],
                stackable=bool(row['stackable']), max_stack=row['max_stack'],
                energy_gain=row['energy_gain'], grow_time=row['grow_time'],
                tool_type=ToolType(row['tool_type']) if row['tool_type'] else None 
            )
        return None

    def get_plant_data(self, plant_id: str) -> PlantData | None:
        self.cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
        if row := self.cursor.fetchone():
            # Rebuild the SpriteRect from the integers in the database
            rect = SpriteRect(row['rect_x'], row['rect_y'], row['rect_w'], row['rect_h'])
            
            return PlantData(
                name=row['name'], grow_time=row['grow_time'],
                harvest_item=row['harvest_item'], image_stages=row['image_stages'],
                image_rect=rect, is_tree=bool(row['is_tree']), regrows=bool(row['regrows'])
            )
        return None

    def get_shop_data(self, shop_id: str) -> ShopData | None:
        # First, get the shop name
        self.cursor.execute("SELECT * FROM shops WHERE id = ?", (shop_id,))
        shop_row = self.cursor.fetchone()
        
        if not shop_row:
            return None
            
        # Second, fetch all the item IDs linked to this shop
        self.cursor.execute("SELECT item_id FROM shop_items WHERE shop_id = ?", (shop_id,))
        items_list = [row['item_id'] for row in self.cursor.fetchall()]
        
        return ShopData(
            store_name=shop_row['store_name'], 
            items_ids=items_list
        )

    def get_items_by_category(self, category: ItemCategory) -> list[ItemData]:
        """Returns a list of all items that match a specific category."""
        self.cursor.execute("SELECT * FROM items WHERE category = ?", (category.value,))
        
        results = []
        for row in self.cursor.fetchall():
            results.append(ItemData(
                name=row['name'], description=row['description'],
                category=ItemCategory(row['category']), image_key=row['image_key'],
                buy_price=row['buy_price'], sell_price=row['sell_price'],
                stackable=bool(row['stackable']), max_stack=row['max_stack'],
                energy_gain=row['energy_gain'], grow_time=row['grow_time'],
                tool_type=ToolType(row['tool_type']) if row['tool_type'] else None 
            ))
        return results

    def close(self) -> None:
        self.conn.close()