import pygame, os
from settings import BLOCK_SIZE
#Helper Function
def get_asset(fileName, path="assets"): 
    """Gets the full, cross-platform path for a file in the assets folder.

    :param fileName: The name of the file in the asset folder.
    :type fileName: str
    :param path: The subdirectory path.
    :type path: str, optional
    :return: The full, combined path to the asset.
    :rtype: str """
    return os.path.join(path, fileName)

def calc_pos_rect(desired_width, desired_height, screen_width, screen_height, x_offset=0, y_offset=0):
    """Calculates the top-left (x, y) coordinates to center a block 
    of size (desired_width, desired_height) on the screen, 
    applies an offset, and returns the result as a pygame.Rect."""
    return pygame.Rect(
        ((screen_width - desired_width) // 2) + x_offset,
        ((screen_height - desired_height) // 2) + y_offset,
        desired_width, 
        desired_height
    )

def get_axis(value, lessthan, greaterthan):
    """ Categorizes a numeric value as negative, positive, or zero, returning 
    a specified descriptive string for each case.

    :param value: The numeric input being checked (e.g., delta_health, tick_difference).
    :param lessthan: The value to return if input is less than zero (negative).
    :param greaterthan: The value to return if input is greater than zero (positive).
    :return: 'lessthan', 'greaterthan', or 0 if the value is zero."""
    if value < 0:
        return lessthan
    else:
        return greaterthan
    
def get_direction(dx, dy, tick = 0):
    abs_dx, abs_dy = abs(dx), abs(dy)
    if abs_dx == 0 and abs_dy == 0:
        return None
    # 1. Alternation Tie-breaker (If abs_dx == abs_dy)
    if abs_dx == abs_dy:
        # Check if the tick falls into the first half of the 16-tick cycle
        if tick % 16 < 8:
            return get_axis(dx, "Left", "Right")
        else: # Even tick: Prioritize Vertical (Up/Down)
            return get_axis(dy, "Up", "Down")

    # 2. Magnitude Priority (Non-Diagonal movement)
    if abs_dx > abs_dy:
        # Horizontal axis has the greatest speed
        return get_axis(dx, "Left", "Right")
    else: 
        # Vertical axis has the greatest speed
        return get_axis(dy, "Up", "Down")
    
def align_rect(rect, x, y, align="center"):
    """Moves a rect so its specific anchor point matches the (x, y) coordinate.
    Example: align_rect(r, 100, 100, "topright") moves r so its topright is at 100,100."""
    try: # Dynamic handling: equivalent to rect.center = (x,y) or rect.topleft = (x,y)
        setattr(rect, align, (x, y))
    except AttributeError:
        print(f"Align Error: '{align}' is not a valid Rect attribute. Defaulting to center.")
        rect.center = (x, y)
    return rect

def draw_text(screen, text, font_key: str, x, y, colour_name=None, align="center"):
    """ Renders text using the global TEXT dict and aligns it to (x, y)."""
    from core.asset_loader import AssetLoader
    
    # Get Text Config bfrom its name
    config = AssetLoader.get_text_config(font_key)
    if config is None:
        print(f"Error with text config: {font_key}")
        return
    
    # Get Optional Override Colour
    colour = AssetLoader.get_colour(colour_name) if colour_name else None
    
    # Render (Config calls AssetLoader.get_font internally 
    # and handles font loading and default colours
    text_surf = config.render(str(text), colour)
    
    # Align + Draw
    rect = align_rect(text_surf.get_rect(), x, y, align)
    screen.blit(text_surf, rect)
