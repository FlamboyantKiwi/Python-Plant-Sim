from core.types import SpriteRect, ScaleRect, EntityConfig, EntityState, AnimationGrid, FontType, TextConfig, Material, Quality, CropVisualData, UP, LEFT, RIGHT, DOWN
from settings import (
    HUD_FONT_SIZE, HUD_FONT_BOLD,
    SLOT_FONT_SIZE, SLOT_FONT_BOLD
)
from dataclasses import dataclass, field
import random
  
CROP_VISUALS = {
    # --- SINGLE HARVEST VEGETABLES ---
    "Beet": CropVisualData(
        container=SpriteRect(240, 192, 48, 16),
        fruit=SpriteRect(224, 60, 16, 32),
        world_art=SpriteRect(144, 404, 64, 36)),
    "Onion": CropVisualData(
        container=SpriteRect(48, 208, 48, 16),
        fruit=SpriteRect(192, 60, 16, 32),
        world_art=SpriteRect(144, 368, 64, 36)),
    "Cabbage": CropVisualData(
        container=SpriteRect(48, 192, 48, 16),
        fruit=SpriteRect(260, 11, 24, 32),
        world_art=SpriteRect(0, 211, 128, 24)),
    "Squash": CropVisualData(
        container=SpriteRect(96, 208, 48, 16),
        fruit=SpriteRect(0, 0, 32, 48),
        world_art=SpriteRect(0, 235, 128, 36)),
    "Cauliflower": CropVisualData(
        container=SpriteRect(0, 192, 48, 16),
        fruit=SpriteRect(128, 8, 32, 38),
        world_art=SpriteRect(0, 133, 128, 24)),
    "Melon": CropVisualData(
        container=SpriteRect(60, 160, 48, 32),
        fruit=SpriteRect(64, 0, 32, 48),
        world_art=SpriteRect(0, 280, 128, 36)),
    
    # --- REGROWING CROPS ---
    "Green Bean": CropVisualData(
        container=SpriteRect(0, 208, 48, 16),
        fruit=SpriteRect(160, 60, 16, 32),
        world_art=SpriteRect(0, 171, 128, 36)),
    "Cucumber": CropVisualData(
        container=SpriteRect(240, 144, 48, 16),
        fruit=SpriteRect(100, 60, 24, 32),
        world_art=SpriteRect(0, 53, 128, 42)),
    "Red Pepper": CropVisualData(
        container=SpriteRect(192, 160, 48, 16),
        fruit=SpriteRect(4, 60, 24, 32),
        world_art=SpriteRect(0, 95, 128, 36)),
    "Grape": CropVisualData(
        container=SpriteRect(240, 208, 48, 16),
        fruit=SpriteRect(196, 11, 24, 32),
        world_art=SpriteRect(0, 6, 128, 42)),
    "Pineapple": CropVisualData(
        container=SpriteRect(240, 160, 48, 32),
        fruit=SpriteRect(32, 0, 32, 48),
        world_art=SpriteRect(0, 316, 128, 36)),

    # --- MUSHROOMS ---
    "Mushroom": CropVisualData(
        container=SpriteRect(192, 192, 48, 16),
        fruit=SpriteRect(68, 60, 24, 32),
        world_art=SpriteRect(224, 404, 64, 36)),
    "Chestnut Mushroom": CropVisualData(
        container=SpriteRect(144, 208, 48, 16),
        fruit=SpriteRect(36, 60, 24, 32),
        world_art=SpriteRect(224, 368, 64, 36)),

    # --- TREES ---
    "Apple": CropVisualData(
        container=SpriteRect(192, 144, 48, 16),
        fruit=SpriteRect(228, 11, 24, 32),
        world_art=SpriteRect(128, 146, 255, 64),
        is_tree=True),
    "Lemon": CropVisualData(
        container=SpriteRect(240, 128, 48, 16),
        fruit=SpriteRect(128, 60, 16, 32),
        world_art=SpriteRect(128, 82, 255, 64),
        is_tree=True),
    "Plum": CropVisualData(
        container=SpriteRect(192, 208, 48, 16),
        fruit=SpriteRect(256, 60, 16, 32),
        world_art=SpriteRect(128, 4, 255, 78),
        is_tree=True),
    "Coconut": CropVisualData(
        container=SpriteRect(192, 176, 48, 16),
        fruit=SpriteRect(160, 8, 32, 38),
        world_art=SpriteRect(128, 290, 255, 78),
        is_tree=True),
    "Banana": CropVisualData(
        container=SpriteRect(0, 176, 48, 16),
        fruit=SpriteRect(96, 8, 32, 38),
        world_art=SpriteRect(128, 212, 255, 78),
        is_tree=True),

    # --- OTHERS (Missing Art) ---
    "Corn": CropVisualData(
        container=SpriteRect(0, 0, 16, 16),
        fruit=SpriteRect(0, 0, 16, 16),
        world_art=SpriteRect(0, 352, 128, 36)),
    "Sunflower": CropVisualData(
        container=SpriteRect(0, 0, 16, 16),
        fruit=SpriteRect(0, 0, 16, 16),
        world_art=SpriteRect(0, 396, 128, 36)),
    "Wheat": CropVisualData(
        container=SpriteRect(0,0,16,16),
        fruit=SpriteRect(0,0,16,16),
        world_art=SpriteRect(0,0,16,16)),
    "Tomato": CropVisualData(
        container=SpriteRect(0,0,16,16),
        fruit=SpriteRect(0,0,16,16),
        world_art=SpriteRect(0,0,16,16))
}

SEED_BAGS_POS = SpriteRect(240, 100, 32, 24) # 2 different seed bags

FRUIT_RANKS = (Quality.GOLD, Quality.SILVER, Quality.BRONZE)
TREE_FRAME_SLICES = [(0, 30), (32, 30), (66, 60), (131, 60), (195, 60) ]
PLANT_FRAME_ORDER = [0, 1, 3, 2]

# You can actually just dynamically grab all the materials directly from the Enum!
MATERIAL_LEVELS = list(Material)

TOOL_SPRITE_LAYOUT = [
    "MATERIAL", "DAGGER", "SWORD", "STAFF", "KNIFE", "BOW", "ARROW", "AXE", 
    "PICKAXE", "SHOVEL", "HOE", "HAMMER", "SCYTHE", "FISHING_ROD", "WATERING_CAN"
]

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
    "DEFAULT":        "#FF00FF", # Magenta for errors
    "DEBUG":          "#FF00FF",
    "TEXT":           "#FFFFFF",
    "HIGHLIGHT":      "#FFFF00",
    "HOVER":          "#9696FF",
    "SPRITESHEET":    "#FF00FF", # Fallback for missing sheets

    # Player & Inventory
    "PLAYER":         "#0000FF",
    "SLOT":           "#969696",
    "INVENTORY_SLOT": "#969696",
    "INV_TEXT":       "#FFFFFF",
    "MONEY":          "#FFD700",
    "GOLD":           "#FFD700",

    # Farming / World
    "UNTILLED":       "#5CCC61",
    "TILLED":         "#421F13",
    "PLANTED":        "#46641E",
    "WATER":          "#38DCF5",
    "SEED":           "#009600",
    
    # Shop
    "SHOP_MENU":      "#FAFAFA",
    "SHOP_BUTTON":    "#64C225",
    "SHOP_HOVER":     "#244210",
    "SHOP_TITLE":     "#000000",
    
    # Menu
    "MenuBG":         "#1E1E1E", # Dark Grey
    "MenuTitle":      "#FFD700", # Gold
    
    # Button
    "ButtonBG":       "#282828", # Dark Grey Background
    "ButtonBorder":   "#646464", # Light Grey Idle Border
    "ButtonHover":    "#FFD700", # Gold Hover Border
    "ButtonActive":   "#FFFFFF", # White
   
    "HOVER_COLOUR":   "#FFFFFF",
    "ACTIVE_COLOUR":  "#FFD700",
}


@dataclass
class MarchingLayout:
    """Blueprint for mapping bitmasks to spritesheet coordinates."""
    raw_mapping: dict
    
    # We will automatically build this in __post_init__
    mapping: dict = field(init=False)
    
    def __post_init__(self):
        self.mapping = {}
        for mask, data in self.raw_mapping.items():
            # 1. Convert everything to a list (even single tuples)
            if not isinstance(data, list):
                data = [data]
                
            # 2. Ensure every tuple has exactly 3 values: (row, col, rotation)
            cleaned_variants = []
            for item in data:
                if len(item) == 3:
                    cleaned_variants.append(item)
                else:
                    # Add a default rotation of 0
                    cleaned_variants.append((item[0], item[1], 0))
                    
            self.mapping[mask] = cleaned_variants

    def get_variant(self, mask: int, fallback_mask: int = 0) -> tuple[int, int, int]:
        """Returns a random (row, col, rotation) for the given mask."""
        # Try the requested mask. If missing, try the fallback mask (usually 0).
        variants = self.mapping.get(mask, self.mapping.get(fallback_mask, [(0, 0, 0)]))
        return random.choice(variants)

GRASS_LAYOUT = MarchingLayout({
    # 1-Sided Corners
    1: (2, 2),  
    2: (2, 0),  
    4: (0, 2),  
    8: (0, 0),
    
    # 2-Sided Adjacent Corners
    3: [(2, 1, 0), (2, 8, 0), (2, 9, 0)],
    5: [(1, 2, 0), (2, 8, 90), (2, 9, 90)],
    10: [(1, 0, 0), (1, 8, 90), (1, 9, 90), (0, 5, 0)],
    12: [(0, 1, 0), (1, 8, 0), (1, 9, 0), (0, 5, -90)],
    
    # Negative Mappings
    14: (1, 4), 13: (1, 3), 11: (0, 4), 7: (0, 3),
    
    # Diagonal Mappings
    9: [(0, 7, 0), (0, 8, 0), (1, 6, 0)],
    6: [(0, 6, 0), (0, 9, 0), (1, 7, 0)],
    
    # All / Nothing
    15: (1, 1), 
    0: (2, 3),  
})

DIRT_LAYOUT = MarchingLayout({
    # 1-Sided Corners
    1: (2, 2),  
    2: (2, 0),  
    4: (0, 2),  
    8: (0, 0),
    
    # 2-Sided Adjacent Corners (| Shapes)
    3: [(2, 1, 0), (1, 9, 0), (1, 8, 0)], 
    5: [(1, 2, 0), (1, 9, 90), (1, 8, 90)], 
    10: [(1, 0, 0), (0, 9, 90), (0, 8, 90), (0, 5, 0)], 
    12: [(0, 1, 0), (0, 9, 0), (0, 8, 0), (0, 5, -90)], 
    
    # Negative Mappings (L Shapes)
    14: (1, 4), 
    13: (1, 3), 
    11: (0, 4), 
    7: (0, 3),
    
    # Diagonal Mappings
    9: [(0, 7, 0), (1, 6, 0)], 
    6: [(0, 6, 0), (1, 7, 0)], 
    
    # All / Nothing
    15: (1, 1), 
    0: (2, 3),
})