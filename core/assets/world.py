from __future__ import annotations
import pygame
from enum import Enum
from typing import TYPE_CHECKING, Any, Sequence

# Runtime Imports
from core.spritesheet import SpriteSheet
from core.types import SpriteRect
from core.assets.asset_data import (
    CROP_VISUALS, GROUND_TILE_REGIONS, TILE_DETAILS, 
    MATERIAL_LEVELS, TOOL_SPRITE_LAYOUT, TREE_FRAME_SLICES, 
    PLANT_FRAME_ORDER, FRUIT_RANKS, SEED_BAGS_POS,
    MarchingLayout, Quality)
from settings import BLOCK_SIZE, QUAD_SIZE
from core.assets.base import SpriteGroup

# Type-Only Imports
if TYPE_CHECKING:
    from core.assets import AssetLoader

class TileGroup(SpriteGroup):    
    def load(self) -> None:
        sheet = self.get_sheet("main")
        if not sheet: 
            return
        
        # 1. Load Ground Regions
        for key, rect in GROUND_TILE_REGIONS.items():
            self.storage[key] = sheet.extract_tiles_by_dimensions(
                rect.x, rect.y, rect.w, rect.h, 16, 16, self.SCALE_FACTOR
            )
        
        # 2. Dirt Fallback
        dirt_tiles = self.storage.get("DIRT")
        if dirt_tiles:
            self.storage["DIRT_IMAGE"] = pygame.transform.scale(dirt_tiles[11], (BLOCK_SIZE, BLOCK_SIZE))
            
        # 3. Details
        detail_sheet = self.get_sheet("details")
        if detail_sheet:
            for key, rect_list in TILE_DETAILS.items():
                self.storage[f"DETAIL_{key.upper()}"] = []
                for r in rect_list:
                    self.storage[f"DETAIL_{key.upper()}"].extend(
                        detail_sheet.extract_tiles_by_dimensions(r.x, r.y, r.w, r.h, r.tile_w, r.tile_h, self.SCALE_FACTOR)
                    )

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
        sheet = self.get_sheet("main")
        if not sheet: 
            return

        for name, visual_data in CROP_VISUALS.items():
            rect = visual_data.world_art
            
            if visual_data.is_tree:
                slices = TREE_FRAME_SLICES
            else:
                frame_w = rect.w // len(PLANT_FRAME_ORDER)
                slices = [(idx * frame_w, frame_w) for idx in PLANT_FRAME_ORDER]    
                
            for i, (offset, width) in enumerate(slices):
                self.storage[f"{name}_{i}"] = sheet.get_image(
                    rect.x + offset, rect.y, width, rect.h,
                    (width * self.SCALE_FACTOR, rect.h * self.SCALE_FACTOR)
                )
        
class FruitGroup(SpriteGroup):
    def __init__(self, manager: AssetLoader, **sheet_files: str) -> None:
        super().__init__(manager, **sheet_files)
        # Move these from class level to instance level
        self.containers = {}
        self.seed_bags = {}
        self.cache = {}

    def load(self) -> None:
        sheet = self.get_sheet("main")
        if not sheet: 
            return

        for name, visual_data in CROP_VISUALS.items():
            clean_key = name.lower().replace(" ", "_") 
            
            # Note: Assuming 3 quality levels for all fruits for this visual extraction
            self.storage[clean_key] = self._create_strip(
                sheet, visual_data.container, FRUIT_RANKS, 3, 2
            )
            
            self.containers[clean_key] = sheet.get_image(
                visual_data.fruit.x, visual_data.fruit.y, 
                visual_data.fruit.w, visual_data.fruit.h
            )
            
        self.seed_bags = self._create_strip(sheet, SEED_BAGS_POS, FRUIT_RANKS[1:], 2, 3)

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
            print("no bag")
            # Ask the parent manager for the fallback!
            return self.manager.images.get_image(f"MISSING_BAG_{clean_id}")
        elif not fruit: 
            print("no fruit")
            return bag
        
        comp = bag.copy()
        bx, by = comp.get_rect().center
        fx, fy = fruit.get_rect().size
        comp.blit(fruit, (bx - fx//2, by - fy//2 - 2))
        
        self.cache[cache_key] = comp
        return comp
