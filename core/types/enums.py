# THis file should contain only pure constants and Enums.

from enum import Enum, auto

class StateID(Enum):
    MENU = auto()
    PLAYING = auto()
    SHOP = auto()
    CHAR_SELECT = auto()
    HUD = auto()

class EntityState(Enum):
    WALK = "Walk"
    IDLE = "Idle"
    RUN = "Run"

class Direction(Enum):
    DOWN = "Down"
    UP = "Up"
    LEFT = "Left"
    RIGHT = "Right"
    
DOWN, UP, LEFT, RIGHT= Direction.DOWN, Direction.UP, Direction.LEFT, Direction.RIGHT
STANDARD_DIRECTIONS = [DOWN, UP, LEFT, RIGHT]

class EntityCategory(str, Enum):
    """Maps directly to the root asset folders for animated entities."""
    PLAYER = "Player"
    FARM_ANIMALS = "Farm_Animals"
    NPC = "NPCs"

class ItemType(Enum):
    # --- Tools ---
    TOOL         = ("tool", "generic")
    HOE          = ("tool", "hoe")
    WATERING_CAN = ("tool", "water")
    AXE          = ("tool", "axe")
    PICKAXE      = ("tool", "pick")
    SWORD        = ("tool", "sword")
    SCYTHE       = ("tool", "scythe") 
    ROD          = ("tool", "rod")
    # Combat
    DAGGER       = ("tool", "dagger")
    BOW          = ("tool","bow")
    STAFF        = ("tool","staff")
    # Misc
    HAMMER       = ("tool","hammer")
    SHOVEL       = ("tool","shovel")

    # --- Consumables ---
    SEED         = ("seed", "none")
    FRUIT        = ("fruit", "none")
    CROP         = ("crop", "none")
    
    # --- Resources ---
    WOOD         = ("misc", "none")
    STONE        = ("misc", "none")
    GENERIC      = ("misc", "none")

    def __init__(self, category: str, use_id: str):
        self.category = category
        self.use_id = use_id

class ItemCategory(Enum):
    SEED = "seed"
    TOOL = "tool"
    CROP = "crop"
    FRUIT = "fruit" 
    MISC = "misc"

class ToolType(Enum):
    # Farming
    HOE = "hoe"
    WATER = "water"
    # Gathering
    AXE = "axe"
    PICKAXE = "pick"
    ROD = "rod"
    # Combat
    SWORD = "sword"
    DAGGER = "dagger"
    BOW = "bow"
    STAFF = "staff"
    # Misc
    HAMMER = "hammer"
    SCYTHE = "scythe"
    SHOVEL = "shovel"
    # Fallback
    GENERIC = "generic"
    
class Material(Enum):
    WOOD = "WOOD"
    COPPER = "COPPER"
    IRON = "IRON"
    GOLD = "GOLD"

class Quality(Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"

class FontType(Enum):
    HUD = "HUD"
    SLOT = "SLOT"