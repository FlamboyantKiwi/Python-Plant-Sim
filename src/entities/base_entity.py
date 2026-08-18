from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.custom_types import Num, Group
    from src.entities import Player

class Entity(pygame.sprite.Sprite):
    """Absolute base class for anything that exists in the game world."""
    def __init__(self, image: pygame.Surface | None, initial_rect: pygame.Rect, 
                 initial_hitbox: pygame.Rect, *groups: Group, hitbox_offset: int = 10) -> None:
        super().__init__(*groups)
        self.image = image
        
        self.rect = initial_rect
        self.hitbox = initial_hitbox
        self.hitbox_offset = hitbox_offset
        
        # Snap the visual rect to the hitbox exactly once on creation
        self.sync_rect_to_hitbox()

    def sync_rect_to_hitbox(self) -> None:
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
    
    def draw(self, surface: pygame.Surface, offset_x: Num = 0, offset_y: Num = 0) -> None:
        """Standard drawing logic."""
        if self.image is None: 
            return
        draw_rect = self.rect.copy()
        draw_rect.x -= int(offset_x)
        draw_rect.y -= int(offset_x)
        surface.blit(self.image, draw_rect)

    def on_interact(self, player: 'Player') -> bool:
        """Default behavior when the player interacts with this object empty-handed."""
        return False
