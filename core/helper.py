import pygame, os
from settings import BLOCK_SIZE, COLOURS, DEFAULT_COLOUR, IMAGE_LOAD_FAILURES
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

def load_sound(fileName, volume=0.2, repeat=False): 
    """Loads a sound file, sets volume, and optionally plays it on a loop.

    :param fileName: The name of the sound file.
    :type fileName: str
    :param volume: The volume. Values above 1.0 may cause audio clipping.
    :type volume: float, optional, (0.0 or higher).
    :param repeat: If True, plays the sound in an infinite loop.
    :type repeat: bool, optional
    :return pygame.mixer.Sound: The loaded sound object. """
    sound = pygame.mixer.Sound(get_asset(fileName))
    sound.set_volume(max(0.0, volume))
    if repeat:
        sound.play(-1,0)
    return sound

def load_image(fileName, scale=None, factor=1, angle=0):
    """Loads an image, scales to exact dimensions 
    and/or proportionally by a factor, and applies rotation.

    :param fileName: The name of the image file.
    :type fileName: str
    :param scale: The exact (width, height) to scale to.
    :type scale: tuple, optional
    :param factor: A multiplier to scale the image by.
    :type factor: float, optional
    :param angle: Degrees to rotate the image counter-clockwise.
    :type angle: float, optional
    :return pygame.Surface: The loaded and transformed image surface."""
    try:
        img = pygame.image.load(get_asset(fileName)).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        if factor != 1:
            size = round(img.get_width() * factor), round(img.get_height() * factor)
            img = pygame.transform.scale(img, size)
        return pygame.transform.rotate(img, angle)
    except Exception as e:
        print(f"ERROR: Could not load image '{fileName}': {e}")
        fallback = pygame.Surface((48, 48))
        fallback.fill((255, 0, 255)) 
        return fallback

def get_grid_pos(pos):
    """Snaps a pixel coordinate to the nearest grid position."""
    # Integer division (//) and multiplication snaps the coordinate to the block size.
    return [(pos[0] // BLOCK_SIZE) * BLOCK_SIZE, 
            (pos[1] // BLOCK_SIZE) * BLOCK_SIZE]

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

def get_colour(name, fallback_type=None):
    # 1. Try Specific colour name
    final_colour = COLOURS.get(name)
    
    # 2. Try Fallback Type
    if final_colour is None and fallback_type:
        final_colour = COLOURS.get(fallback_type)
        
    # 3. Use Global Default if both fail
    if final_colour is None:
        final_colour = DEFAULT_COLOUR
        
    return final_colour

def get_image(image_name:str, scale, fallback_type=None):
    if image_name == None:
            image_name = fallback_type

    if image_name not in IMAGE_LOAD_FAILURES:
        try: # Load image based on image name
            image = pygame.image.load(get_asset(image_name)).convert_alpha()
            if scale:
                image = pygame.transform.scale(image, scale)
            return image
            
        except (pygame.error, FileNotFoundError, AttributeError) as e:
            # First time this file failed: log the error
            print(f"Warning: Failed to load image {image_name}. Falling back to color. Error: {e}")
            IMAGE_LOAD_FAILURES.add(image_name)

    ## Fallback to Colored Surface (Runs if try failed or was skipped)
    # 1. Get the fallback color using the tiered helper function
    colour = get_colour(image_name.upper(), fallback_type) 
    
    # 2. Create and fill the surface
    image = pygame.Surface(scale) 
    image.fill(colour)
    return image

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
    

def draw_text(screen, text, font, x, y, colour):
    text = font.render(text, True, colour)
    rect = text.get_rect(center=(x, y))
    screen.blit(text, rect)