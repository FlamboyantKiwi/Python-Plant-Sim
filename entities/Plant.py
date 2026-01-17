import pygame
from core.types import PlantData
from Assets.asset_data import get_plant_data
from core.asset_loader import AssetLoader
from settings import BLOCK_SIZE

class Plant:
    def __init__(self, name: str, x: int, y: int):
        self.x, self.y = x, y
        
        # Get Logic Data (Growth time, is_tree, etc)
        self.data: PlantData = get_plant_data(name)
        
        # State
        self.age = 0.0
        self.days_old = 0
        
    def grow(self, amount: float):
        """ Call this to test the animation stages """
        self.age += amount
        if self.age > self.data.grow_time:
            self.age = self.data.grow_time

    def draw(self, surface: pygame.Surface, offset_x=0, offset_y=0):
        # Calculate  the current growth stage image
        image_key = f"{self.data.name}_{self.data.get_stage_index(self.age)}"
        image = AssetLoader.get_image(image_key)
        if not image: return

        # Calculate Tile Position in pixels
        tile_pixel_x = (self.x * BLOCK_SIZE) - offset_x
        tile_pixel_y = (self.y * BLOCK_SIZE) - offset_y
        
        # Get the Rect of the image we are about to draw
        sprite_rect = image.get_rect()
        
        # Anchor the sprite:
        sprite_rect.midbottom = (
            tile_pixel_x + (BLOCK_SIZE // 2), 
            tile_pixel_y + BLOCK_SIZE
        )
        
        # Draw
        surface.blit(image, sprite_rect)