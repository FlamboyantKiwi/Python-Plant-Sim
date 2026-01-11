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

    # --- MASTER CONFIGURATION ---
    # This tells the loader HOW to load and read each entity type.
    # If you add "MONSTER" later, just add an entry here!
    ENTITY_SETTINGS = {
        "PLAYER": EntityConfig(
            sheets=PLAYER_SHEETS,
            folder="Player",
            states=PLAYER_STATES,
            directions=PLAYER_DIRECTIONS,
            frames=PLAYER_FRAMES),
        "ANIMAL": EntityConfig(
            sheets=ANIMAL_SHEETS,
            folder="Farm_Animals",
            states=ANIMAL_STATES,
            directions=ANIMAL_DIRECTIONS,
            frames={"Walk": 3, "Idle": 2})} # Default frames
        

    @classmethod
    def __init__(cls):
        # Prevent double loading if instantiated multiple times
        if cls.TILE_ASSETS: return
        cls.load_fruit_assets()
        cls.load_tool_assets()
        cls.load_tile_assets()
        cls.load_tile_detail_assets()
        
        for category, config in cls.ENTITY_SETTINGS.items():
            cls.ENTITIES[category] = cls.load_entity_group(
                names=config.sheets, 
                folder=config.folder, 
                states=config.states
            )
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
    def load_entity_group(cls, names:list, folder:str, states:dict):
        """ Loads a group of entities (Players, Animals, Monsters) that share structure.
        Returns: { 'SkinName': { 'State': [Images...] } } """
        group_assets = {}
        
        for name in names:
            group_assets[name] = {}
            sheet = cls.load_spritesheet(name, folder)
            if not sheet: continue

            # Loop through states (Walk, Idle, Run) using the Data Class Rects
            for state_name, rect in states.items():
                group_assets[name][state_name] = sheet.extract_tiles_by_dimensions(
                    start_x=rect.x, start_y=rect.y, 
                    region_width=rect.w, region_height=rect.h, 
                    tile_width=cls.TILE_SIZE, tile_height=cls.TILE_SIZE, 
                    scale_factor=cls.SCALE_FACTOR)
        return group_assets

    @classmethod
    def get_animated_sprite(cls, category: str, name: str, state: str, direction: str, tick: int):
        """ Universal function to get the correct frame for ANY moving entity. """
        # 1. Retrieve the specific entity's image set
        entity_library = cls.ENTITIES.get(category, {}) # Get Player or Animal dict
        sheet = entity_library.get(name)                # Get "Fox" or "Bull"
        if not sheet: return None

        # 2. Retrieve Configuration for this Category (Player vs Animal vs Monster)
        config = cls.ENTITY_SETTINGS.get(category)
        if not config: return None

        directions_map = config.directions
        frames_map = config.frames

        # 3. Determine Direction Offset
        # Logic: Handles both Flat (Animal) and Nested (Player) direction maps
        dir_offset = 0
        if isinstance(directions_map, dict):
            # Check Nested: {State: {Direction: Int}}
            if state in directions_map and isinstance(directions_map[state], dict):
                 dir_offset = directions_map[state].get(direction, 0)
            # Check Flat: {Direction: Int}
            elif direction in directions_map:
                 dir_offset = directions_map.get(direction, 0)

        # 4. Calculate Frame Index
        max_frames = frames_map.get(state, 1)
        current_frame = tick % max_frames
        sprite_index = (dir_offset * max_frames) + current_frame
        
        # 5. Retrieve Image
        images = sheet.get(state)
        if images and 0 <= sprite_index < len(images):
            return images[sprite_index]
            
        return None

    # ==================================================
    #   SPECIFIC LOADERS (Tools, Fruits, Tiles)
    # ==================================================

    @classmethod
    def load_tool_assets(cls):
        tool_sheet = cls.load_spritesheet("Tools_All")
        if not tool_sheet: return
        for row, material in enumerate(MATERIAL_LEVELS):
            cls.ALL_TOOLS[material] = {}
            for col, tool_type in enumerate(TOOL_TYPES):
                cls.ALL_TOOLS[material][tool_type] = tool_sheet.get_image(
                    x=col * cls.TILE_SIZE, y=row * cls.TILE_SIZE + 2,
                    width=cls.TILE_SIZE, height=cls.TILE_SIZE,
                    scale=(cls.ITEM_SIZE, cls.ITEM_SIZE)
                )
        print("Tool assets loaded successfully.")

    @classmethod
    def load_tile_assets(cls):
        """ Loads all tile assets, scales the base dirt tile, assigns it to 
        settings.DIRT_TILE, and returns the full dictionary of tileset lists. """
        # Load the SpriteSheet
        sheet = cls.load_spritesheet("exterior")
        if not sheet:  return
        # Dynamically Extract Marching Squares Tilesets (32x32 sprites)
        for key, rect in GROUND_TILE_REGIONS.items():
            cls.TILE_ASSETS[key] = sheet.extract_tiles_by_dimensions(
                rect.x, rect.y, rect.w, rect.h, 16, 16, cls.SCALE_FACTOR
            )
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
        if not sheet: return
        for tile_type, details in TILE_DETAILS.items():
            cls.TILE_DETAILS[tile_type] = []
            for d in details:
                cls.TILE_DETAILS[tile_type].extend(sheet.extract_tiles_by_dimensions(
                    d.x, d.y, d.w, d.h, d.tile_w, d.tile_h, cls.SCALE_FACTOR
                ))

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
            cls.ALL_FRUITS[name] = cls.create_fruit(sheet, pair.a, FRUIT_RANKS, num, 2)
            cls.ALL_FRUIT_CONTAINERS[name] = sheet.get_image(pair.b.x, pair.b.y, pair.b.w, pair.b.h)
            
        cls.SEED_BAGS = cls.create_fruit(sheet, SEED_BAGS_POS, ["1", "2"], 2, 3)
    
    @classmethod
    def create_fruit(cls, sheet: SpriteSheet, rect, ranks, number=3, scale_factor = None):
        """Helper for fruit strips."""
        items = {}
        w = rect.w // number
        scale = (w * scale_factor, rect.h * scale_factor)
        for i, rank in enumerate(ranks):
            items[rank] = sheet.get_image(rect.x + (i * w), rect.y, w, rect.h, scale)
        return items
    
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
