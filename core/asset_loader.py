# asset_loader.py
import pygame, os, inspect
from enum import Enum
from abc import ABC

from core.spritesheet import SpriteSheet
from core.types import ItemCategory, EntityConfig, ItemData, FontType, EntityState, Direction, TextConfig
from Assets.asset_data import *
from settings import BLOCK_SIZE

### Parent Classes

class AssetGroup(ABC):
    """Universal Base Class. 
    Automatically gives every subclass its own unique STORAGE dictionary."""
    
    def __init_subclass__(cls, **kwargs):
        """Magic method: Runs when a subclass is defined.
        Ensures every group has its own storage dicts."""
        super().__init_subclass__(**kwargs)
        cls.STORAGE = {}

    @classmethod
    @abstractmethod
    def load(cls):
        pass

class ConfigGroup(AssetGroup):
    """Parent for Dictionary-based assets (Colours, Text).
    Handles: Storage, Missing Keys, Defaults, and Debugging."""
    
    MISSING = set() 
    DEFAULT = None
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Give every config group its own independent tracking sets
        cls.MISSING = set()
        cls.DEFAULT = None
    @classmethod
    def get_val(cls, key):
        """Generic lookup with error tracking."""
        # 1. Try Exact Match
        val = cls.STORAGE.get(key)
        if val: return val

        # 2. Handle Missing
        if key not in cls.MISSING:
            # --- NEW DEBUG LOGIC ---
            caller_info = "Unknown source"
            try:
                # Look back through the stack to find who called this
                for frame in inspect.stack():
                    filename = os.path.basename(frame.filename)
                    # Skip these files to find the 'real' culprit
                    ignore_files = ["asset_loader.py", "ui_elements.py", "helper.py"]
                    
                    if filename not in ignore_files:
                        # Format: filename:line_number
                        filename = os.path.basename(frame.filename)
                        caller_info = f"{filename}:{frame.lineno}"
                        break
            except Exception:
                pass

            print(f"[{cls.__name__}] Warning: Missing Key '{key}' (Requested by: {caller_info})")
            # -----------------------
            
            cls.MISSING.add(key)

    @classmethod
    def debug_print(cls):
        print(f"\n--- {cls.__name__} ({len(cls.STORAGE)}) ---")
        # Print Missing
        if cls.MISSING:
            print(f"MISSING KEYS ({len(cls.MISSING)}):")
            for key in sorted(cls.MISSING):
                print(f"  [X] {key}")
        else:
            print("No missing keys.")
        print("-" * 30)

class SpriteGroup(AssetGroup):
    """Parent for Sheet-based assets (Tiles, Tools, Plants)."""
    SCALE_FACTOR = 2
    TILE_SIZE = 32

    @classmethod
    def load_spritesheet(cls, name: str):
        """Safe loader wrapper, used by all Sprite Groups."""
        try:
            return SpriteSheet(f"{name}.png")
        except Exception as e:
            print(f"Failed to load {name}: {e}")
            return None

### Config Group Implementations

class TextGroup(ConfigGroup):
    """Manages TextConfig styles (presets like 'TITLE', 'HUD')."""
    DEFAULT = None # Will be set during load()
    @classmethod
    def load(cls):
        cls.STORAGE.update(TEXT)
        cls.DEFAULT = cls.STORAGE.get("default", TextConfig())

    @classmethod
    def get_config(cls, key: str):
        return cls.get_val(key)
   
class ColourGroup(ConfigGroup):
    """Manages game palette and provides debug printing."""
    DEFAULT = (255, 0, 255) # Error Fallback
    
    @classmethod
    def load(cls):
        cls.STORAGE.update(COLOURS)
        cls.DEFAULT = COLOURS.get("DEFAULT", (255, 0, 255))

    @classmethod
    def get_colour(cls, name, fallback_type=None) -> tuple:
        """Tiered lookup: Name -> Fallback -> Default."""
        
        # Try exact match
        col = cls.STORAGE.get(name)
        if col: return col
        
        # Try fallback category
        if fallback_type:
            col = cls.STORAGE.get(fallback_type)
            if col: return col
        
        # Fallback to generic missing logic
        return cls.get_val(name) or cls.DEFAULT

### Sprite Group Implementations

class TileGroup(SpriteGroup):    
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

class ToolGroup(SpriteGroup):
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

class PlantGroup(SpriteGroup):
    @classmethod
    def load(cls):
        sheet = cls.load_spritesheet("Plants")
        if not sheet: return

        for name, asset in CROPS.items():
            rect = asset.world_art
            
            # Use the asset's built-in flag to decide how to slice the sprite!
            if asset.is_tree:
                # Static Trees (Use the predefined tuple slices)
                slices = TREE_FRAME_SLICES
            else:
                # Dynamic Crops (Calculate widths and reorder based on PLANT_FRAME_ORDER)
                frame_w = rect.w // len(PLANT_FRAME_ORDER)
                slices = [(idx * frame_w, frame_w) for idx in PLANT_FRAME_ORDER]    
                
            # Extract and store each stage of the plant/tree
            for i, (offset, width) in enumerate(slices):
                cls.STORAGE[f"{name}_{i}"] = sheet.get_image(
                    rect.x + offset, rect.y, width, rect.h,
                    (width * cls.SCALE_FACTOR, rect.h * cls.SCALE_FACTOR)
                )
        
class FruitGroup(SpriteGroup):
    CONTAINERS = {}
    SEED_BAGS = {}
    CACHE = {}

    @classmethod
    def load(cls):
        sheet = cls.load_spritesheet("Supplies")
        if not sheet: return

        for name, asset in CROPS.items():
            num = 2 if name == "Melon" else 3
            cls.STORAGE[name] = cls._create_strip(sheet, asset.fruit_container_image, FRUIT_RANKS, num, 2)
            cls.CONTAINERS[name] = sheet.get_image(
                asset.fruit_image.x, asset.fruit_image.y, 
                asset.fruit_image.w, asset.fruit_image.h)
            
        cls.SEED_BAGS = cls._create_strip(sheet, SEED_BAGS_POS, ["1", "2"], 2, 3)

    @classmethod
    def _create_strip(cls, sheet, rect, ranks, num, scale_f):
        items = {}
        w = rect.w // num
        for i, rank in enumerate(ranks):
            items[rank] = sheet.get_image(rect.x + (i * w), rect.y, w, rect.h, (w*scale_f, rect.h*scale_f))
        return items

class EntityGroup(SpriteGroup):
    @classmethod
    def load(cls):
        for category, config in GAME_ENTITIES.items():
            cls.STORAGE[category] = {}
            for name in config.sheets:
                cls.STORAGE[category][name] = {}
                path = AssetLoader.get_asset_path(f"{name}.png", folder=config.folder)
                sheet = SpriteSheet(path)
                
                for state, anim_grid in config.animations.items():
                    s_key = state.value if isinstance(state, Enum) else state
                    cls.STORAGE[category][name][s_key] = {}
                    for direction, rect in anim_grid.items():
                        d_key = direction.value if isinstance(direction, Enum) else direction
                        frames = []
                        cols, rows = rect.w // 32, rect.h // 32
                        for r in range(rows):
                            for c in range(cols):
                                frames.append(sheet.get_image(rect.x + (c*32), rect.y + (r*32), 32, 32, (64, 64)))
                        cls.STORAGE[category][name][s_key][d_key] = frames

### Unique Groups
class ImageGroup(AssetGroup):
    """Manages standalone images (UI, backgrounds, icons) 
        that aren't part of a spritesheet."""
    FAILURES = set()   
    @classmethod
    def load(cls): pass # ImageGroup loads on demand, so load() is empty
    @classmethod
    def get_image(cls, filename: str, scale=None) -> pygame.Surface:
        """Tries to get a cached image. If not found, loads from disk.
            If loading fails, generates a fallback. to-appends .png if missing."""
        if "." not in filename:
            filename = f"{filename}.png"
            
        # Create a unique cache key (Filename + Scale)
        # We need this because "icon.png" at 32x32 is different from "icon.png" at 64x64
        key = (filename, scale)

        # Return Cached if exists
        if key in cls.STORAGE:          return cls.STORAGE[key]
        # Check if we already failed this file (Prevent log spam)
        if filename in cls.FAILURES:    return cls.generate_fallback(filename, scale)

        # Attempt Load
        try:
            full_path = AssetLoader.get_asset_path(filename)
            img = pygame.image.load(full_path).convert_alpha()
            
            #Adjust size of image
            if scale:   img = pygame.transform.scale(img, scale)
            # Store image in cache
            cls.STORAGE[key] = img
            return img

        except (pygame.error, FileNotFoundError):
            print(f"Warning: Failed to load standalone image '{filename}'.")
            cls.FAILURES.add(filename)
            
            # Create and Cache the fallback so we don't recalculate it every frame
            fallback = cls.generate_fallback(filename, scale)
            cls.STORAGE[key] = fallback
            return fallback

    @classmethod
    def generate_fallback(cls, name, scale):
        """Internal helper to make the pink squares."""
        w, h = scale if scale else (32, 32)
        surf = pygame.Surface((w, h))
        
        # Use our ColourGroup for the fallback colour!
        col = ColourGroup.get_colour(name.upper(), "HIGHLIGHT") 
        surf.fill(col)
        
        # Draw a little 'X' or border to show it's missing
        pygame.draw.rect(surf, (0,0,0), (0,0,w,h), 1)
        return surf
    @classmethod
    def debug_print_failures(cls):
        print(f"\n--- Failed Images ({len(cls.FAILURES)}) ---")
        if not cls.FAILURES:
            print("No image load failures. All good!")
        else:
            for name in sorted(cls.FAILURES):
                print(f" [MISSING] • {name}")
        print("------------------------------------\n")

class FontGroup(AssetGroup):
    """ Internal helper class to manage font caching."""
    @classmethod
    def get_font(cls, config: TextConfig) -> pygame.font.Font:
        # Create a unique key for the cache
        key = (config.name, config.size, config.bold, config.italic)
        
        if key not in cls.STORAGE:
            if not pygame.font.get_init(): pygame.font.init()
            # Load and store
            cls.STORAGE[key] = pygame.font.SysFont(
                config.name, config.size, config.bold, config.italic)
        return cls.STORAGE[key]

    @classmethod
    def debug_print_fonts(cls):
        print(f"\n--- Cached Fonts ({len(cls.STORAGE)}) ---")
        for key in cls.STORAGE:
            name, size, bold, italic = key
            styles = []
            if bold: styles.append("Bold")
            if italic: styles.append("Italic")
            style_str = " + ".join(styles) if styles else "Normal"
            print(f"• Name: {name:<20} | Size: {size:<3} | Style: {style_str}")
        print("-" * 30)

### Main Asset Loader

class AssetLoader:
    has_loaded = False
    @classmethod
    def __init__(cls):
        if cls.has_loaded: return
        cls.has_loaded = True
        
        # Load all sub-groups
        ColourGroup.load()
        TextGroup.load()
        TileGroup.load()
        ToolGroup.load()
        PlantGroup.load()
        FruitGroup.load()
        EntityGroup.load()
        
        print("--- All Asset Sub-Groups Loaded ---")
        
    # --- UNIVERSAL GETTERS ---
    @staticmethod
    def get_asset_path(filename, folder="Assets"): 
        """Standardizes path creation."""
        return os.path.join(folder, filename)
    @classmethod
    def load_raw_image(cls, filename: str) -> pygame.Surface|None:
        """Loads an image from disk with NO fallback and NO caching.
            Returns None if the file is missing.
            Useful for SpriteSheets or systems that want to handle errors manually."""
        # Normalise name
        if "." not in filename:
            filename = f"{filename}.png"

        # Get Path
        full_path = cls.get_asset_path(filename)

        # Try Load
        try:
            return pygame.image.load(full_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            print(f"DEBUG: load_raw_image failed for '{filename}'")
            return None
       
    @classmethod
    def get_image(cls, key: str) -> pygame.Surface:
        """Universal lookup that checks through specialized groups."""
        # Check Plants
        if key in PlantGroup.STORAGE: return PlantGroup.STORAGE[key]
        
        # Check Tools (Format: WOOD_AXE)
        if "_" in key:
            parts = key.upper().split("_", 1)
            if parts[0] in ToolGroup.STORAGE:
                return ToolGroup.STORAGE[parts[0]].get(parts[1])
        
        # Check Fruits (Format: Tomato)
        if key in FruitGroup.STORAGE:
            return FruitGroup.STORAGE[key].get("BRONZE")

        fallback = TileGroup.STORAGE.get("DIRT_IMAGE")
        if fallback:
            return fallback
        # generate error coloured square
        return ImageGroup.get_image(f"MISSING_{key}")
        
    @classmethod
    def get_item_image(cls, data: ItemData) -> pygame.Surface | None:
        """Determines which group to query based on Category."""
        if data.category == ItemCategory.TOOL:
            return cls.get_image(data.image_key)
        elif data.category == ItemCategory.SEED:
            return cls.get_seed_image(data.image_key)
        elif data.category in (ItemCategory.CROP, ItemCategory.FRUIT):
            formatted_name = data.image_key.replace("_", " ").title()
            return FruitGroup.STORAGE.get(formatted_name, {}).get("BRONZE")
        return TileGroup.STORAGE.get("DIRT_IMAGE")
    @classmethod
    def get_seed_image(cls, seed_name: str, bag_id="1") -> pygame.Surface | None:
        cache_key = f"{bag_id}_{seed_name}"
        if cache_key in FruitGroup.CACHE: return FruitGroup.CACHE[cache_key]
        
        bag = FruitGroup.SEED_BAGS.get(bag_id)
        
        formatted_name = seed_name.replace("_", " ").title()
        fruit = FruitGroup.STORAGE.get(formatted_name, {}).get("BRONZE")
        
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
        except (KeyError, IndexError): # Only return None if the animation/frame is actually missing
            return None
    
    @classmethod
    def load_image(cls, filename: str, scale=None):             return ImageGroup.get_image(filename, scale)
    @classmethod
    def get_font(cls, config: TextConfig) -> pygame.font.Font:  return FontGroup.get_font(config)
    @classmethod
    def get_colour(cls, name:str, fallback:str|None = None):    return ColourGroup.get_colour(name, fallback)
    @classmethod 
    def get_text_config(cls, key:str):                          return TextGroup.get_config(key)
    
    @classmethod
    def debug_assets(cls):
        """Prints a full report of all loaded assets and any failures."""
        print("\n" + "="*40)
        print(f"{'ASSET LOADER DEBUG REPORT':^40}")
        print("="*40)
        
        ColourGroup.debug_print()
        TextGroup.debug_print()
        ImageGroup.debug_print_failures() # Keeping this name as it's specific to failures
        FontGroup.debug_print_fonts()
        
        print(f"\nTiles:  {len(TileGroup.STORAGE)}")
        print(f"Tools:  {len(ToolGroup.STORAGE)}")
        print(f"Plants: {len(PlantGroup.STORAGE)}")
        print("="*40 + "\n")