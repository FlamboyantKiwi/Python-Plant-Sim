from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple
from core.types import (ItemData, ItemCategory, SpriteRect, RectPair, ToolType,
    ScaleRect, EntityConfig, EntityState, AnimationGrid, UP, DOWN, LEFT, RIGHT)

# ==========================================
# GAMEPLAY BALANCE CONFIG
# ==========================================

# 1. CROP BALANCE
# Keys match FRUIT_TYPES keys. 
# Missing keys will use the 'DEFAULT' values.
CROP_BALANCE = {
    "DEFAULT":       {"seed_price": 10, "crop_price": 20, "grow_time": 3, "energy": 10},
    "Tomato":        {"seed_price": 15, "crop_price": 35, "grow_time": 4, "energy": 15},
    "Cauliflower":   {"seed_price": 40, "crop_price": 90, "grow_time": 8, "energy": 30},
    "Melon":         {"seed_price": 50, "crop_price": 120, "grow_time": 10, "energy": 50},
    "Pineapple":     {"seed_price": 100, "crop_price": 300, "grow_time": 14, "energy": 80},
    "Wheat":         {"seed_price": 5,  "crop_price": 10, "grow_time": 2, "energy": 5},
}

# 2. TOOL BALANCE
# Base costs for specific tool types
BASE_TOOL_COST = {
    "HOE": 50, "WATERING_CAN": 50, "AXE": 100, "PICKAXE": 100, 
    "SWORD": 200, "FISHING_ROD": 150, "SCYTHE": 80, "DEFAULT": 100
}

# Multipliers for materials
MATERIAL_MULTIPLIERS = { "WOOD": 1, "COPPER": 5, "IRON": 15, "GOLD": 50 }

FRUIT_RANKS = ("GOLD", "SILVER", "BRONZE")
MATERIAL_LEVELS = ["WOOD", "COPPER", "IRON", "GOLD"]

# ============ Data Structures ============ #

def get_item_data(item_id: str) -> ItemData:
    """Safe way to get item data. Returns a placeholder if missing."""
    if item_id in ITEMS:
        return ITEMS[item_id]
    
    # Fallback/Error Item
    print(f"WARNING: Item ID '{item_id}' not found in database.")
    return ItemData(name="Unknown",  description="misc", category=ItemCategory.MISC,  image_key="None", buy_price=0)

# ============ Tools ============ #
TOOL_SPRITE_LAYOUT = ["MATERIAL", "DAGGER", "SWORD", "STAFF", "KNIFE", "BOW", "ARROW", "AXE", 
    "PICKAXE", "SHOVEL", "HOE", "HAMMER", "SCYTHE", "FISHING_ROD", "WATERING_CAN"]

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

# --- GENERATE SEEDS & CROPS AUTOMATICALLY ---
for fruit_name in FRUIT_TYPES.keys():
    
    # Clean up name (e.g. "Green Bean" -> "green_bean")
    safe_id = fruit_name.lower().replace(" ", "_")
    stats = CROP_BALANCE.get(fruit_name, CROP_BALANCE["DEFAULT"])

    # Add the Seed
    ITEMS[f"{safe_id}_seeds"] = ItemData(
        name=f"{fruit_name} Seeds",
        description=f"Plant these to grow {fruit_name}. Takes {stats['grow_time']} days.",
        category=ItemCategory.SEED,
        image_key=fruit_name,

        buy_price=stats["seed_price"],
        grow_time=stats["grow_time"]
    )

    # Add the Crop/Fruit
    ITEMS[safe_id] = ItemData(
        name=fruit_name,
        buy_price=stats["crop_price"],
        category=ItemCategory.CROP,
        description=f"Fresh {fruit_name}. Restores {stats['energy']} energy.",
        image_key=fruit_name,
        energy_gain=stats["energy"]
    )

# --- GENERATE TOOLS AUTOMATICALLY ---

def _register_material_item(mat: str, sprite_key: str):
    """Creates raw resources like 'Wood', 'Iron'."""
    multiplier = MATERIAL_MULTIPLIERS.get(mat, 1)
    
    # Logic: Materials are named simply "Wood", not "Wood Material"
    item_id = mat.lower()
    
    ITEMS[item_id] = ItemData(
        name=mat.title(),
        # Raw materials are cheap but scale up
        buy_price=10 * multiplier, 
        category=ItemCategory.MISC,
        description=f"A raw piece of {mat.lower()}.",
        image_key=f"{mat}_{sprite_key}",
        stackable=True
    )

def _register_ammo_item(mat: str, sprite_key: str):
    """Creates ammo like 'Wood Arrow', 'Gold Arrow'."""
    multiplier = MATERIAL_MULTIPLIERS.get(mat, 1)
    
    item_id = f"{mat.lower()}_{sprite_key.lower()}"
    
    ITEMS[item_id] = ItemData(
        name=f"{mat.title()} Arrow",
        # Ammo is cheaper than tools
        buy_price=5 * multiplier,
        category=ItemCategory.MISC, # or ItemCategory.TOOL if you prefer
        description=f"A {mat.lower()}-tipped arrow.",
        image_key=f"{mat}_{sprite_key}",
        stackable=True
    )

def _register_tool_item(mat: str, sprite_key: str):
    """Creates weapons and tools like 'Wood Axe', 'Iron Sword'."""
    multiplier = MATERIAL_MULTIPLIERS.get(mat, 1)
    base_cost = BASE_TOOL_COST.get(sprite_key, 100)
    
    price = int(base_cost * multiplier)
    if mat == "WOOD": price = 0 # Starter tools are free?
    
    item_id = f"{mat.lower()}_{sprite_key.lower()}"
    
    # Dynamic behavior lookup
    behavior = getattr(ToolType, sprite_key, ToolType.GENERIC)

    ITEMS[item_id] = ItemData(
        name=f"{mat.title()} {sprite_key.replace('_', ' ').title()}",
        buy_price=price,
        category=ItemCategory.TOOL,
        description=f"A {mat.lower()} quality tool.",
        image_key=f"{mat}_{sprite_key}",
        tool_type=behavior,
        stackable=False
    )

for mat in MATERIAL_LEVELS:
    for sprite_key in TOOL_SPRITE_LAYOUT:
        
        # Traffic Cop Logic: Dispatch to the correct builder
        if sprite_key == "MATERIAL":
            _register_material_item(mat, sprite_key)
            
        elif sprite_key == "ARROW":
            _register_ammo_item(mat, sprite_key)
            
        else:
            # Everything else (Axes, Hoes, Swords) is a Tool
            _register_tool_item(mat, sprite_key)