from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from src.config import HEIGHT, WIDTH
from src.core import Direction, EntityState  ### check

from .base_entity import Entity

if TYPE_CHECKING:
    from src.custom_types import Group, Interactables, Num

class MovingEntity(Entity):
    """Base class for entities that can move and collide dynamically."""
    def __init__(self, image: pygame.Surface | None, initial_rect: pygame.Rect, 
                 initial_hitbox: pygame.Rect, base_speed: Num, *groups: Group, 
                 hitbox_offset: int = 10) -> None:
        # Pass the visual data up to the basic Entity class
        super().__init__(image, initial_rect, initial_hitbox, *groups, hitbox_offset=hitbox_offset)
        
        # Add movement-specific variables
        self.pos = pygame.math.Vector2(self.hitbox.center)
        self.direction = pygame.math.Vector2()
        self.current_speed:Num = 0
        self.base_speed = base_speed

        self.state: EntityState = EntityState.IDLE
        self.facing: Direction = Direction.DOWN

    @staticmethod
    def _hitbox_collide(entity:Any, obj:Any) -> bool:
        """Custom Pygame collision callback to check hitboxes instead of visual rects."""
        target_rect = getattr(obj, 'hitbox', obj.rect)
        return entity.hitbox.colliderect(target_rect)

    def move(self, dt:Num, collidable_objects:Interactables) -> None:
        """Applies vector movement and handles axis-separated collisions."""
        if self.direction.magnitude_squared() == 0: 
            self.finalize_movement()
            return
      
        # Horizontal Movement
        if self.direction.x != 0:
            self.pos.x += self.direction.x * self.current_speed * dt
            self.hitbox.centerx = round(self.pos.x)
            self.check_horizontal(collidable_objects)

        # Vertical Movement
        if self.direction.y != 0:
            self.pos.y += self.direction.y * self.current_speed * dt
            self.hitbox.centery = round(self.pos.y)
            self.check_vertical(collidable_objects)
        
        self.finalize_movement()

    def check_horizontal(self, collidable_objects:Interactables) -> None:
        """Resolves collisions on the X axis."""
        potential_hits = pygame.sprite.spritecollide(self, collidable_objects, False, collided=self._hitbox_collide) #type:ignore
        
        for obj in potential_hits:
            is_solid = getattr(obj, 'obstructed', False) or getattr(obj, '_base_obstructed', False)
        
            if is_solid:
                target_rect = obj.hitbox if hasattr(obj, 'hitbox') else obj.rect
                
                if self.direction.x > 0: # Moving Right
                    self.hitbox.right = target_rect.left
                elif self.direction.x < 0: # Moving Left
                    self.hitbox.left = target_rect.right
                    
                self.pos.x = self.hitbox.centerx

    def check_vertical(self, collidable_objects:Interactables) -> None:
        """Resolves collisions on the Y axis."""
        potential_hits = pygame.sprite.spritecollide(self, collidable_objects, False, collided=self._hitbox_collide) #type:ignore
        
        for obj in potential_hits:
            is_solid = getattr(obj, 'obstructed', False) or getattr(obj, '_base_obstructed', False)
        
            if is_solid:
                target_rect = obj.hitbox if hasattr(obj, 'hitbox') else obj.rect
                
                if self.direction.y > 0: # Moving Down
                    self.hitbox.bottom = target_rect.top
                elif self.direction.y < 0: # Moving Up
                    self.hitbox.top = target_rect.bottom
                    
                self.pos.y = self.hitbox.centery

    def finalize_movement(self) -> None:
        """Clamps the hitbox to the screen and syncs all positioning variables."""
        screen_bounds = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.hitbox.clamp_ip(screen_bounds)
        
        self.pos.x = self.hitbox.centerx
        self.pos.y = self.hitbox.centery
        
        # Call the parent class method to snap the visual rect to our newly moved hitbox!
        self.sync_rect_to_hitbox()
