from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.config import BLOCK_SIZE

# Runtime Imports
from src.core import ASSETS, PlantData
from src.utils import Log

from .base_entity import Entity

# Type-Only Imports
if TYPE_CHECKING:
    from src.custom_types import Group, Player

class Plant(Entity):
    def __init__(self, plant_id: str, grid_x: int, grid_y: int, *groups:Group) -> None:
        self.plant_id = plant_id
        self.grid_x, self.grid_y = grid_x, grid_y
        
        # Get Logic Data (Growth time, is_tree, etc)
        self.data: PlantData = ASSETS.plant(plant_id)
        
        # State
        self.age:float = 0.0
        self.days_old:int = 0
        self.is_harvested:bool = False
        
        # Make trees solid for collisions and set their hitbox scale to 50%
        self.obstructed = self.data.is_tree
        self.hitbox_scale = 0.5 if self.obstructed else 1.0
        
        # Translate Grid to Absolute World Pixels
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
        
        # Initialize Entity
        super().__init__(initial_image, self.rect, start_hitbox, *groups)
        
    @property
    def is_dead(self) -> bool:
        """Returns True if the crop has been harvested and will not regrow."""
        return self.is_harvested and not self.data.regrows and not self.data.is_tree
    
    def _get_current_image(self) -> pygame.Surface:
        """Helper to generate the current stage key and fetch the image."""
        image_key = f"{self.data.name}_{self.data.get_stage_index(self.age, self.is_harvested)}"
        return ASSETS.get_image(image_key)
    
    def grow(self, amount: float) -> None:
        """ Call this to test the animation stages """
        self.age += amount
        self.age = min(self.age, self.data.grow_time)
        
        self.update_visuals()

    def harvest(self) -> str|None:
        """Triggers when player interacts with fully grown crops"""
        if self.age >= self.data.grow_time and not self.is_harvested:

            # Spawn item
            yielded_item_id = self.data.harvest_item
            # Change Visuals
            if self.data.regrows or self.data.is_tree:
                # Drop the age back to 75%. resume growing 
                self.age = self.data.grow_time * 0.75 
            else:
                # Single harvest crop permanently transitions to Frame 4 (Stump/Empty)
                self.is_harvested = True
                
            self.update_visuals()
            return yielded_item_id
            
        return None

    def on_interact(self, player: Player) -> bool:
        """ When player clicks on this plant with empty hand, ,try harvest it"""
        harvested_item_id = self.harvest()
        
        if harvested_item_id:
            # Try to push it into the player's inventory
            if player.receive_item(harvested_item_id):
                return True
            else:
                Log.error("Inventory is full! Cannot harvest.")
                # (Optional: Revert the harvest state here if you want them to try again later)
                return False
                
        return False
    
    def update_visuals(self) -> None:
        """ Checks if the plant grew into a new stage and updates the sprite. """
        new_image = self._get_current_image()
        if new_image == self.image: 
            return # Only update if the image changed
        
        self.image = new_image
        # Trees are taller than seeds, so we must re-anchor the midbottom to the ground!
        bottom_anchor = self.hitbox.midbottom
        self.rect = self.image.get_rect()
        self.hitbox = self._calculate_hitbox(scale=self.hitbox_scale)
        
        # Re-anchor the new hitbox to the exact spot on the ground
        self.hitbox.midbottom = bottom_anchor
        
        # Snap the newly sized visual rect back to the correctly placed hitbox
        self.sync_rect_to_hitbox()

    def till(self) -> bool:
        if self.is_dead:
            if self.tile:
                self.tile.occupant = None
            self.kill()
            Log.success("Cleared dead plant!")
            return True
        return False