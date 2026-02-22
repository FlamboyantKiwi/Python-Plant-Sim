import pygame
from core.types import PlantData
from core.asset_loader import AssetLoader
from entities.physicsEntity import PhysicsEntity
from Assets.asset_data import get_plant_data

from settings import BLOCK_SIZE

class Plant(PhysicsEntity):
    def __init__(self, name: str, grid_x: int, grid_y: int):
        self.grid_x, self.grid_y = grid_x, grid_y
        
        # Get Logic Data (Growth time, is_tree, etc)
        self.data: PlantData = get_plant_data(name)
        
        # State
        self.age = 0.0
        self.days_old = 0
        
        # 1. Translate Grid to Absolute World Pixels
        world_pixel_x = grid_x * BLOCK_SIZE
        world_pixel_y = grid_y * BLOCK_SIZE
       
        initial_image = self._get_current_image()
        
        start_rect = initial_image.get_rect()
        start_rect.midbottom = (
            world_pixel_x + (BLOCK_SIZE // 2), 
            world_pixel_y + BLOCK_SIZE
        )
        
        # Create Hitbox (Slightly smaller than a block, sitting at the base of the plant)
        start_hitbox = pygame.Rect(0, 0, BLOCK_SIZE - 10, BLOCK_SIZE // 2)
        start_hitbox.midbottom = start_rect.midbottom
        
        # Initialize PhysicsEntity (Speed is 0, because plants don't walk!)
        super().__init__(
            image=initial_image,
            initial_rect=start_rect, 
            initial_hitbox=start_hitbox, 
            base_speed=0)
        
        # Make trees solid for collisions
        self.obstructed = getattr(self.data, 'is_tree', True)
    
    def _get_current_image(self) -> pygame.Surface:
        """Helper to generate the current stage key and fetch the image."""
        image_key = f"{self.data.name}_{self.data.get_stage_index(self.age)}"
        return AssetLoader.get_image(image_key)
    
    def grow(self, amount: float):
        """ Call this to test the animation stages """
        self.age += amount
        if self.age > self.data.grow_time:
            self.age = self.data.grow_time
        
        self.update_visuals()
        
    def update_visuals(self):
        """ Checks if the plant grew into a new stage and updates the sprite. """
        new_image = self._get_current_image()
        if new_image == self.image: return # Only update if the image changed
        
        self.image = new_image
        # Trees are taller than seeds, so we must re-anchor the midbottom to the ground!
        bottom_anchor = self.rect.midbottom
        self.rect = self.image.get_rect()
        self.rect.midbottom = bottom_anchor
            