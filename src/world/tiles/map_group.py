from __future__ import annotations

import pygame


class MapTileGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def custom_draw(self, camera_offset: pygame.math.Vector2) -> None:
        """Draws all tiles, applying the camera offset and snapping to integers 
        to prevent sprite tearing."""
        for tile in self.sprites():
            # Apply the offset and cast to int to prevent sub-pixel gaps
            offset_x = int(tile.rect.left - camera_offset.x)
            offset_y = int(tile.rect.top - camera_offset.y)
            
            self.display_surface.blit(tile.image, (offset_x, offset_y))
