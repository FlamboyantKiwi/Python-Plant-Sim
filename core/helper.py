import pygame
import os
from typing import Any
#Helper Function
def get_asset(fileName:str, path:str="assets") -> str: 
    """Returns the full cross-platform file path for a specific asset."""
    return os.path.join(path, fileName)

def calc_pos_rect(desired_width: int, desired_height: int, screen_width: int, screen_height: int, x_offset: int = 0, y_offset: int = 0) -> pygame.Rect:
    """Calculates coordinates to center a block on screen and returns a pygame.Rect."""
    return pygame.Rect(
        ((screen_width - desired_width) // 2) + x_offset,
        ((screen_height - desired_height) // 2) + y_offset,
        desired_width, 
        desired_height
    )

def get_axis(value:int, lessthan:str, greaterthan:str) -> str:
    """Returns 'lessthan' if value < 0, otherwise returns 'greaterthan'."""
    return lessthan if value < 0 else greaterthan
    
def get_direction(dx: int, dy: int, tick: int = 0) -> str|None:
    """Determines the primary direction (Up, Down, Left, Right) based on velocity and tick cycle."""
    abs_dx, abs_dy = abs(dx), abs(dy)
    if abs_dx == 0 and abs_dy == 0:
        return None
    # Alternation Tie-breaker (If abs_dx == abs_dy)
    if abs_dx == abs_dy:
        # Check if the tick falls into the first half of the 16-tick cycle
        if tick % 16 < 8:
            return get_axis(dx, "Left", "Right")
        else: # Even tick: Prioritize Vertical (Up/Down)
            return get_axis(dy, "Up", "Down")

    # Magnitude Priority (Non-Diagonal movement)
    if abs_dx > abs_dy:
        # Horizontal axis has the greatest speed
        return get_axis(dx, "Left", "Right")
    else: 
        # Vertical axis has the greatest speed
        return get_axis(dy, "Up", "Down")
    
def align_rect(rect: pygame.Rect, x: int, y: int, align: str = "center") -> pygame.Rect:
    """Sets a specific anchor point of a Rect to (x, y) coordinates."""
    try:
        setattr(rect, align, (x, y))
    except AttributeError:
        print(f"Align Error: '{align}' is not a valid Rect attribute. Defaulting to center.")
        rect.center = (x, y)
    return rect

def draw_text(screen: pygame.Surface, text:Any, font_key: str, x: int, y: int, colour_name: str|None = None, align: str = "center") -> None:
    """Renders text from the asset loader and blits it to the screen with alignment."""
    from core.asset_loader import ASSETS
    
    # Get Text Config bfrom its name
    config = ASSETS.get_text_config(font_key)
    if config is None:
        print(f"Error with text config: {font_key}")
        return
    
    # Get Optional Override Colour
    colour = ASSETS.get_colour(colour_name) if colour_name else None
    
    # Render (Config calls AssetLoader.get_font internally 
    # and handles font loading and default colours
    text_surf = config.render(str(text), colour)
    
    # Align + Draw
    rect = align_rect(text_surf.get_rect(), x, y, align)
    screen.blit(text_surf, rect)

def get_grid_pos(index: int, cols: int = 2, start: tuple[int, int] = (10, 130), size: tuple[int, int] = (50, 50), gap: tuple[int, int] = (10, 10)) -> tuple[int, int]:
    """Calculates the (x, y) pixel position for an item based on its index in a grid."""
    # 1. Logic: Convert linear index (0,1,2,3) to Grid (col, row)
    current_col = index % cols  
    current_row = index // cols 

    # 2. Math: Calculate pixel position
    # Position = Start + (Which Column * (Item Width + Gap Width))
    x = start[0] + (current_col * (size[0] + gap[0]))
    y = start[1] + (current_row * (size[1] + gap[1]))
    
    return x, y
