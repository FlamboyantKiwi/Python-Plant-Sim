# asset_loader.py
import pygame, os
from enum import Enum

from core.spritesheet import SpriteSheet
from core.helper import get_colour
from core.types import ItemCategory, EntityConfig, ItemData, FontType, EntityState, Direction
from Assets.asset_data import GAME_ENTITIES, MATERIAL_LEVELS, TILE_DETAILS, FRUIT_TYPES, FRUIT_RANKS, SEED_BAGS_POS, GROUND_TILE_REGIONS, TOOL_SPRITE_LAYOUT, PLANT_SPRITE_REGIONS, TREE_SPRITE_REGIONS, TREE_FRAME_SLICES
from settings import BLOCK_SIZE, HUD_FONT_SIZE, SLOT_FONT_SIZE

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
    ALL_PLANTS = {}

    # Cashes
    _SEED_CACHE = {}
    ENTITIES = {}
    FONTS:dict[FontType, pygame.font.Font] = {}

    @classmethod
    def __init__(cls):
        # Prevent double loading if instantiated multiple times
        if cls.TILE_ASSETS: return

        cls.load_resources()
        cls.load_fruit_assets()
        cls.load_tool_assets()
        cls.load_tile_assets()
        cls.load_tile_detail_assets()
        cls.load_plant_assets()
        
        for category, config in GAME_ENTITIES.items():
            cls.ENTITIES[category] = cls.load_entity_group(config)
        print("--- Assets Loaded ---")
    
    @classmethod
    def load_resources(cls):
        # Initialize font module specifically here if needed, 
        # though pygame.init() in Game usually covers it.
        if not pygame.font.get_init():
            pygame.font.init()
            
        font_config = {
            FontType.HUD:   (HUD_FONT_SIZE, True),
            FontType.SLOT:  (SLOT_FONT_SIZE, False),
        }

        # The Loop
        for font_enum, (size, is_bold) in font_config.items():
            try:
                # You can swap "arial" for a custom .ttf path here if you want
                cls.FONTS[font_enum] = pygame.font.SysFont("arial", size, bold=is_bold)
            except Exception as e:
                print(f"AssetLoader Error: Could not load font {font_enum.name}: {e}")
                # Create a generic fallback to prevent crashes
                cls.FONTS[font_enum] = pygame.font.SysFont("arial", 20)

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
            cls.ALL_TOOLS = cls.extract_grid(sheet, MATERIAL_LEVELS, TOOL_SPRITE_LAYOUT)
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
    def load_plant_assets(cls):        
        """ Loads growing plant sprites (Crops and Trees). """
        sheet = cls.load_spritesheet("Plants") 
        if not sheet: return

        # Load Crops: 4 frames per strip
        FRAMES_PER_STRIP = 4

        for crop_name, rect in PLANT_SPRITE_REGIONS.items():
            frame_width = rect.w // FRAMES_PER_STRIP
            
            for i in range(FRAMES_PER_STRIP):
                img = sheet.get_image(
                    x=rect.x + (i * frame_width),
                    y=rect.y,
                    width=frame_width,
                    height=rect.h,
                    scale=(frame_width * cls.SCALE_FACTOR, rect.h * cls.SCALE_FACTOR)
                )
                cls.ALL_PLANTS[f"{crop_name}_{i}"] = img

        # --- 2. LOAD TREES (Unevenly Spaced) ---
        for tree_name, rect in TREE_SPRITE_REGIONS.items():
            
            # Iterate through the manual slices defined in asset_data
            for i, (rel_x, width) in enumerate(TREE_FRAME_SLICES):
                
                img = sheet.get_image(
                    x=rect.x + rel_x,  # Start X + Offset
                    y=rect.y,
                    width=width,
                    height=rect.h,
                    # Scale trees up
                    scale=(width * cls.SCALE_FACTOR, rect.h * cls.SCALE_FACTOR)
                )
                
                # Key example: "Apple_0", "Apple_4"
                cls.ALL_PLANTS[f"{tree_name}_{i}"] = img
                
        print(f"Loaded plants: {len(PLANT_SPRITE_REGIONS)} crops, {len(TREE_SPRITE_REGIONS)} trees.")

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
    def get_animated_sprite(cls, category: str, name: str, state: EntityState, direction: Direction, frame: int):
        """ Universal function to get the correct frame for ANY moving entity. """
       # 1. Retrieve the specific entity's library
        entity_library = cls.ENTITIES.get(category, {}) 
        sheet_data = entity_library.get(name)             
        if not sheet_data: return None # Error

        # 2. Retrieve the State Dictionary (e.g. "Walk")
        # Handles cases where input might be an Enum or String
        s_key = state.value
        state_data = sheet_data.get(s_key)
        if not state_data: return None # Error

        # Retrieve the Direction List (e.g. "Down")
        d_key = direction.value
        
        # Fallback to DOWN if the specific direction is missing
        frames = state_data.get(d_key)
        if not frames:
            frames = state_data.get(Direction.DOWN) 
            if not frames: return None # Error

        # Calculate current frame (based on tick and total frames) 
        current_frame = int(frame) % len(frames)
        return frames[current_frame]

    # ==================================================
    #   SPECIFIC GETTERS
    # ==================================================

    @classmethod
    def get_image(cls, key: str) -> pygame.Surface | None:
        """ 
        Universal string-based lookup. 
        Used by the Plant class to find 'Apple_0', 'Corn_3', etc. 
        """
        # 1. Check Plants (Growing Stages)
        # Keys look like: "Corn_0", "Apple_4"
        if key in cls.ALL_PLANTS:
            return cls.ALL_PLANTS[key]
        
        # 2. Check Tools/Materials 
        # Keys look like: "WOOD_AXE", "IRON_HOE"
        if "_" in key:
            try:
                mat, typ = key.upper().split("_", 1)
                if mat in cls.ALL_TOOLS and typ in cls.ALL_TOOLS[mat]:
                    return cls.ALL_TOOLS[mat][typ]
            except: pass

        # 3. Check Fruits (Items)
        # If the key is just "Tomato", return the Bronze icon
        if key in cls.ALL_FRUITS:
            return cls.ALL_FRUITS[key].get("BRONZE")
        
        return cls.TILE_ASSETS.get("DIRT_IMAGE")

    
    @classmethod
    def get_item_image(cls, item_data:ItemData):
        """ Determines which loader to use based on the Item Category. """
        key = item_data.image_key
        cat = item_data.category

        if cat == ItemCategory.TOOL:
            return cls.get_tool_image(key)
            
        elif cat == ItemCategory.SEED:
            return cls.get_seed_image(key)
            
        elif cat in (ItemCategory.CROP, ItemCategory.FRUIT):
            # Crops default to the 'Bronze' rank visual for the inventory icon
            return cls.get_fruit_image(f"BRONZE_{key}")

        elif cat == ItemCategory.MISC:
            # Try tool sheet first (Materials usually live there)
            img = cls.get_tool_image(key)
            if img: return img
            
            # Fallback: Try fruit sheet
            return cls.get_fruit_image(f"BRONZE_{key}")
        
        # Fallback Error
        print(f"AssetLoader: No image loader defined for category: {cat}, key: {key}")
        return cls.TILE_ASSETS.get("DIRT_IMAGE")

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

    @classmethod
    def get_font(cls, font_type: FontType):
        """ Returns the requested font or a default system font if missing."""
        # Try to get the specific font
        font = cls.FONTS.get(font_type)
        if font: return font
            
        # Fallback
        print(f"AssetLoader Warning: Font '{font_type}' not found. Using default.")
        return pygame.font.SysFont("arial", 20)