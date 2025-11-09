# settings.py
import pygame
pygame.init()

# Game/Screen Defaults
BLOCK_SIZE = 64
SPRITESHEET_SIZE = 16
QUAD_SIZE = BLOCK_SIZE//2 #32
WIDTH = 900
HEIGHT = 900
FPS = 60

#colours
COLOURS = {
    "PLAYER": (0, 0, 255),
    "UNTILLED": (92, 204, 97),
    "INVENTORY_SLOT": (150, 150, 150),
    "HIGHLIGHT": (255, 255, 0),
    "HOVER": (150, 150, 255),
    "SEED": (0, 150, 0),
    "TOOL": (69, 50, 31),
    "INV_TEXT": (255, 255, 255),
    "DEBUG": (255, 0, 255),
    "TILLED": (66, 31, 19),
    "PLANTED": (70, 100, 30),
    "WATER": (56, 220, 245),
    "SHOP_BUTTON": (100, 194, 37),
    "SHOP_HOVER": (36, 66, 16),
    "SHOP_MENU": (250, 250, 250)
    }
DEFAULT_COLOUR = COLOURS["DEBUG"]

IMAGE_LOAD_FAILURES = set()

try:
    DIRT_TILE = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
    DIRT_TILE.fill(COLOURS["TILLED"]) 
    
    WATER_TILE = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
    WATER_TILE.fill(COLOURS["WATER"])
    print("Basic tiles initialized upon settings import.")
except NameError as e:
    # This catch handles cases where BLOCK_SIZE or COLOURS might not be defined yet
    # You might not need this if your settings file is ordered correctly.
    print(f"Error initializing basic tiles in settings: {e}")
    DIRT_TILE = pygame.Surface((1, 1)) # Placeholder to prevent crash
    WATER_TILE = pygame.Surface((1, 1)) # Placeholder to prevent crash

# Inventory Defaults
INV_SIZE = 8
INV_PADDING = 5
SLOT_SIZE = 50
HIGHLIGHT_THICKNESS = 2
HUD_FONT = pygame.font.Font(None, 36)
SLOT_FONT = pygame.font.Font(None, 24)

#Shop Button
SHOP_BUTTON = pygame.Rect(BLOCK_SIZE//2, BLOCK_SIZE//2, BLOCK_SIZE, BLOCK_SIZE) 

SHOP_MENU_WIDTH = 400
SHOP_MENU_HEIGHT = 450
SHOP_MENU = pygame.Rect((WIDTH - SHOP_MENU_WIDTH) // 2,
                        (HEIGHT - SHOP_MENU_HEIGHT) // 2,
                        SHOP_MENU_WIDTH, SHOP_MENU_HEIGHT)
