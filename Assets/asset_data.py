from core.types import *
from settings import (
    HUD_FONT_SIZE, HUD_FONT_BOLD,
    SLOT_FONT_SIZE, SLOT_FONT_BOLD
)
from dataclasses import dataclass

@dataclass
class CropAsset:
    # --- Logic / Balance ---
    seed_price: int
    crop_price: int
    grow_time: int
    energy: int
    
    # --- Visuals ---
    fruit_container_image: SpriteRect  # The crate/seed bag
    fruit_image: SpriteRect            # The actual fruit sprite
    world_art: SpriteRect              # The growing plant sprite
    
    # --- Flags (Optional) ---
    regrows: bool|None = None
    is_tree: bool = False
    
    def __post_init__(self):
        """Runs automatically after the object is created."""
        if self.regrows is None:
            # If the user didn't specify, default to True for trees, False for plants
            self.regrows = self.is_tree
            
    def generate_seed_data(self, name: str, image_key: str) -> ItemData:
        return ItemData(
            name=f"{name} Seeds",
            description=f"Takes {self.grow_time} days to grow.",
            category=ItemCategory.SEED,
            image_key=f"{image_key}_seeds", 
            buy_price=self.seed_price,
            # Pass grow_time so the logic knows how long it takes
            grow_time=self.grow_time 
        )

    def generate_crop_data(self, name: str, image_key: str) -> ItemData:
        return ItemData(
            name=name,
            description=f"A fresh {name}. Restores energy.",
            category=ItemCategory.CROP,
            image_key=image_key,
            # We set buy_price to 0 (cannot be bought), 
            # but we explicitly set sell_price to override the __post_init__ halving logic
            buy_price=0,
            sell_price=self.crop_price,
            energy_gain=self.energy
        )

    def generate_plant_data(self, name: str, harvest_id: str) -> PlantData:
        if self.is_tree:    stage_count = 5
        else:               stage_count = 4
        return PlantData(
            name=name,
            grow_time=self.grow_time,
            harvest_item=harvest_id,
            
            image_stages=stage_count,     # The Integer (for math)
            image_rect=self.world_art,    # The Sprite (for rendering)
            
            is_tree=self.is_tree,
            regrows=self.regrows or False
        )
    

CROPS = {
    # --- SINGLE HARVEST VEGETABLES ---
    "Beet": CropAsset(
        10, 22, 3, 8,
        fruit_container_image=SpriteRect(240, 192, 48, 16),
        fruit_image=SpriteRect(224, 60, 16, 32),
        world_art=SpriteRect(144, 404, 64, 36)),
    "Onion": CropAsset(
        12, 28, 4, 10,
        fruit_container_image=SpriteRect(48, 208, 48, 16),
        fruit_image=SpriteRect(192, 60, 16, 32),
        world_art=SpriteRect(144, 368, 64, 36)),
    "Cabbage": CropAsset(
        20, 55, 6, 15,
        fruit_container_image=SpriteRect(48, 192, 48, 16),
        fruit_image=SpriteRect(260, 11, 24, 32),
        world_art=SpriteRect(0, 211, 128, 24)),
    "Squash": CropAsset(
        30, 75, 7, 20,
        fruit_container_image=SpriteRect(96, 208, 48, 16),
        fruit_image=SpriteRect(0, 0, 32, 48),
        world_art=SpriteRect(0, 235, 128, 36)),
    "Cauliflower": CropAsset(
        40, 95, 9, 30,
        fruit_container_image=SpriteRect(0, 192, 48, 16),
        fruit_image=SpriteRect(128, 8, 32, 38),
        world_art=SpriteRect(0, 133, 128, 24)),
    "Melon": CropAsset(
        50, 130, 10, 50,
        fruit_container_image=SpriteRect(60, 160, 48, 32),
        fruit_image=SpriteRect(64, 0, 32, 48),
        world_art=SpriteRect(0, 280, 128, 36)),
    
    # --- REGROWING CROPS ---
    "Green Bean": CropAsset(
        30, 20, 5, 12,
        fruit_container_image=SpriteRect(0, 208, 48, 16),
        fruit_image=SpriteRect(160, 60, 16, 32),
        world_art=SpriteRect(0, 171, 128, 36),
        regrows=True),
    "Cucumber": CropAsset(
        35, 25, 5, 15,
        fruit_container_image=SpriteRect(240, 144, 48, 16),
        fruit_image=SpriteRect(100, 60, 24, 32),
        world_art=SpriteRect(0, 53, 128, 42),
        regrows=True),
    "Red Pepper": CropAsset(
        40, 45, 7, 22,
        fruit_container_image=SpriteRect(192, 160, 48, 16),
        fruit_image=SpriteRect(4, 60, 24, 32),
        world_art=SpriteRect(0, 95, 128, 36),
        regrows=True),
    "Grape": CropAsset(
        45, 50, 8, 25,
        fruit_container_image=SpriteRect(240, 208, 48, 16),
        fruit_image=SpriteRect(196, 11, 24, 32),
        world_art=SpriteRect(0, 6, 128, 42),
        regrows=True),
    "Pineapple": CropAsset(
        150, 350, 14, 100,
        fruit_container_image=SpriteRect(240, 160, 48, 32),
        fruit_image=SpriteRect(32, 0, 32, 48),
        world_art=SpriteRect(0, 316, 128, 36),
        regrows=True),

    # --- MUSHROOMS ---
    "Mushroom": CropAsset(
        20, 40, 3, 20,
        fruit_container_image=SpriteRect(192, 192, 48, 16),
        fruit_image=SpriteRect(68, 60, 24, 32),
        world_art=SpriteRect(224, 404, 64, 36),
        regrows=True),
    "Chestnut Mushroom": CropAsset(
        25, 55, 4, 25,
        fruit_container_image=SpriteRect(144, 208, 48, 16),
        fruit_image=SpriteRect(36, 60, 24, 32),
        world_art=SpriteRect(224, 368, 64, 36),
        regrows=True),

    # --- TREES ---
    "Apple": CropAsset(
        100, 60, 10, 25,
        fruit_container_image=SpriteRect(192, 144, 48, 16),
        fruit_image=SpriteRect(228, 11, 24, 32),
        world_art=SpriteRect(128, 146, 255, 64),
        is_tree=True),
    "Lemon": CropAsset(
        120, 70, 11, 30,
        fruit_container_image=SpriteRect(240, 128, 48, 16),
        fruit_image=SpriteRect(128, 60, 16, 32),
        world_art=SpriteRect(128, 82, 255, 64),
        is_tree=True),
    "Plum": CropAsset(
        130, 75, 11, 30,
        fruit_container_image=SpriteRect(192, 208, 48, 16),
        fruit_image=SpriteRect(256, 60, 16, 32),
        world_art=SpriteRect(128, 4, 255, 78),
        is_tree=True),
    "Coconut": CropAsset(
        150, 90, 12, 40,
        fruit_container_image=SpriteRect(192, 176, 48, 16),
        fruit_image=SpriteRect(160, 8, 32, 38),
        world_art=SpriteRect(128, 290, 255, 78),
        is_tree=True),
    "Banana": CropAsset(
        180, 110, 13, 50,
        fruit_container_image=SpriteRect(0, 176, 48, 16),
        fruit_image=SpriteRect(96, 8, 32, 38),
        world_art=SpriteRect(128, 212, 255, 78),
        is_tree=True),

    # --- OTHERS  ---
    # WARNING: Corn/Sunflower are missing Inventory Art. Will look into later
    "Corn": CropAsset(
        10, 20, 4, 15,
        fruit_container_image=SpriteRect(0, 0, 16, 16), # MISSING
        fruit_image=SpriteRect(0, 0, 16, 16),           # MISSING
        world_art=SpriteRect(0, 352, 128, 36)
    ),
    "Sunflower": CropAsset(
        15, 40, 5, 20,
        fruit_container_image=SpriteRect(0, 0, 16, 16), # MISSING
        fruit_image=SpriteRect(0, 0, 16, 16),           # MISSING
        world_art=SpriteRect(0, 396, 128, 36)
    ),
    # WARNING: wheat/tomato are missing art!
    "Wheat": CropAsset(
        5, 10, 2, 5, 
        fruit_container_image=SpriteRect(0,0,16,16), # MISSING
        fruit_image=SpriteRect(0,0,16,16), # MISSING
        world_art=SpriteRect(0,0,16,16)),# MISSING
    "Tomato": CropAsset(
        25, 30, 6, 18, 
        fruit_container_image=SpriteRect(0,0,16,16), # MISSING
        fruit_image=SpriteRect(0,0,16,16), # MISSING
        world_art=SpriteRect(0,0,16,16), # MISSING
        regrows=True),
}

SEED_BAGS_POS = SpriteRect(240, 100, 32, 24) # 2 different seed bags

FRUIT_RANKS = ("GOLD", "SILVER", "BRONZE")
TREE_FRAME_SLICES = [(0, 30), (32, 30), (66, 60), (131, 60), (195, 60) ]
PLANT_FRAME_ORDER = [0, 1, 3, 2]

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
        harvest_item="none", image_stages=1, image_rect=SEED_BAGS_POS, is_tree=False, regrows=False)
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
for fruit_name, asset in CROPS.items():
    
    # Clean up name (e.g. "Green Bean" -> "green_bean")
    safe_id = fruit_name.lower().replace(" ", "_")

    # Generate Data using the unified CropAsset
    ITEMS[f"{safe_id}_seeds"] = asset.generate_seed_data(name=fruit_name, image_key=safe_id)
    ITEMS[safe_id] = asset.generate_crop_data(name=fruit_name, image_key=safe_id)
    PLANT_DATA[fruit_name] = asset.generate_plant_data(name=fruit_name, harvest_id=safe_id)

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
    "SLOT":          (150, 150, 150),
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
    
    # Button
    "ButtonBG": (40, 40, 40),           # Dark Grey Background
    "ButtonBorder": (100, 100, 100),    # Light Grey Idle Border
    "ButtonHover": (255, 215, 0),       # Gold Hover Border
    "ButtonActive": (255,255,255),       # White
   
    "HOVER_COLOUR": (255,255,255),
    "ACTIVE_COLOUR": (255, 215, 0),
}


MARCHING_TILES = {
    # Marching Squares Map Config
    # Format: Bitmask -> (Row, Col, Rotation)

    # 1-Sided Corners
    1: (2, 2),  # NW active
    2: (2, 0),  # NE active
    4: (0, 2),  # SW active
    8: (0, 0),  # SE active
    
    # 2-Sided Adjacent Corners (| Shapes)
    3: [(2, 1, 0), (2, 8, 0), (2, 9, 0)],  # NW, NE active
    5: [(1, 2, 0), (2, 8, 90), (2, 9, 90)],  # NW, SW active
    10: [(1, 0, 0), (1, 8, 90), (1, 9, 90), (0, 5, 0)], # NE, SE active
    12: [(0, 1, 0), (1, 8, 0), (1, 9, 0), (0, 5, -90)], # SW, SE active
    
    # Negative Mappings (Inverted/Not Grass)  (L Shape)
    # These masks represent when only the specified corner is DIRT (or inactive).
    # Mask is calculated as: 15 - Corner_Bit
    14: (1, 4),  # NOT NW active
    13: (1, 3),  # NOT NE active
    11: (0, 4),  # NOT SW active
    7: (0, 3),   # NOT SE active
    
    # Diagonal Mappings (Specific two-corner pattern) ( \ or / Shape)
    9: [(0, 7, 0), (0, 8, 0), (1, 6, 0)], # NW, SE active
    6: [(0, 6, 0), (0, 9, 0), (1, 7, 0)], # NE, SW active
    
    # All / Nothing
    15: (1, 1), # All active (Full Grass)
    0: (2,3),   # None active (All Dirt) - Fallback
}
