import pygame
from core.types import PlantData
from core.asset_loader import AssetLoader
from entities.physicsEntity import Entity
from Assets.asset_data import get_plant_data

from settings import BLOCK_SIZE

class Plant(Entity):
    def __init__(self, name: str, grid_x: int, grid_y: int):
        self.grid_x, self.grid_y = grid_x, grid_y
        
        # Get Logic Data (Growth time, is_tree, etc)
        self.data: PlantData = get_plant_data(name)
        
        # State
        self.age = 0.0
        self.days_old = 0
        
        # Make trees solid for collisions and set their hitbox scale to 50%
        self.obstructed = getattr(self.data, 'is_tree', True)
        self.hitbox_scale = 0.5 if self.obstructed else 1.0
        
        # 1. Translate Grid to Absolute World Pixels
        world_pixel_x = grid_x * BLOCK_SIZE
        world_pixel_y = grid_y * BLOCK_SIZE
       
        initial_image = self._get_current_image()
        self.rect = initial_image.get_rect()
        
        self.rect.midbottom = (
            world_pixel_x + (BLOCK_SIZE // 2), 
            world_pixel_y + BLOCK_SIZE
        )
        
        # Create Hitbox (Slightly smaller than a block, sitting at the base of the plant)
        start_hitbox = self._calculate_hitbox(scale = self.hitbox_scale)
        start_hitbox.midbottom = self.rect.midbottom
        
        # Initialize PhysicsEntity (Speed is 0, because plants don't walk!)
        super().__init__(
            image=initial_image,
            initial_rect=self.rect, 
            initial_hitbox=start_hitbox)
    
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
        bottom_anchor = self.hitbox.midbottom
        self.rect = self.image.get_rect()
        self.hitbox = self._calculate_hitbox(scale=self.hitbox_scale)
        
        # 4. Re-anchor the new hitbox to the exact spot on the ground
        self.hitbox.midbottom = bottom_anchor
        
        # 5. Snap the newly sized visual rect back to the correctly placed hitbox
        self.sync_rect_to_hitbox()
            