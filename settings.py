# settings.py
import pygame

# Screen & Grid Configuration
BLOCK_SIZE = 64
TILES_X = 16
TILES_Y = 12

WIDTH = BLOCK_SIZE * TILES_X
HEIGHT = BLOCK_SIZE * TILES_Y

SPRITESHEET_SIZE = BLOCK_SIZE // 4
QUAD_SIZE = BLOCK_SIZE // 2

FPS = 60
ANIMATION_SPEED = 5 # Lower is faster (ticks per frame)

# Visuals & Colors
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
    "SHOP_MENU": (250, 250, 250),
    "GOLD": (255, 215, 0),
    "MONEY": (255, 215, 0),
    "TEXT": (255, 255, 255)}
DEFAULT_COLOUR = (255, 0, 255) # Magenta For Errors

IMAGE_LOAD_FAILURES = set()

# Gameplay Config
DETAIL_CHANCE = 0.2

# Inventory UI
INV_SIZE = 8
INV_PADDING = 5
SLOT_SIZE = 50
HIGHLIGHT_THICKNESS = 2

# UI / Fonts
HUD_FONT_SIZE = 20
HUD_FONT_BOLD = True

SLOT_FONT_SIZE = 14
SLOT_FONT_BOLD = False

# Shop UI
SHOP_MENU_WIDTH = 400
SHOP_MENU_HEIGHT = 450
SHOP_MENU = pygame.Rect((WIDTH - SHOP_MENU_WIDTH) // 2,
                        (HEIGHT - SHOP_MENU_HEIGHT) // 2,
                        SHOP_MENU_WIDTH, SHOP_MENU_HEIGHT)

#Shop Button Position
SHOP_BUTTON = pygame.Rect(BLOCK_SIZE//2, BLOCK_SIZE//2, BLOCK_SIZE, BLOCK_SIZE) 

PLAYER_START_INVENTORY = [
    ("wood_hoe", 1),
    ("wood_watering_can", 1),
    ("red_pepper_seeds", 5),
    ("apple", 3)
]
