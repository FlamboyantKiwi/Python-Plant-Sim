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
INTERACTION_DISTANCE = 20

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
MONEY_RECT = pygame.Rect(0, 10, WIDTH, 30)
PLAYER_START_INVENTORY = [
    ("gold_hoe", 1),
    ("wood_watering_can", 1),
    ("red_pepper_seeds", 5),
    ("apple", 3)
]
