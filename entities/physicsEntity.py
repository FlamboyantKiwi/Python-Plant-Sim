import pygame
from settings import WIDTH, HEIGHT

class PhysicsEntity(pygame.sprite.Sprite):
    """Base class for any entity that moves and respects collisions."""
    def __init__(self, initial_rect, initial_hitbox, base_speed):
        super().__init__()
        
        self.rect = initial_rect
        self.hitbox = initial_hitbox
        self.pos = pygame.math.Vector2(self.hitbox.center)
        self.direction = pygame.math.Vector2()
        
        self.current_speed = 0
        self.base_speed = base_speed

    def move(self, dt, collidable_objects):
        """Applies vector movement and handles axis-separated collisions."""
        if self.direction.magnitude() == 0: self.finalize_movement(); return
      
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

    @staticmethod
    def _hitbox_collide(entity, obj):
        """Custom Pygame collision callback to check hitboxes instead of visual rects."""
        target_rect = obj.hitbox if hasattr(obj, 'hitbox') else obj.rect
        return entity.hitbox.colliderect(target_rect)

    def check_horizontal(self, collidable_objects):
        """Resolves collisions on the X axis."""
        potential_hits = pygame.sprite.spritecollide(self, collidable_objects, False, collided=self._hitbox_collide) #type:ignore
        
        for obj in potential_hits:
            if getattr(obj, 'obstructed', False):
                target_rect = obj.hitbox if hasattr(obj, 'hitbox') else obj.rect
                
                if self.direction.x > 0: # Moving Right
                    self.hitbox.right = target_rect.left
                elif self.direction.x < 0: # Moving Left
                    self.hitbox.left = target_rect.right
                    
                self.pos.x = self.hitbox.centerx

    def check_vertical(self, collidable_objects):
        """Resolves collisions on the Y axis."""
        potential_hits = pygame.sprite.spritecollide(self, collidable_objects, False, collided=self._hitbox_collide) #type:ignore
        
        for obj in potential_hits:
            if getattr(obj, 'obstructed', False):
                target_rect = obj.hitbox if hasattr(obj, 'hitbox') else obj.rect
                
                if self.direction.y > 0: # Moving Down
                    self.hitbox.bottom = target_rect.top
                elif self.direction.y < 0: # Moving Up
                    self.hitbox.top = target_rect.bottom
                    
                self.pos.y = self.hitbox.centery

    def finalize_movement(self):
        """Clamps the hitbox to the screen and syncs all positioning variables."""
        # 1. Keep the physics hitbox inside the screen boundaries
        screen_bounds = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.hitbox.clamp_ip(screen_bounds)
        
        # 2. Sync the floating point math vector to the newly clamped hitbox
        self.pos.x = self.hitbox.centerx
        self.pos.y = self.hitbox.centery
        
        # 3. Snap the visual rendering rect to the final physics hitbox
        self.rect.centerx = self.hitbox.centerx
        self.rect.midbottom = self.hitbox.midbottom