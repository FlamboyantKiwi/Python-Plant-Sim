from __future__ import annotations
import pygame
from enum import Enum
from typing import TYPE_CHECKING, Any, Sequence

# Runtime Imports
from src.core.spritesheet import SpriteSheet
from src.core.types import SpriteRect
from src.core.debug_logger import Log
from src.core.assets.asset_data import (
    CROPS_ORDER, TREES_ORDER, GROUND_TILE_REGIONS, TILE_DETAILS, 
    MATERIAL_LEVELS, TOOL_SPRITE_LAYOUT, TREE_FRAME_SLICES, 
    PLANT_FRAME_ORDER, FRUIT_RANKS, SEED_BAGS_POS,
    MarchingLayout, Quality)
from src.settings import BLOCK_SIZE, QUAD_SIZE
from src.core.assets.base import SpriteGroup

# Type-Only Imports
if TYPE_CHECKING:
    from src.core.assets import AssetLoader

class TileGroup(SpriteGroup):    
    def load(self) -> None:
        marching_sets = {
            "GRASS_A": ("grass_a", 160, 48),
            "GRASS_B": ("grass_b", 160, 48),
            "DIRT":    ("dirt",    160, 48),
        }
        for key, (alias, w, h) in marching_sets.items():
            sheet = self.get_sheet(alias)
            if sheet:
                # We extract the whole sheet as a list of 16x16 tiles
                self.storage[key] = sheet.extract_tiles_by_dimensions(
                    0, 0, w, h, 16, 16, self.SCALE_FACTOR
                )
        
        # 2. Dirt Fallback
        dirt_tiles = self.storage.get("DIRT")
        if dirt_tiles and len(dirt_tiles) > 11:
            self.storage["DIRT_IMAGE"] = pygame.transform.scale(
                dirt_tiles[11], (BLOCK_SIZE, BLOCK_SIZE)
            )
            
        # 3. Details (Remains the same as your original)
        detail_sheet = self.get_sheet("details")
        if detail_sheet:
            for key, rect_list in TILE_DETAILS.items():
                storage_key = f"DETAIL_{key.upper()}"
                self.storage[storage_key] = []
                for r in rect_list:
                    tiles = detail_sheet.extract_tiles_by_dimensions(
                        r.x, r.y, r.w, r.h, r.tile_w, r.tile_h, self.SCALE_FACTOR
                    )
                    self.storage[storage_key].extend(tiles)

    def build_marching_tile(self, tileset_key:str, layout:MarchingLayout, neighbors: list[bool], sheet_width=10) -> pygame.Surface:
        """Dynamically builds a 64x64 surface based on the 9-node neighborhood."""
        surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        tileset: list[pygame.Surface] | None = self.storage.get(tileset_key)
        
        # Fallback if tileset is missing
        if not tileset:
            surface.fill(self.manager.colours.get_colour("DEFAULT"))
            return surface

        quads = [
            (neighbors[0], neighbors[1], neighbors[3], neighbors[4]), # NW
            (neighbors[1], neighbors[2], neighbors[4], neighbors[5]), # NE
            (neighbors[3], neighbors[4], neighbors[6], neighbors[7]), # SW
            (neighbors[4], neighbors[5], neighbors[7], neighbors[8]), # SE
        ]
        blit_pos = [(0, 0), (QUAD_SIZE, 0), (0, QUAD_SIZE), (QUAD_SIZE, QUAD_SIZE)]

        for i, inputs in enumerate(quads):
            mask = (inputs[0]*1) + (inputs[1]*2) + (inputs[2]*4) + (inputs[3]*8)
            row, col, rotation = layout.get_variant(mask)
            
            index = row * sheet_width + col
            sub_tile = tileset[index]

            if rotation != 0:
                sub_tile = pygame.transform.rotate(sub_tile, rotation)

            surface.blit(sub_tile, blit_pos[i])
            
        return surface
    
class ToolGroup(SpriteGroup):
    ITEM_SIZE:int = 36
    def load(self) -> None:
        sheet = self.get_sheet("main")
        if not sheet: 
            return
        
        for r_idx, mat in enumerate(MATERIAL_LEVELS):
            mat_str = mat.value if isinstance(mat, Enum) else mat 
            
            self.storage[mat_str] = {}
            for c_idx, tool in enumerate(TOOL_SPRITE_LAYOUT):
                self.storage[mat_str][tool] = sheet.get_image(
                    c_idx * self.TILE_SIZE, 
                    r_idx * self.TILE_SIZE + 2,
                    self.TILE_SIZE, self.TILE_SIZE, 
                    (self.ITEM_SIZE, self.ITEM_SIZE))

    def get(self, key:str) ->pygame.Surface | None:
        if "_" not in key:
            return None
            
        # Split on the first underscore only
        material, tool_name = key.upper().split("_", 1)
        
        # Safely fetch the material dict, then the tool image
        return self.storage.get(material, {}).get(tool_name)

class PlantGroup(SpriteGroup):
    def load(self) -> None:
        def extract_plants(sheet_key: str, order_list: list, world_x: int, world_w: int, is_tree: bool):
            sheet = self.get_sheet(sheet_key)
            if not sheet or not order_list: 
                return
            
            # The image height dictates the uniform grid height
            row_h = sheet.sheet.get_height() // len(order_list)
            
            for i, name in enumerate(order_list):
                current_y = i * row_h
                
                # Grab the uniform padded strip from the grid
                padded_strip = sheet.get_image(world_x, current_y, world_w, row_h)
                
                # Get the tight bounding box to strip bottom transparency
                bounds = padded_strip.get_bounding_rect()
                if bounds.h <= 0: 
                    continue # Skip empty items (like Corn/Sunflower)
                    
                # Create the tightly cropped strip (keeps physics accurate)
                tight_strip = padded_strip.subsurface((0, bounds.y, world_w, bounds.h))

                # Slice the tight strip into animation frames
                if is_tree:
                    slices = TREE_FRAME_SLICES
                else:
                    frame_w = world_w // 4
                    slices = [(idx * frame_w, frame_w) for idx in range(4)]    
                
                for frame_idx, (offset, width) in enumerate(slices):
                    frame_img = tight_strip.subsurface((offset, 0, width, bounds.h))
                    
                    # Apply SCALE_FACTOR manually
                    scaled_size = (width * self.SCALE_FACTOR, bounds.h * self.SCALE_FACTOR)
                    self.storage[f"{name}_{frame_idx}"] = pygame.transform.scale(frame_img, scaled_size)

        extract_plants("crops", CROPS_ORDER, world_x=80, world_w=128, is_tree=False)
        extract_plants("trees", TREES_ORDER, world_x=80, world_w=255, is_tree=True)
        
class FruitGroup(SpriteGroup):
    def __init__(self, manager: AssetLoader, **sheet_files: str) -> None:
        super().__init__(manager, **sheet_files)
        # Move these from class level to instance level
        self.containers = {}
        self.seed_bags = {}
        self.cache = {}

    def load(self) -> None:
        def extract_supplies(sheet_key: str, order_list: list):
            sheet = self.get_sheet(sheet_key)
            if not sheet or not order_list: return
            
            row_h = sheet.sheet.get_height() // len(order_list)
            c_x, c_w = 0, 48
            f_x, f_w = 48, 32

            for i, name in enumerate(order_list):
                clean_key = name.lower().replace(" ", "_") 
                current_y = i * row_h
                
                # --- Container Strip (Quality levels) ---
                padded_container = sheet.get_image(c_x, current_y, c_w, row_h)
                c_bounds = padded_container.get_bounding_rect()
                
                if c_bounds.h > 0:
                    tight_container = padded_container.subsurface((0, c_bounds.y, c_w, c_bounds.h))
                    
                    # Emulate previous _create_strip slicing
                    num_ranks = 3
                    rank_w = c_w // num_ranks
                    scale_f = 2
                    
                    items = {}
                    for rank_idx, rank in enumerate(FRUIT_RANKS):
                        rank_key = rank.value if isinstance(rank, Enum) else rank
                        rank_img = tight_container.subsurface((rank_idx * rank_w, 0, rank_w, c_bounds.h))
                        items[rank_key] = pygame.transform.scale(rank_img, (rank_w * scale_f, c_bounds.h * scale_f))
                        
                    self.storage[clean_key] = items

                # --- Fruit Image ---
                padded_fruit = sheet.get_image(f_x, current_y, f_w, row_h)
                f_bounds = padded_fruit.get_bounding_rect()
                
                if f_bounds.h > 0:
                    self.containers[clean_key] = padded_fruit.subsurface((0, 0, f_w, f_bounds.h))

        # Extract fruits & containers from the new sheets
        extract_supplies("crops", CROPS_ORDER)
        extract_supplies("trees", TREES_ORDER)

        # Fallback to extract Seed Bags from the master Supplies sheet
        supplies_sheet = self.get_sheet("supplies")
        if supplies_sheet:
            self.seed_bags = self._create_strip(supplies_sheet, SEED_BAGS_POS, FRUIT_RANKS[1:], 2, 3)
            
    def _create_strip(self, sheet: SpriteSheet, rect: SpriteRect, ranks: Sequence[Any], num: int, scale_f: int) -> dict[str, pygame.Surface]:
        items:dict[str, pygame.Surface] = {}
        w = rect.w // num
        for i, rank in enumerate(ranks):
            # Extract the string if it's an Enum, otherwise use it as-is (for seed bags)
            rank_key = rank.value if isinstance(rank, Enum) else rank
            
            items[rank_key] = sheet.get_image(
                rect.x + (i * w), rect.y, w, rect.h, 
                (w * scale_f, rect.h * scale_f)
            )
        return items

    def get(self, key: str) -> pygame.Surface | None:
        """Helper to get a fruit, prioritizing Bronze -> Silver -> Gold."""
        data = self.storage.get(key, {})
        return data.get("BRONZE") or data.get("SILVER") or data.get("GOLD")

    def get_seed(self, item_id: str, quality: Quality = Quality.BRONZE) -> pygame.Surface | None:
        """Generates and caches seed bags. Only runs if item_id looks like a seed."""
        if "_seeds" not in item_id.lower():
            return None
        quality_key = quality.value if isinstance(quality, Quality) else quality
        clean_id = item_id.lower().replace("_seeds", "").replace(" ", "_")
        
        cache_key = f"{quality_key}_{clean_id}"
        if cache_key in self.cache: 
            return self.cache[cache_key]
        
        bag = self.seed_bags.get(quality_key)
        fruit_data = self.storage.get(clean_id, {})
        fruit = fruit_data.get("GOLD")
        
        if not bag:
            Log.error("no bag")
            # Ask the parent manager for the fallback!
            return self.manager.images.get_image(f"MISSING_BAG_{clean_id}")
        elif not fruit: 
            Log.error("no fruit")
            return bag
        
        comp = bag.copy()
        bx, by = comp.get_rect().center
        fx, fy = fruit.get_rect().size
        comp.blit(fruit, (bx - fx//2, by - fy//2 - 2))
        
        self.cache[cache_key] = comp
        return comp
