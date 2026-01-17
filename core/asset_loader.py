# asset_loader.py
import pygame, os
from enum import Enum
from abc import ABC, abstractmethod

from core.spritesheet import SpriteSheet
from core.helper import get_colour
from core.types import ItemCategory, EntityConfig, ItemData, FontType, EntityState, Direction
from Assets.asset_data import GAME_ENTITIES, MATERIAL_LEVELS, TILE_DETAILS, FRUIT_TYPES, FRUIT_RANKS, SEED_BAGS_POS, GROUND_TILE_REGIONS, TOOL_SPRITE_LAYOUT, PLANT_SPRITE_REGIONS, TREE_SPRITE_REGIONS, TREE_FRAME_SLICES
from settings import BLOCK_SIZE, HUD_FONT_SIZE, SLOT_FONT_SIZE

class AssetGroup(ABC):
    """Base class for a collection of related assets."""
    SCALE_FACTOR = 2
    TILE_SIZE = 32

    @classmethod
    def load_spritesheet(cls, name: str):
        """Standard safe loader used by all groups."""
        try:
            return SpriteSheet(f"{name}.png")
        except Exception as e:
            print(f"Failed to load {name}: {e}")
            return None

class TileGroup(AssetGroup):
    STORAGE = {}
    
    @classmethod
    def load(cls):
        sheet = cls.load_spritesheet("exterior")
        if not sheet: return
        
        # 1. Load Ground Regions
        for key, rect in GROUND_TILE_REGIONS.items():
            cls.STORAGE[key] = sheet.extract_tiles_by_dimensions(
                rect.x, rect.y, rect.w, rect.h, 16, 16, cls.SCALE_FACTOR
            )
        
        # 2. Dirt Fallback
        dirt_tiles = cls.STORAGE.get("DIRT")
        if dirt_tiles:
            cls.STORAGE["DIRT_IMAGE"] = pygame.transform.scale(dirt_tiles[11], (BLOCK_SIZE, BLOCK_SIZE))
            
        # 3. Details
        detail_sheet = cls.load_spritesheet("ground_grass_details")
        if detail_sheet:
            for key, rect_list in TILE_DETAILS.items():
                cls.STORAGE[f"DETAIL_{key.upper()}"] = []
                for r in rect_list:
                    cls.STORAGE[f"DETAIL_{key.upper()}"].extend(
                        detail_sheet.extract_tiles_by_dimensions(r.x, r.y, r.w, r.h, r.tile_w, r.tile_h, cls.SCALE_FACTOR)
                    )

class ToolGroup(AssetGroup):
    STORAGE = {}
    ITEM_SIZE = 36

    @classmethod
    def load(cls):
        sheet = cls.load_spritesheet("Tools_All")
        if not sheet: return
        
        for r_idx, mat in enumerate(MATERIAL_LEVELS):
            cls.STORAGE[mat] = {}
            for c_idx, tool in enumerate(TOOL_SPRITE_LAYOUT):
                cls.STORAGE[mat][tool] = sheet.get_image(
                    c_idx * cls.TILE_SIZE, 
                    r_idx * cls.TILE_SIZE + 2,
                    cls.TILE_SIZE, cls.TILE_SIZE, 
                    (cls.ITEM_SIZE, cls.ITEM_SIZE)
                )

class PlantGroup(AssetGroup):
    STORAGE = {}

    @classmethod
    def load(cls):
        sheet = cls.load_spritesheet("Plants")
        if not sheet: return

        # 1. Regular Crops (4 stages)
        for name, rect in PLANT_SPRITE_REGIONS.items():
            frame_w = rect.w // 4
            for i in range(4):
                cls.STORAGE[f"{name}_{i}"] = sheet.get_image(
                    rect.x + (i * frame_w), rect.y, frame_w, rect.h,
                    (frame_w * cls.SCALE_FACTOR, rect.h * cls.SCALE_FACTOR)
                )

        # 2. Trees (Manual Slices)
        for name, rect in TREE_SPRITE_REGIONS.items():
            for i, (offset, width) in enumerate(TREE_FRAME_SLICES):
                cls.STORAGE[f"{name}_{i}"] = sheet.get_image(
                    rect.x + offset, rect.y, width, rect.h,
                    (width * cls.SCALE_FACTOR, rect.h * cls.SCALE_FACTOR)
                )

class FruitGroup(AssetGroup):
    STORAGE = {}
    CONTAINERS = {}
    SEED_BAGS = {}
    CACHE = {}

    @classmethod
    def load(cls):
        sheet = cls.load_spritesheet("Supplies")
        if not sheet: return

        for name, pair in FRUIT_TYPES.items():
            num = 2 if name == "Melon" else 3
            cls.STORAGE[name] = cls._create_strip(sheet, pair.a, FRUIT_RANKS, num, 2)
            cls.CONTAINERS[name] = sheet.get_image(pair.b.x, pair.b.y, pair.b.w, pair.b.h)
            
        cls.SEED_BAGS = cls._create_strip(sheet, SEED_BAGS_POS, ["1", "2"], 2, 3)

    @classmethod
    def _create_strip(cls, sheet, rect, ranks, num, scale_f):
        items = {}
        w = rect.w // num
        for i, rank in enumerate(ranks):
            items[rank] = sheet.get_image(rect.x + (i * w), rect.y, w, rect.h, (w*scale_f, rect.h*scale_f))
        return items

class EntityGroup(AssetGroup):
    STORAGE = {}

    @classmethod
    def load(cls):
        for category, config in GAME_ENTITIES.items():
            cls.STORAGE[category] = {}
            for name in config.sheets:
                cls.STORAGE[category][name] = {}
                path = os.path.join(config.folder, f"{name}.png")
                sheet = SpriteSheet(path)
                
                for state, anim_grid in config.animations.items():
                    s_key = state.value if isinstance(state, Enum) else state
                    cls.STORAGE[category][name][s_key] = {}
                    for direction, rect in anim_grid.items():
                        d_key = direction.value if isinstance(direction, Enum) else direction
                        # Reuse the grid logic: assumes 32x32 tiles for entities
                        frames = []
                        cols, rows = rect.w // 32, rect.h // 32
                        for r in range(rows):
                            for c in range(cols):
                                frames.append(sheet.get_image(rect.x + (c*32), rect.y + (r*32), 32, 32, (64, 64)))
                        cls.STORAGE[category][name][s_key][d_key] = frames

class AssetLoader:
    FONTS: dict[FontType, pygame.font.Font] = {}

    @classmethod
    def __init__(cls):
        if TileGroup.STORAGE: return # Singleton check

        # Load all sub-groups
        TileGroup.load()
        print(f"Tiles Loaded: {len(TileGroup.STORAGE) > 0}")
        ToolGroup.load()
        print(f"Tools Loaded: {len(ToolGroup.STORAGE) > 0}")
        PlantGroup.load()
        print(f"Plants Loaded: {len(PlantGroup.STORAGE) > 0}")
        FruitGroup.load()
        EntityGroup.load()
        cls._load_fonts()
        
        print("--- All Asset Sub-Groups Loaded ---")

    @classmethod
    def _load_fonts(cls):
        if not pygame.font.get_init(): pygame.font.init()
        cls.FONTS[FontType.HUD] = pygame.font.SysFont("arial", HUD_FONT_SIZE, bold=True)
        cls.FONTS[FontType.SLOT] = pygame.font.SysFont("arial", SLOT_FONT_SIZE)

    # --- UNIVERSAL GETTERS ---

    @classmethod
    def get_image(cls, key: str) -> pygame.Surface | None:
        """Universal lookup that checks through specialized groups."""
        # 1. Check Plants
        if key in PlantGroup.STORAGE: return PlantGroup.STORAGE[key]
        
        # 2. Check Tools (Format: WOOD_AXE)
        if "_" in key:
            parts = key.upper().split("_", 1)
            if parts[0] in ToolGroup.STORAGE:
                return ToolGroup.STORAGE[parts[0]].get(parts[1])
        
        # 3. Check Fruits (Format: Tomato)
        if key in FruitGroup.STORAGE:
            return FruitGroup.STORAGE[key].get("BRONZE")

        return TileGroup.STORAGE.get("DIRT_IMAGE")

    @classmethod
    def get_item_image(cls, data: ItemData) -> pygame.Surface | None:
        """Determines which group to query based on Category."""
        if data.category == ItemCategory.TOOL:
            return cls.get_image(data.image_key)
        elif data.category == ItemCategory.SEED:
            return cls.get_seed_image(data.image_key)
        elif data.category in (ItemCategory.CROP, ItemCategory.FRUIT):
            return FruitGroup.STORAGE.get(data.image_key.title(), {}).get("BRONZE")
        return TileGroup.STORAGE.get("DIRT_IMAGE")

    @classmethod
    def get_seed_image(cls, seed_name: str, bag_id="1") -> pygame.Surface | None:
        cache_key = f"{bag_id}_{seed_name}"
        if cache_key in FruitGroup.CACHE: return FruitGroup.CACHE[cache_key]
        
        bag = FruitGroup.SEED_BAGS.get(bag_id)
        fruit = FruitGroup.STORAGE.get(seed_name.title(), {}).get("BRONZE")
        
        if not bag or not fruit: return bag
        
        comp = bag.copy()
        bx, by = comp.get_rect().center
        fx, fy = fruit.get_rect().size
        comp.blit(fruit, (bx - fx//2, by - fy//2 - 2))
        FruitGroup.CACHE[cache_key] = comp
        return comp

    @classmethod
    def get_animated_sprite(cls, cat: str, name: str, state: EntityState, direction: Direction, frame: int):
        try:
            frames = EntityGroup.STORAGE[cat][name][state.value][direction.value]
            return frames[int(frame) % len(frames)]
        except: return None

    @classmethod
    def get_font(cls, font_type: FontType):
        return cls.FONTS.get(font_type, pygame.font.SysFont("arial", 20))
