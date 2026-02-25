#spritesheet.py
import pygame

class SpriteSheet:
    path="Assets"
    def __init__(self, filename):
        from core.asset_loader import ASSETS
        self.name = filename
        self.sheet = ASSETS.load_raw_image(filename)

        if self.sheet is None:
            print(f"ERROR: Could not load sprite sheet {filename}")
    def get_image(self, x, y, width, height, scale=None):
        if scale is None:
            scale = width, height
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        if self.sheet:
            image.blit(self.sheet, (0, 0), (x, y, width, height))
        else:
            from core.asset_loader import ASSETS
            colour = ASSETS.get_colour(self.name.upper(), "SPRITESHEET")
            image.fill(colour)

            
        if scale != (width, height):
            image = pygame.transform.scale(image, scale)
        return image

    def extract_tiles_by_dimensions(self, start_x, start_y, region_width, region_height, tile_width, tile_height, scale_factor = 1):
        tiles = []
        
        # Calculate number of columns and rows based on tile dimensions
        cols = region_width // tile_width
        rows = region_height // tile_height

        for row in range(rows):
            for col in range(cols):
                source_x = start_x + (col * tile_width)
                source_y = start_y + (row * tile_height)
                scale = (tile_width  * scale_factor, 
                         tile_height * scale_factor)
                tiles.append(
                    self.get_image(
                        source_x, source_y, 
                        tile_width, tile_height, 
                        scale
                    )
                )
        return tiles
    