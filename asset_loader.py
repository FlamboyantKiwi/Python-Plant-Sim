# asset_loader.py
import pygame
from spritesheet import SpriteSheet
import settings 
from settings import BLOCK_SIZE, QUAD_SIZE

# Constants defining the tool grid structure
TOOL_TYPES = [
    "MATERIAL", "DAGGER", "SWORD", "STAFF", "KNIFE", 
    "BOW", "ARROW", "AXE", "PICKAXE", "SHOVEL", "HOE", 
    "HAMMER", "SCYTHE", "FISHING_ROD", "WATERING_CAN"
]

MATERIAL_LEVELS = ["WOOD", "COPPER", "IRON", "GOLD"]

FRUIT_TYPES = { # type: rect - rect can be split into 3 fruit images: big, normal, small
    "Banana": (0, 176, 48, 16),
    "Cauliflower": (0, 192, 48, 16),
    "Cabbage": (48, 192, 48, 16),
    "Green Bean": (0, 208, 48, 16),
    "Onion": (48, 208, 48, 16),
    "Squash": (96, 208, 48, 16),
    "Chestnut Mushroom": (144, 208, 48, 16),
    "Plum": (192, 208, 48, 16),
    "Grape": (240, 208, 48, 16),
    "Mushroom": (192, 192, 48, 16),
    "Beet": (240, 192, 48, 16),
    "Coconut": (192, 176, 48, 16),
    "Red Pepper": (192, 160, 48, 16),
    "Apple": (192, 144, 48, 16),
    "Cucumber": (240, 144, 48, 16),
    "Lemon": (240, 128, 48, 16),
    "Pineapple": (240, 160, 48, 32),
    "Melon": (60, 160, 48, 32),
}
SEED_BAGS_POS = (240, 100, 32, 24) # 2 different seed bags
FRUIT_CONTAINERS = {
    "Squash": (0, 0, 32, 48),
    "Pineapple": (32, 0, 32, 48),
    "Melon": (64, 0, 32, 48),
    "Banana": (96, 8, 32, 38),
    "Cauliflower": (128, 8, 32, 38),
    "Coconut": (160, 8, 32, 38),
    "Grape": (196, 11, 24, 32),
    "Beet": (228, 11, 24, 32),
    "Cabbage": (260, 11, 24, 32),
    "Red Pepper": (4, 60, 24, 32),
    "Chestnut Mushroom": (36, 60, 24, 32),
    "Mushroom": (68, 60, 24, 32),
    "Cucumber": (100, 60, 24, 32),
    "Lemon": (128, 60, 16, 32),
    "Green Bean": (160, 60, 16, 32),
    "Onion": (192, 60, 16, 32),
    "Beet": (224, 60, 16, 32),
    "Plum": (256, 60, 16, 32),
}

class AssetLoader:
    """Utility class to load and process all tile-related assets from sprite sheets."""
    # Tool sprites are 16x16 in the sheet
    TILE_SIZE = 32
    # Item sprites are scaled to 36x36 for inventory/UI display
    ITEM_SIZE = 36

    # Index for the preferred base dirt tile: (Row 2 * 10 columns) + Col 3 = 23
    DIRT_SPRITE_INDEX = 23 

    ALL_TOOLS = {}
    ALL_FRUITS = {}
    SEED_BAGS = {}
    ALL_FRUIT_CONTAINERS = {}

    fruit_ranks = ("GOLD", "SILVER", "BRONZE")
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
        
        return ground_tiles
    
    @classmethod
    def create_fruit(cls, sheet, rect, ranks, number=3):
        new_fruit = {}
        x, y, width, height = rect
        item_width = width//number
        for i, rank in enumerate(ranks):
            offset_x = x + (i* item_width)
            new_fruit[rank] = sheet.get_image(offset_x, y, item_width, height)
        return new_fruit
    @classmethod
    def load_fruit_assets(cls):
        """Loads and organizes individual fruits/seeds and fruit containers from Supplies.png."""
        
        try:
            supplies_sheet = SpriteSheet("Supplies.png")
            print("Loaded Supplies.png spritesheet...")
        except Exception as e:
            print(f"Failed to load Supplies.png sprite sheet: {e}")
            return # Exit on failure
        
        for name, rect in FRUIT_TYPES.items():
            if name == "Melon":
                fruit_num = 2
            else:
                fruit_num = 3
            cls.ALL_FRUITS[name] = cls.create_fruit(supplies_sheet, rect, cls.fruit_ranks, fruit_num)

        
        for name, [x, y, w, h ] in FRUIT_CONTAINERS.items():
            # Scale containers to a large size (BLOCK_SIZE = 64)
            cls.ALL_FRUIT_CONTAINERS[name] = supplies_sheet.get_image(x, y, w, h)


        x, y, w, h = SEED_BAGS_POS
        cls.SEED_BAGS = cls.create_fruit(supplies_sheet, SEED_BAGS_POS, ["1", "2"], 2)
        print("Fruit and Container assets loaded successfully.")



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