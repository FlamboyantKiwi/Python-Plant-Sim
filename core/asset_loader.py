# asset_loader.py
import pygame, os
from .spritesheet import SpriteSheet
from .helper import get_colour
from settings import BLOCK_SIZE
from Assets.asset_data import *

class AssetLoader:
    """Utility class to load and process all tile-related assets from sprite sheets."""
    SCALE_FACTOR = 2
    # Tool sprites are 16x16 in the sheet
    TILE_SIZE = 32
    ITEM_SIZE = 36 # Item sprites are scaled to 36x36 for inventory/UI display
    DIRT_SPRITE_INDEX = 11 # Index for the preferred base dirt tile: (Row 1 * 10 columns) + Col 1 = 11
    
    # Asset Storage
    TILE_ASSETS = {}
    TILE_DETAILS = {}
    ALL_TOOLS = {}
    ALL_FRUITS = {}
    ALL_FRUIT_CONTAINERS = {}
    SEED_BAGS = {}

    # Cashes
    _SEED_CACHE = {}
    ENTITIES = {}

    @classmethod
    def __init__(cls):
        # Prevent double loading if instantiated multiple times
        if cls.TILE_ASSETS: return
        cls.load_fruit_assets()
        cls.load_tool_assets()
        cls.load_tile_assets()
        cls.load_tile_detail_assets()
        
        for category, config in GAME_ENTITIES.items():
            cls.ENTITIES[category] = cls.load_entity_group(config)
        print("--- Assets Loaded ---")
    
    @classmethod
    def load_spritesheet(cls, name, path = None):
        """Helper to load a sprite sheet safely."""
        try:
            if path:
                image_name = os.path.join(path, f"{name}.png")
            else:
                image_name = f"{name}.png"
            return SpriteSheet(image_name)
        except Exception as e:
            print(f"Failed to load {name} sprite sheet: {e}")
            return None
    @classmethod
    def extract_grid(cls, sheet, rows:list, cols:list):
        """Extracts items arranged in a strict Grid (Rows = Categories, Cols = Variants)."""
        data = {}
        for row_idx, row_key in enumerate(rows):
            data[row_key] = {}
            for col_idx, col_key in enumerate(cols):
                data[row_key][col_key] = sheet.get_image(
                    x=col_idx * cls.TILE_SIZE, 
                    y=row_idx * cls.TILE_SIZE + 2, # Offset +2 per your specific tool sheet
                    width=cls.TILE_SIZE, height=cls.TILE_SIZE,
                    scale=(cls.ITEM_SIZE, cls.ITEM_SIZE)
                )
        return data
    @classmethod
    def extract_regions(cls, sheet, regions: dict):
        """Extracts items based on a dictionary of Named Rects."""
        data = {}
        for key, rect_data in regions.items():
            # Handle List of Rects (e.g., Tile Details)
            if isinstance(rect_data, list):
                data[key] = []
                for r in rect_data:
                    data[key].extend(sheet.extract_tiles_by_dimensions(
                        r.x, r.y, r.w, r.h, r.tile_w, r.tile_h, cls.SCALE_FACTOR
                    ))
            # Handle Single Rect (e.g., Ground Tiles)
            else:
                data[key] = sheet.extract_tiles_by_dimensions(
                    rect_data.x, rect_data.y, rect_data.w, rect_data.h, 16, 16, cls.SCALE_FACTOR
                )
        return data
    @classmethod
    def extract_region(cls, sheet, x, y, width, height):
        """ Cuts a defined rectangular region into a list of individual tile images. """
        frames = []
        # Calculate how many columns and rows fit in this region
        cols = width // cls.TILE_SIZE
        rows = height // cls.TILE_SIZE
        
        for row in range(rows):
            for col in range(cols):
                src_x = x + (col * cls.TILE_SIZE)
                src_y = y + (row * cls.TILE_SIZE)
                
                img = sheet.get_image(
                    x=src_x, 
                    y=src_y,
                    width=cls.TILE_SIZE, 
                    height=cls.TILE_SIZE,
                    scale=(cls.TILE_SIZE * cls.SCALE_FACTOR, cls.TILE_SIZE * cls.SCALE_FACTOR)
                )
                frames.append(img)
                
        return frames

    # ==================================================
    #   SPECIFIC LOADERS (Tools, Fruits, Tiles)
    # ==================================================

    @classmethod
    def load_tool_assets(cls):
        sheet = cls.load_spritesheet("Tools_All")
        if sheet:
            # Logic moved to _extract_grid
            cls.ALL_TOOLS = cls.extract_grid(sheet, MATERIAL_LEVELS, TOOL_TYPES)
            print("Tool assets loaded successfully.")

    @classmethod
    def load_tile_assets(cls):
        """ Loads all tile assets, scales the base dirt tile, assigns it to 
        settings.DIRT_TILE, and returns the full dictionary of tileset lists. """
        # Load the SpriteSheet
        sheet = cls.load_spritesheet("exterior")
        if not sheet:  return

        cls.TILE_ASSETS = cls.extract_regions(sheet, GROUND_TILE_REGIONS)

        # Dirt Fallback - Create Single Dirt Tile for fallback/default
        dirt = cls.TILE_ASSETS.get("DIRT")
        if dirt:
            cls.TILE_ASSETS["DIRT_IMAGE"] = pygame.transform.scale(dirt[cls.DIRT_SPRITE_INDEX], (BLOCK_SIZE, BLOCK_SIZE))
        else:
            s = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            s.fill(get_colour("DIRT"))
            cls.TILE_ASSETS["DIRT_IMAGE"] = s
    @classmethod
    def load_tile_detail_assets(cls):
        sheet = cls.load_spritesheet("ground_grass_details")
        if sheet:
            cls.TILE_DETAILS = cls.extract_regions(sheet, TILE_DETAILS)

    @classmethod
    def load_fruit_assets(cls):
        """Loads and organizes individual fruits/seeds and fruit containers from Supplies.png."""
        sheet = cls.load_spritesheet("Supplies")
        if not sheet: return

        for name, pair in FRUIT_TYPES.items():
            # Special Case
            if name == "Melon":
                num = 2
            else:
                num = 3
            cls.ALL_FRUITS[name] = cls.create_fruit_strip(sheet, pair.a, FRUIT_RANKS, num, 2)
            cls.ALL_FRUIT_CONTAINERS[name] = sheet.get_image(pair.b.x, pair.b.y, pair.b.w, pair.b.h)
            
        cls.SEED_BAGS = cls.create_fruit_strip(sheet, SEED_BAGS_POS, ["1", "2"], 2, 3)
    
    @classmethod
    def create_fruit_strip(cls, sheet: SpriteSheet, rect, ranks, number=3, scale_factor = None):
        """Helper for fruit strips."""
        items = {}
        w = rect.w // number
        scale = (w * scale_factor, rect.h * scale_factor)
        for i, rank in enumerate(ranks):
            items[rank] = sheet.get_image(rect.x + (i * w), rect.y, w, rect.h, scale)
        return items
    
    # ==================================================
    #   ENTITY LOADING
    # ==================================================
    
    @classmethod
    def load_entity_group(cls, config: EntityConfig):
        """Loads a group of entities based on the config object."""
        group_assets = {}
        # Access properties via dot notation directly from the config object
        for name in config.sheets:
            group_assets[name] = {}
            path = os.path.join(config.folder, f"{name}.png")
            sheet = SpriteSheet(path)
            
            # Use config.states
            for state, anim_grid in config.animations.items():
                
                # Convert Enum to String for storage (e.g. EntityState.WALK -> "Walk")
                # This ensures your game loop can use strings OR enums easily
                state_key = state.value if isinstance(state, Enum) else state
                group_assets[name][state_key] = {}
                
                # 2. Iterate over DIRECTIONS (Down, Up...) inside the Grid
                # anim_grid is a Dict[Direction, SpriteRect]
                for direction, rect in anim_grid.items():
                    
                    dir_key = direction.value if isinstance(direction, Enum) else direction
                    
                    # 3. Cut the frames using the Helper
                    # The helper handles the row/col splitting automatically based on Rect size
                    frames = cls.extract_region(sheet, rect.x, rect.y, rect.w, rect.h)
                    
                    group_assets[name][state_key][dir_key] = frames
                        
        return group_assets

    @classmethod
    def get_animated_sprite(cls, category: str, name: str, state: str, direction: str, tick: int):
        """ Universal function to get the correct frame for ANY moving entity. """
       # 1. Retrieve the specific entity's library
        entity_library = cls.ENTITIES.get(category, {}) 
        sheet_data = entity_library.get(name)             
        if not sheet_data: return None # Error

        # 2. Retrieve the State Dictionary (e.g. "Walk")
        # Handles cases where input might be an Enum or String
        s_key = state.value if isinstance(state, Enum) else state
        state_data = sheet_data.get(s_key)
        if not state_data: return None # Error

        # Retrieve the Direction List (e.g. "Down")
        d_key = direction.value if isinstance(direction, Enum) else direction
        
        # Fallback to DOWN if the specific direction is missing
        frames = state_data.get(d_key)
        if not frames:
            frames = state_data.get("Down") 
            if not frames: return None # Error

        # Calculate current frame (based on tick and total frames) 
        current_frame = int(tick) % len(frames)
        return frames[current_frame]

    # ==================================================
    #   SPECIFIC GETTERS
    # ==================================================

    @classmethod
    def get_tool_image(cls, tool_name: str):
        try:
            mat, typ = tool_name.upper().split("_", 1)
            return cls.ALL_TOOLS.get(mat, {}).get(typ)
        except: return None   
    @classmethod
    def get_fruit_image(cls, name):
        try:
            rank, type_ = name.split("_", 1)
            return cls.ALL_FRUITS.get(type_.title(), {}).get(rank.upper())
        except: return None
    @classmethod
    def get_seed_image(cls, seed_name: str = "", bag_id = "1"):
        key = f"{bag_id}_{seed_name}"
        if key in cls._SEED_CACHE: return cls._SEED_CACHE[key]
        
        bag = cls.SEED_BAGS.get(bag_id)
        if not bag: return None
        fruit = cls.get_fruit_image(f"BRONZE_{seed_name}")
        if not fruit: return bag
        
        comp = bag.copy()
        bx, by = comp.get_rect().center
        fx, fy = fruit.get_rect().size
        comp.blit(fruit, (bx - fx//2, by - fy//2 - 2))
        cls._SEED_CACHE[key] = comp
        return comp
