from __future__ import annotations
import pygame
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from custom_types import Colour
#Helper Function

def calc_pos_rect(desired_width: int, desired_height: int, screen_width: int, screen_height: int, x_offset: int = 0, y_offset: int = 0) -> pygame.Rect:
    """Calculates coordinates to center a block on screen and returns a pygame.Rect."""
    return pygame.Rect(
        ((screen_width - desired_width) // 2) + x_offset,
        ((screen_height - desired_height) // 2) + y_offset,
        desired_width, 
        desired_height
    )

def align_rect(rect: pygame.Rect, x: int, y: int, align: str = "center") -> pygame.Rect:
    """Sets a specific anchor point of a Rect to (x, y) coordinates."""
    try:
        setattr(rect, align, (x, y))
    except AttributeError:
        print(f"Align Error: '{align}' is not a valid Rect attribute. Defaulting to center.")
        rect.center = (x, y)
    return rect

def draw_text(screen: pygame.Surface, text:Any, font_key: str, x: int, y: int, colour: Colour|None = None, align: str = "center") -> None:
    """Renders text from the asset loader and blits it to the screen with alignment."""
    from core.assets import ASSETS
    
    # Get Text Config bfrom its name
    config = ASSETS.config(font_key)
    if config is None:
        print(f"Error with text config: {font_key}")
        return
    
    # Get Optional Override Colour
    colour = ASSETS.colour(colour) if colour else None # type: ignore
     
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
