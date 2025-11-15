# asset_loader.py
import pygame, os
from spritesheet import SpriteSheet
import settings 
from settings import BLOCK_SIZE, QUAD_SIZE

# Constants defining the tool grid structure
TOOL_TYPES = [
    "MATERIAL", "DAGGER", "SWORD", "STAFF", "KNIFE", 
    "BOW", "ARROW", "AXE", "PICKAXE", "SHOVEL", "HOE", 
    "HAMMER", "SCYTHE", "FISHING_ROD", "WATERING_CAN"]
MATERIAL_LEVELS = ["WOOD", "COPPER", "IRON", "GOLD"]

FRUIT_TYPES = { # type: rect - rect can be split into 3 fruit images: big, normal, small
    "Banana":           [(0, 176,   48, 16),
                        (96, 8,     32, 38)],
    "Cauliflower":      [(0, 192,   48, 16),
                         (128, 8,   32, 38)],
    "Cabbage":          [(48, 192,  48, 16),
                         (260, 11,  24, 32)],
    "Green Bean":       [(0, 208,   48, 16),
                         (160, 60,  16, 32)],
    "Onion":            [(48, 208,  48, 16),
                         (192, 60,  16, 32)],
    "Squash":           [(96, 208,  48, 16),
                         (0, 0,     32, 48)],
    "Chestnut Mushroom":[(144, 208, 48, 16),
                         (36, 60,   24, 32)],
    "Plum":             [(192, 208, 48, 16),
                         (256, 60,  16, 32)],
    "Grape":            [(240, 208, 48, 16),
                         (196, 11,  24, 32)],
    "Mushroom":         [(192, 192, 48, 16),
                         (68, 60,   24, 32)],
    "Beet":             [(240, 192, 48, 16),
                         (224, 60,  16, 32)],
    "Coconut":          [(192, 176, 48, 16),
                         (160, 8,   32, 38)],
    "Red Pepper":       [(192, 160, 48, 16),
                         (4, 60,    24, 32)],
    "Apple":            [(192, 144, 48, 16),
                         (228, 11,  24, 32)],
    "Cucumber":         [(240, 144, 48, 16),
                         (100, 60,  24, 32)],
    "Lemon":            [(240, 128, 48, 16),
                         (128, 60,  16, 32)],
    "Pineapple":        [(240, 160, 48, 32),
                         (32, 0,    32, 48)],
    "Melon":            [(60, 160,  48, 32), 
                         (64, 0,    32, 48)],
}
SEED_BAGS_POS = (240, 100, 32, 24) # 2 different seed bags

PLAYER_SHEETS = ["BlueBird", "Fox", "GreyCat", "OrangeCat", "Racoon", "WhiteBird"]

class AssetLoader:
    """Utility class to load and process all tile-related assets from sprite sheets."""
    ## --- Tile Attributes ---
    # Tool sprites are 16x16 in the sheet
    TILE_SIZE = 32
    DIRT_SPRITE_INDEX = 11 # Index for the preferred base dirt tile: (Row 1 * 10 columns) + Col 1 = 11
    TILE_ASSETS = {}

    ## --- Item Attributes ---
    # Item sprites are scaled to 36x36 for inventory/UI display
    ITEM_SIZE = 36
    ALL_TOOLS = {}
    ALL_FRUITS = {}
    SEED_BAGS = {}
    ALL_FRUIT_CONTAINERS = {}

    fruit_ranks = ("GOLD", "SILVER", "BRONZE")

    ## --- Player Attributes ---
    PLAYER_IMAGES = {}
    PLAYER_DIRECTIONS = { # X, Y, Width, Height, sprite_size = 32x32
    "Walk": (0, 0, 128, 128),
    "Idle": (0, 128, 128, 32),  
    "Run": (0, 160, 128, 256)}  
    DIRECTIONS = { 
    "Walk": {
        "Down":0, 
        "Right":1, 
        "Left":2, 
        "Up":3
    }, "Run": {
        "Down":0, 
        "Right":2, 
        "Left":1, 
        "Up":3
    }, "Idle": {
        "Down":0, 
        "Right":1, 
        "Left":3, 
        "Up":2
    }}
    PLAYER_FRAMES = {
        "Walk": 4,
        "Idle": 1,
        "Run": 8 }
    
    @classmethod
    def __init__(cls):
        cls.load_fruit_assets()
        cls.load_tool_assets()
        cls.load_tile_assets()
        cls.load_player_assets()
    @classmethod
    def create_fruit(cls, sheet: SpriteSheet, rect, ranks, number=3, scale_factor = None):
        new_fruit = {}
        x, y, width, height = rect
        item_width = width//number
        scale = (item_width*scale_factor, height*scale_factor)
        for i, rank in enumerate(ranks):
            offset_x = x + (i* item_width)
            new_fruit[rank] = sheet.get_image(offset_x, y, item_width, height, scale)
        return new_fruit
    
    # Load Functions
    @classmethod
    def load_tool_assets(cls):
        all_tools= {}

        try:
            tool_sheet = SpriteSheet("Tools_All.png")
            print("Loaded Tools_All.png spritesheet...")
        except Exception as e:
            print(f"Failed to load Tools_All.png sprite sheet: {e}")
            return all_tools
        
        for row_index, material in enumerate(MATERIAL_LEVELS):
            all_tools[material] = {}
            
            for col_index, tool_type in enumerate(TOOL_TYPES):
                # Calculate source coordinates (x, y) for the 16x16 sprite
                source_x = col_index * cls.TILE_SIZE
                source_y = row_index * cls.TILE_SIZE + 2
                
                # Extract and scale the image to the standard item size (36x36)
                tool_image = tool_sheet.get_image(
                    x=source_x,
                    y=source_y,
                    width=cls.TILE_SIZE,
                    height=cls.TILE_SIZE,
                    scale=(cls.ITEM_SIZE, cls.ITEM_SIZE)
                )
                
                all_tools[material][tool_type] = tool_image
        
        print("Tool assets loaded successfully.")
        cls.ALL_TOOLS = all_tools
    @classmethod
    def load_tile_assets(cls):
        """
        Loads all tile assets, scales the base dirt tile, assigns it to 
        settings.DIRT_TILE, and returns the full dictionary of tileset lists.
        """
        
        # 1. Load the SpriteSheet
        try:
            exterior_sheet = SpriteSheet("exterior.png")
            print("Loaded exterior spritesheet...")
        except Exception as e:
            print(f"Failed to load exterior sprite sheet: {e}")
            return {"GRASS_A_TILES": []} # Return empty set on failure

        # 2. Extract Marching Squares Tilesets (32x32 sprites)
        ground_tiles = {
            "GRASS_A_TILES": exterior_sheet.extract_tiles_from_region(0, 176, 160, 48, 16, QUAD_SIZE),
            "GRASS_B_TILES": exterior_sheet.extract_tiles_from_region(0, 224, 160, 48, 16, QUAD_SIZE),
            "DIRT_TILES": exterior_sheet.extract_tiles_from_region(0, 272, 160, 48, 16, QUAD_SIZE)
        }
        
        # 3. Overwrite DIRT_TILE in settings.py with the specific scaled sprite
        dirt_tileset = ground_tiles.get("DIRT_TILES")
        if dirt_tileset and len(dirt_tileset) > cls.DIRT_SPRITE_INDEX:
            dirt_sprite_32x32 = dirt_tileset[cls.DIRT_SPRITE_INDEX]
            
            # Scale the 32x32 sprite up to 64x64 (BLOCK_SIZE)
            scaled_dirt = pygame.transform.scale(dirt_sprite_32x32, (BLOCK_SIZE, BLOCK_SIZE))
            
            settings.DIRT_TILE = scaled_dirt
            print(f"settings.DIRT_TILE updated and scaled to 64x64 using sprite at index {cls.DIRT_SPRITE_INDEX}.")
        else:
            print(f"Warning: Could not load DIRT_TILE sprite at index {cls.DIRT_SPRITE_INDEX}. Using solid color fallback.")
            
        # 4. (Optional) You can add logic here to extract other single sprites like PLANT_TILE.
        
        cls.TILE_ASSETS = ground_tiles
    @classmethod
    def load_fruit_assets(cls):
        """Loads and organizes individual fruits/seeds and fruit containers from Supplies.png."""
        
        try:
            supplies_sheet = SpriteSheet("Supplies.png")
            print("Loaded Supplies.png spritesheet...")
        except Exception as e:
            print(f"Failed to load Supplies.png sprite sheet: {e}")
            return # Exit on failure
        
        for name, [fruit, container] in FRUIT_TYPES.items():
            if name == "Melon":
                fruit_num = 2
            else:
                fruit_num = 3
            cls.ALL_FRUITS[name] = cls.create_fruit(supplies_sheet, fruit, cls.fruit_ranks, fruit_num, scale_factor=2)
            x,y,w,h = container
            cls.ALL_FRUIT_CONTAINERS[name] = supplies_sheet.get_image(x,y,w,h)

        x, y, w, h = SEED_BAGS_POS
        cls.SEED_BAGS = cls.create_fruit(supplies_sheet, SEED_BAGS_POS, ["1", "2"], 2, scale_factor=3)
        print("Fruit and Container assets loaded successfully.")
    @classmethod
    def load_player_assets(cls):
        for player in PLAYER_SHEETS:
            player_images = {}
            player_sheet = SpriteSheet(os.path.join("Player", f"{player}.png"))
            if player_sheet is None:
                player_images = {}
                return None
            sprite_directions = cls.PLAYER_DIRECTIONS.keys()
            for direction in sprite_directions:
                x, y, w, h = cls.PLAYER_DIRECTIONS[direction]
                player_images[direction] = player_sheet.extract_tiles_from_region(x, y, w, h, 32, 64)

            cls.PLAYER_IMAGES[player] = player_images
        """print("Player Types: ", len(cls.PLAYER_IMAGES)) # 6 player types/skins
        print("Player Images: ", 
              len(cls.PLAYER_IMAGES["Fox"]["Walk"]), # 16 walk animations. 4 images for each direction
              len(cls.PLAYER_IMAGES["Fox"]["Run"]),  # 32 Run animations.  8 images for each direction
              len(cls.PLAYER_IMAGES["Fox"]["Idle"])) # 4 idle animations.  1 image for each direction"""

    # Get Functions
    @classmethod
    def get_player_image_direction(cls, sheet, state: str, direction: str, tick: int):
        movement_types = list(cls.PLAYER_DIRECTIONS.keys())
        if state not in movement_types:
            return
        if direction not in cls.DIRECTIONS[state]:
            return
        max_frames = AssetLoader.PLAYER_FRAMES[state]
        tick = tick % max_frames
        movement_images = sheet.get(state)
        direction_id = (cls.DIRECTIONS[state][direction] * max_frames) + tick
        return movement_images[direction_id]
    @classmethod
    def get_player_image(cls, player_type: str):
        if player_type in cls.PLAYER_IMAGES:
            return cls.PLAYER_IMAGES[player_type]
        print("Error!")
    @classmethod
    def get_tool_image(cls, tool_name: str):
        material, type  = tool_name.upper().split("_", 1)
        print(type, material)
        return cls.ALL_TOOLS.get(material).get(type)
    @classmethod
    def get_fruit_image(cls, fruit_name: str):
        rank, name  = fruit_name.split("_", 1)
        fruit_rank_dict = cls.ALL_FRUITS.get(name.title())
        return fruit_rank_dict.get(rank.upper())
    @classmethod
    def get_seed_image(cls, seed_name: str = "", bag_id = "1"):
        bag_surface = cls.SEED_BAGS.get(bag_id)
        fruit_surface = cls.get_fruit_image(f"BRONZE_{seed_name}")

        if bag_surface is None:
            print(f"Warning: Seed bag ID '{bag_id}' not found.")
            return None
        if fruit_surface is None:
            # If the fruit is missing, just return the bag
            return bag_surface.copy()
        
        # 2. Create the Composite Surface
        # Must use .copy() to avoid drawing on the original SEED_BAGS asset
        composite_image = bag_surface.copy()
        
        # 3. Calculate Centering Position
        # The image size is likely 36x36 (cls.ITEM_SIZE). We center the smaller fruit image 
        # slightly above the center to sit naturally on the bag opening.
        bag_rect = composite_image.get_rect()
        fruit_rect = fruit_surface.get_rect()
        
        # Center horizontally and position slightly up
        center_x = bag_rect.width // 2
        center_y = bag_rect.height // 2 - 2 # Shift up by 2 pixels

        blit_pos_x = center_x - (fruit_rect.width // 2)
        blit_pos_y = center_y - (fruit_rect.height // 2)

        # 4. Blit the Fruit onto the Bag
        composite_image.blit(fruit_surface, (blit_pos_x, blit_pos_y))
        
        return composite_image



    """
    @classmethod
    def load_level_assets(cls):
         Initializes the EXTERIOR SpriteSheet and extracts all GROUND_TILES and 
        the PLANT_TILE. Stores them as class attributes (cls.EXTERIOR, etc.).
        if cls.EXTERIOR is not None:
            print("Level assets already loaded.")
            return

        # 2. Load the SpriteSheet
        try:
            cls.EXTERIOR = SpriteSheet("exterior.png")
            print("loaded spritesheet...")
        except Exception as e:
            print(f"Failed to load exterior sprite sheet: {e}")
            return
        
        # print(cls.EXTERIOR.sheet) # Keep or remove print for debugging

        # 3. Extract GROUND_TILES
        cls.GROUND_TILES = {
            "GRASS_A_TILES": cls.EXTERIOR.extract_tiles_from_region(0, 176, 160, 48, 16, QUAD_SIZE),
            "GRASS_B_TILES": cls.EXTERIOR.extract_tiles_from_region(0, 224, 160, 48, 16, QUAD_SIZE),
            "DIRT_TILES":cls.EXTERIOR.extract_tiles_from_region(0, 272, 160, 48, 16, QUAD_SIZE)
        }

        dirt_tileset = cls.GROUND_TILES.get("DIRT_TILES")
        cls.DIRT_TILE = dirt_tileset[23]

         # 4. Extract PLANT_TILE 🌿 (Re-enabled the extraction)
        cls.PLANT_TILE = cls.EXTERIOR.get_image(
            x=9, 
            y=281, 
            width=32, 
            height=32, 
            #scale=(BLOCK_SIZE, BLOCK_SIZE)
        )

        pebbles = cls.EXTERIOR.extract_tiles_from_region(144, 112, 80, 16)
        little_rocks = cls.EXTERIOR.extract_tiles_from_region(48, 400, 192, 64, tile_size = 32)
            # add: (0, 400, 48, 48)
        #big rock: X = 0 Y = 40 Width = 48 Height = 48
        print("Level assets initialized successfully.")
    """