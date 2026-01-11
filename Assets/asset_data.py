from dataclasses import dataclass
from typing import NamedTuple
# ============ Data Structures ============ #

@dataclass(frozen=True)
class SpriteRect:
    """Defines a basic region on a sprite sheet."""
    x: int
    y: int
    w: int
    h: int

@dataclass(frozen=True)
class ScaleRect(SpriteRect):
    """Defines a region containing multiple tiles of a specific size."""
    tile_w: int
    tile_h: int

@dataclass(frozen=True)
class RectPair:
    """ Used for Fruits.
    a: The Fruit Strip (3 frames: Gold, Silver, Bronze)
    b: The Container (Crate/Basket) """
    a: SpriteRect 
    b: SpriteRect

class EntityConfig(NamedTuple):
    """Blueprint for registering a new entity type."""
    sheets: list        # List of filenames (e.g. ["Fox", "Cat"])
    folder: str         # Folder name (e.g. "Player")
    states: dict        # The Rect definitions (e.g. PLAYER_STATES)
    directions: dict    # Direction mapping (e.g. PLAYER_DIRECTIONS)
    frames: dict        # Frame counts (e.g. PLAYER_FRAMES)

# ============ Tiles ============ #
# Constants defining the tool grid structure
TOOL_TYPES = [
    "MATERIAL", "DAGGER", "SWORD", "STAFF", "KNIFE", 
    "BOW", "ARROW", "AXE", "PICKAXE", "SHOVEL", "HOE", 
    "HAMMER", "SCYTHE", "FISHING_ROD", "WATERING_CAN"]
MATERIAL_LEVELS = ["WOOD", "COPPER", "IRON", "GOLD"]

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
FRUIT_RANKS = ("GOLD", "SILVER", "BRONZE")

# ============ Player ============ #
PLAYER_SHEETS = ["BlueBird", "Fox", "GreyCat", "OrangeCat", "Racoon", "WhiteBird"]

# X, Y, Width, Height, sprite_size = 32x32
PLAYER_STATES = { 
    "Walk": SpriteRect(0, 0, 128, 128),
    "Idle": SpriteRect(0, 128, 128, 32),
    "Run":  SpriteRect(0, 160, 128, 256)}  
PLAYER_DIRECTIONS = { 
    "Walk": {"Down":0, "Right":1, "Left":2, "Up":3}, 
    "Run":  {"Down":0, "Right":2, "Left":1, "Up":3}, 
    "Idle": {"Down":0, "Right":1, "Left":3, "Up":2}}
PLAYER_FRAMES = {"Walk": 4, "Idle": 1, "Run": 8}

# ============ Animals ============ #

ANIMAL_SHEETS = ["Bull", "Calf", "Chick", "Lamb", "Piglet", "Rooster", "Sheep", "Turkey"]

ANIMAL_DIRECTIONS = {"Down": 0,"Up": 1,"Left": 2,"Right": 3}
ANIMAL_STATES = { ### Needs new values!
    "Walk": SpriteRect(0, 0, 128, 128), 
    "Idle": SpriteRect(0, 128, 128, 128)
}