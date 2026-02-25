# asset_loader.py
import pygame
import os
import inspect
from enum import Enum
from abc import ABC, abstractmethod

from core.spritesheet import SpriteSheet
from core.types import ItemCategory, ItemData,  EntityState, Direction, TextConfig
from Assets.asset_data import CROPS, TEXT, COLOURS, GROUND_TILE_REGIONS, TILE_DETAILS, MATERIAL_LEVELS, TOOL_SPRITE_LAYOUT, TREE_FRAME_SLICES, PLANT_FRAME_ORDER, FRUIT_RANKS, SEED_BAGS_POS, GAME_ENTITIES, MarchingLayout, Quality
from settings import BLOCK_SIZE, QUAD_SIZE

### Parent Classes

class AssetGroup(ABC):
    """Universal Base Class. 
    Automatically gives every subclass its own unique STORAGE dictionary."""
    
    def __init__(self, manager):
        self.manager = manager
        self.storage = {}

    @abstractmethod
    def load(self):
        pass
    
    @abstractmethod
    def debug_print(self):
        pass

class ConfigGroup(AssetGroup):
    """Parent for Dictionary-based assets (Colours, Text).
    Handles: Storage, Missing Keys, Defaults, and Debugging."""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.missing = set()
        self.default = None
        
    def get_val(self, key):
        """Generic lookup with error tracking."""
        # 1. Try Exact Match
        val = self.storage.get(key)
        if val: 
            return val

        # 2. Handle Missing & Stack Trace
        if key not in self.missing:
            # --- YOUR DEBUG LOGIC ---
            caller_info = "Unknown source"
            try:
                # Look back through the stack to find who called this
                for frame in inspect.stack():
                    filename = os.path.basename(frame.filename)
                    # Skip these files to find the 'real' culprit
                    ignore_files = ["asset_loader.py", "ui_elements.py", "helper.py"]
                    
                    if filename not in ignore_files:
                        # Format: filename:line_number
                        caller_info = f"{filename}:{frame.lineno}"
                        break
            except Exception:
                pass

            # Use self.__class__.__name__ instead of cls.__name__
            print(f"[{self.__class__.__name__}] Warning: Missing Key '{key}' (Requested by: {caller_info})")
            # -----------------------
            
            self.missing.add(key)
            
        return self.default

    def debug_print(self):
        print(f"\n--- {self.__class__.__name__} ({len(self.storage)}) ---")
        # Print Missing
        if self.missing:
            print(f"MISSING KEYS ({len(self.missing)}):")
            for key in sorted(self.missing):
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
        
    def debug_print(self):
        """Default debug for all Sprite groups."""
        print(f"\n--- {self.__class__.__name__} ({len(self.storage)} items loaded) ---")
        print("-" * 30)

### Config Group Implementations

class TextGroup(ConfigGroup):
    """Manages TextConfig styles (presets like 'TITLE', 'HUD')."""
    def __init__(self, manager):
        super().__init__(manager) 
        # Default will be set during load()

    def load(self):
        self.storage.update(TEXT)
        self.default = self.storage.get("default", TextConfig())


    def get_config(self, key: str):
        return self.get_val(key)
   
class ColourGroup(ConfigGroup):
    """Manages game palette and provides debug printing."""
    def __init__(self, manager):
        super().__init__(manager)
        self.default = (255, 0, 255)

    def load(self):
        self.storage.update(COLOURS)
        self.default = COLOURS.get("DEFAULT", (255, 0, 255))

    def get_colour(self, name, fallback_type=None) -> tuple:
        """Tiered lookup: Name -> Fallback -> Default."""
        
        # Try exact match
        col = self.storage.get(name)
        if col: 
            return col
        
        # Try fallback category
        if fallback_type:
            col = self.storage.get(fallback_type)
            if col: 
                return col
        
        # Fallback to generic missing logic
        return self.get_val(name) or self.default

### Sprite Group Implementations

class TileGroup(SpriteGroup):    
    def load(self):
        sheet = self.load_spritesheet("exterior")
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
        detail_sheet = self.load_spritesheet("ground_grass_details")
        if detail_sheet:
            for key, rect_list in TILE_DETAILS.items():
                self.storage[f"DETAIL_{key.upper()}"] = []
                for r in rect_list:
                    self.storage[f"DETAIL_{key.upper()}"].extend(
                        detail_sheet.extract_tiles_by_dimensions(r.x, r.y, r.w, r.h, r.tile_w, r.tile_h, self.SCALE_FACTOR)
                    )

    def build_marching_tile(self, tileset_key:str, layout:MarchingLayout, neighbors: list[bool], sheet_width=10)->pygame.Surface:
        """Dynamically builds a 64x64 surface based on the 9-node neighborhood."""
        surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        tileset = self.storage.get(tileset_key)
        
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
    ITEM_SIZE = 36
    def load(self):
        sheet = self.load_spritesheet("Tools_All")
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
    def load(self):
        sheet = self.load_spritesheet("Plants")
        if not sheet: 
            return

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
                self.storage[f"{name}_{i}"] = sheet.get_image(
                    rect.x + offset, rect.y, width, rect.h,
                    (width * self.SCALE_FACTOR, rect.h * self.SCALE_FACTOR)
                )
        
class FruitGroup(SpriteGroup):
    def __init__(self, manager):
        super().__init__(manager)
        # Move these from class level to instance level
        self.containers = {}
        self.seed_bags = {}
        self.cache = {}

    def load(self):
        sheet = self.load_spritesheet("Supplies")
        if not sheet: 
            return

        for name, asset in CROPS.items():
            clean_key = name.lower().replace(" ", "_") 
            ranks = FRUIT_RANKS[:asset.quality_levels]
            self.storage[clean_key] = self._create_strip(sheet, asset.fruit_container_image, ranks, asset.quality_levels, 2)
            self.containers[clean_key] = sheet.get_image(
                asset.fruit_image.x, asset.fruit_image.y, 
                asset.fruit_image.w, asset.fruit_image.h)
            
        self.seed_bags = self._create_strip(sheet, SEED_BAGS_POS, FRUIT_RANKS[1:], 2, 3)

    def _create_strip(self, sheet, rect, ranks, num, scale_f):
        items = {}
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
        """Generates and caches seed bags."""
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

class EntityGroup(SpriteGroup):
    def load(self):
        for category, config in GAME_ENTITIES.items():
            self.storage[category] = {}
            for name in config.sheets:
                self.storage[category][name] = {}
                path = self.manager.get_asset_path(f"{name}.png", folder=config.folder)
                sheet = SpriteSheet(path)
                
                for state, anim_grid in config.animations.items():
                    s_key = state.value if isinstance(state, Enum) else state
                    self.storage[category][name][s_key] = {}
                    for direction, rect in anim_grid.items():
                        d_key = direction.value if isinstance(direction, Enum) else direction
                        frames = []
                        cols, rows = rect.w // 32, rect.h // 32
                        for r in range(rows):
                            for c in range(cols):
                                frames.append(sheet.get_image(rect.x + (c*32), rect.y + (r*32), 32, 32, (64, 64)))
                        self.storage[category][name][s_key][d_key] = frames

    def get_sprite(self, cat: str, name: str, state: EntityState, direction: Direction, frame: int):
        """Safely fetches a specific frame of animation."""
        try:
            frames = self.storage[cat][name][state.value][direction.value]
            return frames[int(frame) % len(frames)]
        except (KeyError, IndexError):
            return None

### Unique Groups
class ImageGroup(AssetGroup):
    """Manages standalone images (UI, backgrounds, icons) 
        that aren't part of a spritesheet."""
    def __init__(self, manager):
        super().__init__(manager)
        self.failures = set()
    def load(self): pass # ImageGroup loads on demand, so load() is empty
    def get_image(self, filename: str, scale=None) -> pygame.Surface:
        """Tries to get a cached image. If not found, loads from disk.
            If loading fails, generates a fallback. to-appends .png if missing."""
        if "." not in filename:
            filename = f"{filename}.png"
            
        # Create a unique cache key (Filename + Scale)
        # We need this because "icon.png" at 32x32 is different from "icon.png" at 64x64
        key = (filename, scale)

        # Return Cached if exists
        if key in self.storage:         
            return self.storage[key]
        # Check if we already failed this file (Prevent log spam)
        if filename in self.failures:   
            return self.generate_fallback(filename, scale)

        # Attempt Load
        try:
            full_path = self.manager.get_asset_path(filename)
            img = pygame.image.load(full_path).convert_alpha()
            
            #Adjust size of image
            if scale:   
                img = pygame.transform.scale(img, scale)
            # Store image in cache
            self.storage[key] = img
            return img

        except (pygame.error, FileNotFoundError):
            print(f"Warning: Failed to load standalone image '{filename}'.")
            self.failures.add(filename)
            
            # Create and Cache the fallback so we don't recalculate it every frame
            fallback = self.generate_fallback(filename, scale)
            self.storage[key] = fallback
            return fallback

    def generate_fallback(self, name, scale):
        """Internal helper to make the pink squares."""
        w, h = scale if scale else (32, 32)
        surf = pygame.Surface((w, h))
        
        # Use our ColourGroup for the fallback colour!
        col = self.manager.colours.get_colour(name.upper(), "HIGHLIGHT")
        surf.fill(col)
        
        # Draw a little 'X' or border to show it's missing
        pygame.draw.rect(surf, (0,0,0), (0,0,w,h), 1)
        return surf
    def debug_print(self):
        print(f"\n--- {self.__class__.__name__} ({len(self.storage)} loaded, {len(self.failures)} failed) ---")
        if not self.failures:
            print("No image load failures. All good!")
        else:
            for name in sorted(self.failures):
                print(f"  [MISSING] • {name}")
        print("-" * 30)

class FontGroup(AssetGroup):
    """ Internal helper class to manage font caching."""
    def __init__(self, manager):
        super().__init__(manager)
        
    def load(self): pass # fonts load on demand - so this isn't needed
    
    def get_font(self, config: TextConfig) -> pygame.font.Font:
        # Create a unique key for the cache
        key = (config.name, config.size, config.bold, config.italic)
        
        if key not in self.storage:
            if not pygame.font.get_init(): 
                pygame.font.init()
            # Load and store
            self.storage[key] = pygame.font.SysFont(
                config.name, config.size, config.bold, config.italic)
        return self.storage[key]

    def debug_print(self):
        print(f"\n--- {self.__class__.__name__} ({len(self.storage)} cached) ---")
        for key in self.storage:
            name, size, bold, italic = key
            styles = []
            if bold: 
                styles.append("Bold")
            if italic: 
                styles.append("Italic")
            style_str = " + ".join(styles) if styles else "Normal"
            print(f"• Name: {name:<20} | Size: {size:<3} | Style: {style_str}")
        print("-" * 30)

### Main Asset Loader

class AssetLoader:
    def __init__(self):
        # Create all sub-groups
        self.colours = ColourGroup(self)
        self.text = TextGroup(self)
        self.tiles = TileGroup(self)
        self.tools = ToolGroup(self)
        self.plants = PlantGroup(self)
        self.fruits = FruitGroup(self)
        self.entities = EntityGroup(self)
        self.images = ImageGroup(self)
        self.fonts = FontGroup(self)
        
        # Dynamically pack them into a dict for easy looping
        self.groups = {
            name: obj 
            for name, obj in vars(self).items() 
            if isinstance(obj, AssetGroup)
        }
        
        self._image_routers = {
            ItemCategory.TOOL: self.tools.get,
            ItemCategory.CROP: self.plants.storage.get, 
            ItemCategory.FRUIT: self.fruits.get,
            ItemCategory.SEED: self.fruits.get_seed,
        }
        
    def load_all(self):
        """Called once at the start of game."""
        for name, group in self.groups.items():
            group.load()
        print("--- All Asset Sub-Groups Loaded ---")
        
    # --- UNIVERSAL GETTERS ---
    def get_asset_path(self, filename, folder="Assets"): 
        """Standardizes path creation."""
        return os.path.join(folder, filename)

    def load_raw_image(self, filename: str) -> pygame.Surface|None:
        """Loads an image from disk with NO fallback and NO caching.
            Returns None if the file is missing.
            Useful for SpriteSheets or systems that want to handle errors manually."""
        # Normalise name
        if "." not in filename:
            filename = f"{filename}.png"

        # Get Path
        full_path = self.get_asset_path(filename)

        # Try Load
        try:
            return pygame.image.load(full_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            print(f"DEBUG: load_raw_image failed for '{filename}'")
            return None
       
    def get_image(self, key: str) -> pygame.Surface:
        """Universal lookup that checks through specialized groups."""
        # Check specific groups using their dedicated getters
        if img := self.plants.storage.get(key): 
            return img
        if img := self.tools.get(key):     
            return img
        if img := self.fruits.get(key):   
            return img

        if fallback := self.tiles.storage.get("DIRT_IMAGE"):
            return fallback
        
        # generate error coloured square
        return self.images.get_image(f"MISSING_{key}")
        
    def get_item_image(self, data: ItemData) -> pygame.Surface:
        """Determines which group to query based on a dictionary lookup"""
        router_func = self._image_routers.get(data.category)
        if router_func:
            img = router_func(data.image_key)
            if img: 
                return img

        # Fallback
        return self.images.get_image(f"MISSING_{data.image_key}")

    def get_animated_sprite(self, cat: str, name: str, state: EntityState, direction: Direction, frame: int):
        return self.entities.get_sprite(cat, name, state, direction, frame)

    def get_marching_tile(self, tileset_key:str, layout:MarchingLayout, neighbors: list[bool]) -> pygame.Surface:
        return self.tiles.build_marching_tile(tileset_key, layout, neighbors)

    def load_image(self, filename: str, scale=None):            
        return self.images.get_image(filename, scale)
        
    def get_font(self, config: TextConfig) -> pygame.font.Font:  
        return self.fonts.get_font(config)
        
    def get_colour(self, name:str, fallback:str|None = None):    
        return self.colours.get_colour(name, fallback)
        
    def get_text_config(self, key:str):                          
        return self.text.get_config(key)
    
    def debug_assets(self):
        """Prints a full report of all loaded assets and any failures."""
        print("\n" + "="*40)
        print(f"{'ASSET LOADER DEBUG REPORT':^40}")
        print("="*40)
        
        for name, group in self.groups.items():
            group.debug_print()
                
        print("="*40 + "\n")
        
ASSETS = AssetLoader()