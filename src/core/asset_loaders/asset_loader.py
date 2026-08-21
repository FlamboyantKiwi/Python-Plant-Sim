from __future__ import annotations
import sys
import pygame
import os
from typing import TYPE_CHECKING, Callable

# Type-Only Imports
if TYPE_CHECKING:
    from src.custom_types import EntityType, Colour

# Runtime Imports
from .. import Log
from ..types import (
    ItemCategory, ItemData, EntityState, Direction, PlantData, 
    ShopData, TextConfig, EntityCategory
)

# Sub-Group Relative Imports
from .asset_group import AssetGroup
from .colour_group import ColourGroup
from .text_group import TextGroup
from .font_group import FontGroup
from .image_group import ImageGroup
from .database_group import DatabaseGroup
from .entity_group import EntityGroup
from .tile_group import TileGroup
from .tool_group import ToolGroup
from .plant_group import PlantGroup
from .fruit_group import FruitGroup

from src.config import (
    COLOURS, TEXT, GAME_ENTITIES, TILE_DETAILS, 
    TOOL_GROUP_DATA, PLANT_GROUP_DATA, FRUIT_GROUP_DATA, MarchingLayout
)

class AssetLoader:
    def __init__(self):
        # Create all sub-groups
        self.colours = ColourGroup(self, raw_data=COLOURS)
        self.text = TextGroup(self, raw_data=TEXT)
        self.entities = EntityGroup(self, raw_data=GAME_ENTITIES)
        self.tiles = TileGroup(
            self, raw_data=TILE_DETAILS, 
            grass_a="tiles/grass_a", grass_b="tiles/grass_b",
            dirt="tiles/dirt", details="ground_grass_details"
        )
        self.tools = ToolGroup(self, raw_data=TOOL_GROUP_DATA, main="Tools_All")
        
        self.plants = PlantGroup(
            self, raw_data=PLANT_GROUP_DATA, 
            crops="plants/crops", trees="plants/trees"
        )
        
        self.fruits = FruitGroup(
            self, raw_data=FRUIT_GROUP_DATA, 
            crops="plants/crops", trees="plants/trees", supplies="Supplies"
        )
        
        self.images = ImageGroup(self)
        self.fonts = FontGroup(self)
        self.database = DatabaseGroup(self)

        # Dynamically pack them into a dict for easy looping
        self.groups: dict[str, AssetGroup] = {
            name: obj 
            for name, obj in vars(self).items() 
            if isinstance(obj, AssetGroup)
        }

        self._image_routers: dict[ItemCategory, Callable[[str], pygame.Surface | None]] = {
            ItemCategory.TOOL: self.tools.get,
            ItemCategory.CROP: self.plants.storage.get, 
            ItemCategory.FRUIT: self.fruits.get,
            ItemCategory.SEED: lambda key: self.fruits.get_seed(key),
        }
    
    def clean_up(self) -> None:
        """Called right before the game quits to close file connections."""
        for group in self.groups.values():
            group.clean_up()
        Log.success("--- All Assets Cleaned Up & Safely Closed ---")

    def load_all(self) -> None:
        """Called once at the start of game."""
        for group in self.groups.values():
            group.load()
        Log.success("--- All Asset Sub-Groups Loaded ---")
        
    # --- UNIVERSAL GETTERS ---
    def get_image_path(self, filename: str, subfolder: str = "") -> str: 
        """Standardizes path creation with a fixed Assets/images base and PyInstaller support."""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        
        if subfolder:
            return os.path.join(base_path, "Assets", "images", subfolder, filename)
        
        return os.path.join(base_path, "Assets", "images", filename)

    def load_raw_image(self, filename: str) -> pygame.Surface | None:
        """Loads an image from disk with NO fallback and NO caching.
            Returns None if the file is missing.
            Useful for SpriteSheets or systems that want to handle errors manually."""
        # Normalise name
        if "." not in filename:
            filename = f"{filename}.png"

        # Get Path
        full_path = self.get_image_path(filename)

        # Try Load
        try:
            return pygame.image.load(full_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            Log.error(f"DEBUG: load_raw_image failed for '{filename}'")
            return None
       
    def _get_fallback_image(self, key: str) -> pygame.Surface:
        """Centralized fallback logic for missing images."""
        if fallback := self.tiles.storage.get("DIRT_IMAGE"):
            return fallback
        return self.images.get_image(f"MISSING_{key}")
       
    def get_image(self, key: str) -> pygame.Surface:
        """Universal lookup that checks through all known item groups."""
        for getter in self._image_routers.values():
            if img := getter(key):
                return img
                
        return self._get_fallback_image(key)
        
    def item_image(self, data: ItemData) -> pygame.Surface:
        """Determines which group to query based on the item category."""
        if router_func := self._image_routers.get(data.category):
            if img := router_func(data.image_key): 
                return img
        
        return self._get_fallback_image(data.image_key)

    def sprite(self, category: EntityCategory, name: EntityType, state: EntityState, direction: Direction, frame: int) -> pygame.Surface | None:
        return self.entities.get_sprite(category, name, state, direction, frame)

    def autotile(self, tileset_key:str, layout:MarchingLayout, neighbors: list[bool]) -> pygame.Surface:
        return self.tiles.build_marching_tile(tileset_key, layout, neighbors)

    def load_image(self, filename: str, scale=None) -> pygame.Surface:            
        return self.images.get_image(filename, scale)
        
    def font(self, config: TextConfig) -> pygame.font.Font:  
        return self.fonts.get_font(config)
        
    def colour(self, name:Colour, fallback:Colour|None = None) -> pygame.Color:    
        return self.colours.get_colour(name, fallback)
        
    def config(self, key:str) -> TextConfig:                          
        return self.text.get_config(key)
    
    # Database Getters
    def item(self, item_id: str) -> ItemData:
        return self.database.get_item(item_id)
        
    def plant(self, plant_id: str) -> PlantData:
        return self.database.get_plant(plant_id)
        
    def shop(self, shop_id: str) -> ShopData:
        return self.database.get_shop(shop_id)

    def debug_assets(self):
        """Prints a full report of all loaded assets and any failures."""
        Log.divider(40, "=")
        Log.info(f"{'ASSET LOADER DEBUG REPORT':^40}")
        
        for name, group in self.groups.items():
            group.debug_print()
                
        Log.divider(40, "=")
        
ASSETS = AssetLoader()