#spritesheet.py
import pygame

class SpriteSheet:
    path="SpriteSheets"
    def __init__(self, filename):
        from helper import get_asset
        try:
            self.name = filename
            self.sheet = pygame.image.load(get_asset(filename, self.path)).convert_alpha()
        except pygame.error as e:
            print(f"ERROR: Could not load sprite sheet {filename}. {e}")
            self.sheet = None # None if failured
    def get_image(self, x, y, width, height, scale=None):
        from helper import get_colour
        if scale is None:
            scale = width, height
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        if self.sheet is None:
            colour = get_colour(self.name.upper(), "SPRITESHEET")
            image.fill(colour)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        if scale != (width, height):
            image = pygame.transform.scale(image, scale)
        return image
    def extract_tiles_from_region(self, start_x, start_y, width, height, tile_size=16, final_scale=32):
        """ Extracts all 16x16 tiles from a defined region of the sprite sheet.
            
            :returns: A list of pygame.Surface objects. """
        tiles = []
        cols = width // tile_size
        rows = height // tile_size
        for row in range(rows):
            for col in range(cols):
                source_x = start_x + (col*tile_size)
                source_y = start_y + (row*tile_size)
                tiles.append(
                    self.get_image(
                    source_x, source_y, 
                    tile_size, tile_size, 
                    (final_scale,final_scale)
                ))
        return tiles