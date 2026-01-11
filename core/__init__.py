# 1. Expose the Main Game Class
from .game import Game

# 2. Expose the Asset Management
from .asset_loader import AssetLoader
from .spritesheet import SpriteSheet

# 3. Expose common Helper functions
# Using 'from .helper import *' is okay here if helper.py is purely utility functions,
# but being explicit is better for tracking dependencies.
from .helper import (
    get_asset,
    load_image,
    load_sound,
    get_grid_pos,
    calc_pos_rect,
    get_colour,
    get_direction
)