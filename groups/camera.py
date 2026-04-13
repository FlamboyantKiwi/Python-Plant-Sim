from __future__ import annotations
import pygame
from typing import TYPE_CHECKING, cast

from settings import WIDTH, HEIGHT, DEBUG

if TYPE_CHECKING:
    from entities.player import Player
    from entities.entity import Entity

class CameraGroup(pygame.sprite.Group):
    def __init__(self)-> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    @property
    def entities(self) -> list['Entity']:
        """Returns a strictly-typed list of Entities for Pylance."""
        # By casting to Entity, Pylance knows everything in this list has a .hitbox
        return cast(list['Entity'], self.sprites())

    def custom_draw(self, player: Player)-> None:
        # Calculate Camera Offset (to keep player centered)
        self.offset.x = player.rect.centerx - WIDTH // 2
        self.offset.y = player.rect.centery - HEIGHT // 2

        # Sort by the bottom of the hitbox (Y-Sorting)
        # This ensures entities "lower" on screen are drawn last (on top)
        for sprite in sorted(self.entities, key=lambda sprite: sprite.hitbox.bottom):
            # Calculate offset position
            offset_x = int(sprite.rect.left - self.offset.x)
            offset_y = int(sprite.rect.top - self.offset.y)
            
            if sprite.image:
                self.display_surface.blit(sprite.image, (offset_x, offset_y))
            
            if DEBUG:
                pygame.draw.rect(self.display_surface, (0,255,0), sprite.rect.move(-self.offset.x, -self.offset.y), 1)
                pygame.draw.rect(self.display_surface, (255,0,0), sprite.hitbox.move(-self.offset.x, -self.offset.y), 1)
                
