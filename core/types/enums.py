# THis file should contain only pure constants and Enums.

from enum import Enum

class EntityState(Enum):
    WALK = "Walk"
    IDLE = "Idle"
    RUN = "Run"

class Direction(Enum):
    DOWN = "Down"
    RIGHT = "Right"
    LEFT = "Left"
    UP = "Up"
DOWN, RIGHT, LEFT, UP = Direction.DOWN, Direction.RIGHT, Direction.LEFT, Direction.UP

class AnimalType(str, Enum):
    """Maps directly to the filenames in the Farm_Animals directory."""
    BULL = "Bull"
    CALF = "Calf"
    CHICK = "Chick"
    LAMB = "Lamb"
    PIGLET = "Piglet"
    ROOSTER = "Rooster"
    SHEEP = "Sheep"
    TURKEY = "Turkey"

class PlayerType(str, Enum):
    """Maps directly to the filenames in the Player directory."""
    BLUE_BIRD = "BlueBird"
    FOX = "Fox"
    GREY_CAT = "GreyCat"
    ORANGE_CAT = "OrangeCat"
    RACOON = "Racoon"  # Spelled with one 'C' to match the file!
    WHITE_BIRD = "WhiteBird"

class EntityCategory(str, Enum):
    """Maps directly to the root asset folders for animated entities."""
    PLAYER = "PLAYER"
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