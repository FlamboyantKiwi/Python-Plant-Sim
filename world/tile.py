import pygame
from settings import  BLOCK_SIZE
from core.asset_loader import AssetLoader

class Tile(pygame.sprite.Sprite):
    """The Base Class. Holds the factory method and basic visual/position data."""
    def __init__(self, level, x, y, tile_type_key: str, neighbors: list[bool], detail_image=None):
        self.level = level
        super().__init__()
        self.grid_x = int(x // BLOCK_SIZE)
        self.grid_y = int(y // BLOCK_SIZE)
        self.position = (x, y)
        self.tile_type_key = tile_type_key
        self.detail_image = detail_image
        
        # Base variables EVERY tile needs
        if not hasattr(self, 'obstructed'): 
            self.obstructed = False

        # Generate initial visual
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.refresh_terrain(neighbors)
        self.rect = self.image.get_rect(topleft=self.position)

    @classmethod
    def create(cls, level, x, y, tile_type_key: str, neighbors: list[bool], detail_image=None):
        """THE FACTORY: Looks at the key and returns the correct subclass!"""
        if tile_type_key == "WATER":
            return WaterTile(level, x, y, tile_type_key, neighbors, detail_image)
        else:
            return GroundTile(level, x, y, tile_type_key, neighbors, detail_image)

    def refresh_terrain(self, new_neighbors: list[bool]):
        """Generates the base visual. Subclasses will extend this."""
        pass
    
# Subclasses 
    
class GroundTile(Tile):
    """Tile containing all farming logic."""
    def __init__(self, level, x, y, tile_type_key: str, neighbors: list[bool], detail_image=None):
        
        # Only GroundTiles get farming variables!
        self.plant = None
        self.is_tilled = False
        self.tillable = (tile_type_key in ["GRASS_A", "GRASS_B", "DIRT"])
        self.watered = False
        
        # Call the parent __init__ to set up position and visuals
        super().__init__(level, x, y, tile_type_key, neighbors, detail_image)
        

    def refresh_terrain(self, new_neighbors: list[bool]):
        dirt_img = AssetLoader.get_image("DIRT_IMAGE")
        self.base_image = dirt_img.copy() if dirt_img else pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        if not dirt_img: self.base_image.fill((139, 69, 19)) # Fallback brown
        
        # LAYER 2: Draw the Grass marching squares over the dirt
        if any(new_neighbors):
            # Crucial Fix: Always use a GRASS tileset to draw the grass overlay!
            grass_key = self.tile_type_key if "GRASS" in self.tile_type_key else "GRASS_A"
            grass_overlay = AssetLoader.get_marching_tile(grass_key, new_neighbors)
            self.base_image.blit(grass_overlay, (0, 0))

        self.image = self.base_image.copy()

        # LAYER 3: Draw static details (Pebbles, flowers, etc.)
        if self.detail_image:
            detail_rect = self.detail_image.get_rect(center=(BLOCK_SIZE // 2, BLOCK_SIZE // 2))
            self.image.blit(self.detail_image, detail_rect)
            
        # LAYER 4: Draw farming overlays (Tilled soil, water)
        if self.is_tilled:
            tilled_img = AssetLoader.get_image("tilled_soil")
            if tilled_img:
                self.image.blit(tilled_img, tilled_img.get_rect(center=(BLOCK_SIZE//2, BLOCK_SIZE//2)))


class WaterTile(Tile):
    """Tile representing water. Blocks movement."""
    def __init__(self, level, x, y, tile_type_key: str, neighbors: list[bool], detail_image=None):
        self.obstructed = True
        super().__init__(level, x, y, tile_type_key, neighbors, detail_image)
        
        
    def refresh_terrain(self, new_neighbors: list[bool]):
        # A simple, static block of water. (Keeps memory low!)
        self.base_image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.base_image.fill((56, 220, 245)) # Cyan Water
        self.image = self.base_image.copy()

