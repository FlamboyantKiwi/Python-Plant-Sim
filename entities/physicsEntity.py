import pygame
from settings import WIDTH, HEIGHT

class Entity(pygame.sprite.Sprite):
    """Absolute base class for anything that exists in the game world."""
    def __init__(self, image: pygame.Surface, initial_rect: pygame.Rect, initial_hitbox: pygame.Rect, hitbox_offset=10):
        super().__init__()
        self.image = image
        
        self.rect = initial_rect
        self.hitbox = initial_hitbox
        self.hitbox_offset = hitbox_offset
        
        # Snap the visual rect to the hitbox exactly once on creation
        self.sync_rect_to_hitbox()

    def sync_rect_to_hitbox(self):
        """Aligns the visual sprite with the physics hitbox."""
        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom + self.hitbox_offset

    def _calculate_hitbox(self, scale:float=1.0) -> pygame.Rect:
        """Calculates a hitbox dynamically based on the current image dimensions."""
        # Hitbox height is 1/3rd of the image height (so it just covers the trunk/base).
        # max() ensures it never shrinks to an impossible size (0/negative).
        hb_width = max(10, int((self.rect.width - 10) * scale))
        hb_height = max(10, self.rect.height // 3)
        
        return pygame.Rect(0, 0, hb_width, hb_height)
    
    def draw(self, surface: pygame.Surface, offset_x=0, offset_y=0):
        """Standard drawing logic."""
        if self.image is None: return
        draw_rect = self.rect.copy()
        draw_rect.x -= offset_x
        draw_rect.y -= offset_y
        surface.blit(self.image, draw_rect)

class MovingEntity(Entity):
    """Base class for entities that can move and collide dynamically."""
    def __init__(self, image: pygame.Surface, initial_rect: pygame.Rect, initial_hitbox: pygame.Rect, base_speed: int | float, hitbox_offset=10):
        # Pass the visual data up to the basic Entity class
        super().__init__(image, initial_rect, initial_hitbox, hitbox_offset)
        
        # Add movement-specific variables
        self.pos = pygame.math.Vector2(self.hitbox.center)
        self.direction = pygame.math.Vector2()
        self.current_speed = 0
        self.base_speed = base_speed

    @staticmethod
    def _hitbox_collide(entity, obj):
        """Custom Pygame collision callback to check hitboxes instead of visual rects."""
        target_rect = obj.hitbox if hasattr(obj, 'hitbox') else obj.rect
        return entity.hitbox.colliderect(target_rect)

    def move(self, dt, collidable_objects):
        """Applies vector movement and handles axis-separated collisions."""
        if self.direction.magnitude() == 0: 
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
        screen_bounds = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.hitbox.clamp_ip(screen_bounds)
        
        self.pos.x = self.hitbox.centerx
        self.pos.y = self.hitbox.centery
        
        # Call the parent class method to snap the visual rect to our newly moved hitbox!
        self.sync_rect_to_hitbox()
