from core.types import *
from settings import (
    HUD_FONT_SIZE, HUD_FONT_BOLD,
    SLOT_FONT_SIZE, SLOT_FONT_BOLD
)
from dataclasses import dataclass
# ==========================================
# GAMEPLAY BALANCE CONFIG
# ==========================================

FRUIT_RANKS = ("GOLD", "SILVER", "BRONZE")
CROP_BALANCE = {
    # --- SINGLE HARVEST CROPS (Standard) ---
    "Beet":             CropConfig(seed_price=10, crop_price=22, grow_time=3, energy=8),
    "Onion":            CropConfig(seed_price=12, crop_price=28, grow_time=4, energy=10),
    "Cabbage":          CropConfig(seed_price=20, crop_price=55, grow_time=6, energy=15),
    "Squash":           CropConfig(seed_price=30, crop_price=75, grow_time=7, energy=20),
    "Cauliflower":      CropConfig(seed_price=40, crop_price=95, grow_time=9, energy=30),
    "Melon":            CropConfig(seed_price=50, crop_price=130, grow_time=10, energy=50),
    "Wheat":            CropConfig(seed_price=5,  crop_price=10,  grow_time=2, energy=5),

    # --- REGROWING CROPS (Harvest multiple times) ---
    # These usually cost more upfront but pay off over time
    "Green Bean":       CropConfig(seed_price=30, crop_price=20, grow_time=5, energy=12, regrows=True),
    "Cucumber":         CropConfig(seed_price=35, crop_price=25, grow_time=5, energy=15, regrows=True),
    "Tomato":           CropConfig(seed_price=25, crop_price=30, grow_time=6, energy=18, regrows=True),
    "Red Pepper":       CropConfig(seed_price=40, crop_price=45, grow_time=7, energy=22, regrows=True),
    "Grape":            CropConfig(seed_price=45, crop_price=50, grow_time=8, energy=25, regrows=True),
    "Pineapple":        CropConfig(seed_price=150, crop_price=350, grow_time=14, energy=100, regrows=True),

    # --- MUSHROOMS (Fast growers, good energy) ---
    "Mushroom":         CropConfig(seed_price=20, crop_price=40, grow_time=3, energy=20, regrows=True),
    "Chestnut Mushroom":CropConfig(seed_price=25, crop_price=55, grow_time=4, energy=25, regrows=True),

    # --- TREES (Permanent, long growth, high yield) ---
    # Note: is_tree=True usually implies it blocks movement and takes 5 stages
    "Apple":            CropConfig(seed_price=100, crop_price=60, grow_time=10, energy=25, is_tree=True, regrows=True),
    "Lemon":            CropConfig(seed_price=120, crop_price=70, grow_time=11, energy=30, is_tree=True, regrows=True),
    "Plum":             CropConfig(seed_price=130, crop_price=75, grow_time=11, energy=30, is_tree=True, regrows=True),
    "Coconut":          CropConfig(seed_price=150, crop_price=90, grow_time=12, energy=40, is_tree=True, regrows=True),
    "Banana":           CropConfig(seed_price=180, crop_price=110, grow_time=13, energy=50, is_tree=True, regrows=True),
    # Others
    "Corn":             CropConfig(seed_price=10, crop_price=20, grow_time=4, energy=15),
    "Sunflower":        CropConfig(seed_price=15, crop_price=40, grow_time=5, energy=20),
}
DEFAULT_CROP = CropConfig(seed_price=10, crop_price=20, grow_time=3, energy=10)

PLANT_SPRITE_REGIONS = {
    "Grape":        SpriteRect(0, 6,   128, 42),
    "Cucumber":     SpriteRect(0, 53,  128, 42),
    "Red Pepper":   SpriteRect(0, 95,  128, 36),
    "Cauliflower":  SpriteRect(0, 133, 128, 24),
    "Green Bean":   SpriteRect(0, 171, 128, 36),
    "Cabbage":      SpriteRect(0, 211, 128, 24),
    "Squash":       SpriteRect(0, 235, 128, 36),
    "Melon":        SpriteRect(0, 280, 128, 36),
    "Pineapple":    SpriteRect(0, 316, 128, 36),
    "Corn":         SpriteRect(0, 352, 128, 36),
    "Sunflower":    SpriteRect(0, 396, 128, 36),

    "Onion":             SpriteRect(144, 368, 64, 36),
    "Chestnut Mushroom": SpriteRect(224, 368, 64, 36),
    "Beet":              SpriteRect(144, 404, 64, 36),
    "Mushroom":          SpriteRect(224, 404, 64, 36),
}

TREE_FRAME_SLICES = [
    (0, 30),    # Stage 0: Seed
    (32, 30),   # Stage 1: Sapling
    (66, 60),   # Stage 2: Growing
    (131, 60),  # Stage 3: Mature
    (195, 60)   # Stage 4: Fruiting
]
TREE_SPRITE_REGIONS = {
    "Plum":     SpriteRect(128, 4,   255, 78),
    "Lemon":    SpriteRect(128, 82,  255, 64),
    "Apple":    SpriteRect(128, 146, 255, 64),
    "Banana":   SpriteRect(128, 212, 255, 78),
    "Coconut":  SpriteRect(128, 290, 255, 78), 
}

# Materials
MATERIAL_MULTIPLIERS = { "WOOD": 1, "COPPER": 5, "IRON": 15, "GOLD": 50 }
MATERIAL_LEVELS = ["WOOD", "COPPER", "IRON", "GOLD"]

TOOL_SPRITE_LAYOUT = [
    "MATERIAL", "DAGGER", "SWORD", "STAFF", "KNIFE", "BOW", "ARROW", "AXE", 
    "PICKAXE", "SHOVEL", "HOE", "HAMMER", "SCYTHE", "FISHING_ROD", "WATERING_CAN"
]
TOOL_DEFINITIONS = [
    MaterialBP(sprite_suffix="MATERIAL", base_cost=10),
    ArrowBP(sprite_suffix="ARROW", base_cost=5),

    # Tools
    ToolBP(sprite_suffix="HOE",          base_cost=50,  tool_type=ToolType.HOE),
    ToolBP(sprite_suffix="WATERING_CAN", base_cost=50,  tool_type=ToolType.WATER, display_suffix="Watering Can"),
    ToolBP(sprite_suffix="AXE",          base_cost=100, tool_type=ToolType.AXE),
    ToolBP(sprite_suffix="PICKAXE",      base_cost=100, tool_type=ToolType.PICKAXE),
    ToolBP(sprite_suffix="FISHING_ROD",  base_cost=150, tool_type=ToolType.ROD, display_suffix="Fishing Rod"),

    # Weapons
    ToolBP(sprite_suffix="SWORD",  base_cost=200, tool_type=ToolType.SWORD),
    ToolBP(sprite_suffix="SCYTHE", base_cost=80,  tool_type=ToolType.SCYTHE),
    
    # 5. Generic / Unused (Defaults to Generic ToolType)
    ToolBP(sprite_suffix="DAGGER", base_cost=100),
    ToolBP(sprite_suffix="STAFF",  base_cost=250),
    ToolBP(sprite_suffix="BOW",    base_cost=150),
    ToolBP(sprite_suffix="HAMMER", base_cost=120),
    ToolBP(sprite_suffix="SHOVEL", base_cost=50, tool_type=ToolType.SHOVEL),
]

# ============ Get Data ============ #

def get_data(key:str, database:dict, fallback):
    """Generic safe-access function for any game database.
    :param key: The ID to look up (e.g. "tomato_seeds")
    :param database: The dictionary to search (e.g. ITEMS)
    :param fallback: The dummy object to return if missing"""
    if key in database:
        return database[key]
    
    print(f"WARNING: ID '{key}' not found in database.")
    return fallback
def get_item_data(item_id: str) -> ItemData:
    fallback_item = ItemData(name="Unknown", description="missing", 
        category=ItemCategory.MISC, image_key="None", buy_price=0)
    return get_data(item_id, ITEMS, fallback_item)
def get_plant_data(plant_name: str) -> PlantData:
    fallback_plant = PlantData(name="Unknown Plant", grow_time=1, 
        harvest_item="none", image_stages=1, is_tree=False, regrows=False)
    return get_data(plant_name, PLANT_DATA, fallback_plant)

# ============ Tiles ============ #
GROUND_TILE_REGIONS = {
    "GRASS_A": SpriteRect(0, 176, 160, 48),
    "GRASS_B": SpriteRect(0, 224, 160, 48),
    "DIRT":    SpriteRect(0, 272, 160, 48)
}
TILE_DETAILS = { #Rect: x, y, width, height, tile_width, tile_height
    "Dirt": [ 
        ScaleRect(0,   0,  320, 64,  32, 32),
        ScaleRect(128, 64, 192, 64,  32, 32),
        ScaleRect(0,   60, 128, 72,  32, 24),
        ScaleRect(320, 0,  16,  128, 16, 32)],
    "Grass": [
        ScaleRect(4,   134, 144, 48, 48, 48),
        ScaleRect(160, 128, 144, 48, 48, 48),
        ScaleRect(128, 136, 32,  32, 32, 32),
        ScaleRect(4,   189, 84,  32, 32, 32),
        ScaleRect(9,   224, 64,  32, 32, 32),
        ScaleRect(80,  224, 96,  32, 32, 32),
        ScaleRect(178, 256, 96,  32, 32, 32),
        ScaleRect(288, 128, 48,  48, 48, 48),
        ScaleRect(0,   256, 64,  32, 32, 32),
        ScaleRect(73,  256, 32,  32, 32, 32),
        ScaleRect(100, 184, 32,  32, 32, 32),
        ScaleRect(176, 240, 92,  16, 32, 16),
        ScaleRect(176, 176, 96,  64, 32, 32),
        ScaleRect(144, 184, 32,  32, 32, 32),
        ScaleRect(304, 176, 32,  32, 32, 32),
        ScaleRect(276, 184, 32,  32, 32, 32),
        ScaleRect(276, 248, 32,  32, 32, 32),
        ScaleRect(304, 224, 32,  32, 32, 32),
        ScaleRect(120, 256, 32,  32, 32, 32),
        ScaleRect(276, 224, 48,  48, 48, 48)]
}

# ============ Fruit ============ #
FRUIT_TYPES = { # type: rect - rect can be split into 3 fruit images: big, normal, small
    "Banana":           RectPair(SpriteRect(0,   176, 48, 16),  SpriteRect(96,  8,   32, 38)),
    "Cauliflower":      RectPair(SpriteRect(0,   192, 48, 16),  SpriteRect(128, 8,   32, 38)),
    "Cabbage":          RectPair(SpriteRect(48,  192, 48, 16),  SpriteRect(260, 11,  24, 32)),
    "Green Bean":       RectPair(SpriteRect(0,   208, 48, 16),  SpriteRect(160, 60,  16, 32)),
    "Onion":            RectPair(SpriteRect(48,  208, 48, 16),  SpriteRect(192, 60,  16, 32)),
    "Squash":           RectPair(SpriteRect(96,  208, 48, 16),  SpriteRect(0,   0,   32, 48)),
    "Chestnut Mushroom":RectPair(SpriteRect(144, 208, 48, 16),  SpriteRect(36,  60,  24, 32)),
    "Plum":             RectPair(SpriteRect(192, 208, 48, 16),  SpriteRect(256, 60,  16, 32)),
    "Grape":            RectPair(SpriteRect(240, 208, 48, 16),  SpriteRect(196, 11,  24, 32)),
    "Mushroom":         RectPair(SpriteRect(192, 192, 48, 16),  SpriteRect(68,  60,  24, 32)),
    "Beet":             RectPair(SpriteRect(240, 192, 48, 16),  SpriteRect(224, 60,  16, 32)),
    "Coconut":          RectPair(SpriteRect(192, 176, 48, 16),  SpriteRect(160, 8,   32, 38)),
    "Red Pepper":       RectPair(SpriteRect(192, 160, 48, 16),  SpriteRect(4,   60,  24, 32)),
    "Apple":            RectPair(SpriteRect(192, 144, 48, 16),  SpriteRect(228, 11,  24, 32)),
    "Cucumber":         RectPair(SpriteRect(240, 144, 48, 16),  SpriteRect(100, 60,  24, 32)),
    "Lemon":            RectPair(SpriteRect(240, 128, 48, 16),  SpriteRect(128, 60,  16, 32)),
    "Pineapple":        RectPair(SpriteRect(240, 160, 48, 32),  SpriteRect(32,  0,   32, 48)),
    "Melon":            RectPair(SpriteRect(60,  160, 48, 32),  SpriteRect(64,  0,   32, 48)),
}
SEED_BAGS_POS = SpriteRect(240, 100, 32, 24) # 2 different seed bags

# ============ Entities (Player, Animals) ============ #
GAME_ENTITIES = {
    "PLAYER": EntityConfig(
    folder="Player",
    sheets=["BlueBird", "Fox", "GreyCat", "OrangeCat", "Racoon", "WhiteBird"],
    animations={
        # WALK/RUN: Vertical Split
        EntityState.WALK:   AnimationGrid(SpriteRect(0, 0, 128, 128), [DOWN, RIGHT, LEFT, UP]),
        EntityState.RUN:    AnimationGrid(SpriteRect(0, 160, 128, 256), [DOWN, LEFT, RIGHT, UP]),
        # IDLE: Horizontal Split
        EntityState.IDLE:   AnimationGrid(SpriteRect(0, 128, 128, 32), [DOWN, RIGHT, UP, LEFT], is_vertical=False)}
    ),
    "ANIMAL": EntityConfig(
    folder="Farm_Animals",
    sheets=["Bull", "Calf", "Chick", "Lamb", "Piglet", "Rooster", "Sheep", "Turkey"],
    animations={
        EntityState.WALK:   AnimationGrid(SpriteRect(0, 0, 128, 128), [DOWN, UP, LEFT, RIGHT]),
        EntityState.IDLE:   AnimationGrid(SpriteRect(0, 128, 128, 128), [DOWN, UP, LEFT, RIGHT])}
    )
}

# ============ Items ============ #
ITEMS = {}
PLANT_DATA = {}

# --- GENERATE SEEDS & CROPS AUTOMATICALLY ---
for fruit_name in FRUIT_TYPES.keys():
    
    config = CROP_BALANCE.get(fruit_name, DEFAULT_CROP)

    # Clean up name (e.g. "Green Bean" -> "green_bean")
    safe_id = fruit_name.lower().replace(" ", "_")

    # Generate Data using the Class Methods
    ITEMS[f"{safe_id}_seeds"] = config.generate_seed_data(name=fruit_name, image_key=fruit_name)
    ITEMS[safe_id] = config.generate_crop_data(name=fruit_name, image_key=fruit_name)
    PLANT_DATA[fruit_name] = config.generate_plant_data(name=fruit_name, harvest_id=safe_id)


for mat in MATERIAL_LEVELS:
    multiplier = MATERIAL_MULTIPLIERS.get(mat, 1)
    
    for blueprint in TOOL_DEFINITIONS:
        # Use the Polymorphic Blueprint logic!
        item_id, item_data = blueprint.generate(mat, multiplier)
        ITEMS[item_id] = item_data

SHOPS = {
    "general_store": ShopData(
        store_name="General Store",
        items_ids=[
            "tomato_seeds",
            "melon_seeds",
            "red_pepper_seeds", # Now available because of your generator!
            "wood_axe", 
            "wood_sword",
            "apple"
        ]
    )
}


FONT_CONFIG = {
    FontType.HUD:   (HUD_FONT_SIZE, HUD_FONT_BOLD),
    FontType.SLOT:  (SLOT_FONT_SIZE, SLOT_FONT_BOLD),
}

TEXT = {
    "default": TextConfig(),
    "HUD": TextConfig(size=20, bold=True),
    "ACTIVE": TextConfig(size=20, bold=True, colour=(50, 50, 50)),
    "SLOT": TextConfig(size=14, colour=(255, 215, 0)),
    "TITLE": TextConfig(size=80, bold=True, colour=(255, 255, 255)),
    "MenuTitle": TextConfig(size=60, bold=True, colour=(255, 215, 0)),
}

        
# --- COLOUR PALETTE ---
COLOURS = {
    # UI & System
    "DEFAULT":       (255, 0, 255), # Magenta for errors
    "DEBUG":         (255, 0, 255),
    "TEXT":          (255, 255, 255),
    "HIGHLIGHT":     (255, 255, 0),
    "HOVER":         (150, 150, 255),
    "SPRITESHEET":   (255, 0, 255), # Fallback for missing sheets

    # Player & Inventory
    "PLAYER":        (0, 0, 255),
    "INVENTORY_SLOT":(150, 150, 150),
    "INV_TEXT":      (255, 255, 255),
    "MONEY":         (255, 215, 0),
    "GOLD":          (255, 215, 0),

    # Farming / World
    "UNTILLED":      (92, 204, 97),
    "TILLED":        (66, 31, 19),
    "PLANTED":       (70, 100, 30),
    "WATER":         (56, 220, 245),
    "SEED":          (0, 150, 0),
    
    # Shop
    "SHOP_MENU":     (250, 250, 250),
    "SHOP_BUTTON":   (100, 194, 37),
    "SHOP_HOVER":    (36, 66, 16),
    "SHOP_TITLE":    (0,  0,  0),
    
    # Menu
    "MenuBG":    (30, 30, 30),      # Dark Grey
    "MenuTitle": (255, 215, 0),     # Gold
}