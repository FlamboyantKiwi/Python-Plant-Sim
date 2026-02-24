from settings import WIDTH, HEIGHT, DEBUG
import pygame

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # 1. Calculate Camera Offset (to keep player centered)
        self.offset.x = player.rect.centerx - WIDTH // 2
        self.offset.y = player.rect.centery - HEIGHT // 2

        # 2. Sort by the bottom of the hitbox (Y-Sorting)
        # This ensures entities "lower" on screen are drawn last (on top)
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.hitbox.bottom):
            # Calculate offset position
            offset_x = int(sprite.rect.left - self.offset.x)
            offset_y = int(sprite.rect.top - self.offset.y)
            
            self.display_surface.blit(sprite.image, (offset_x, offset_y))
            
            if DEBUG:
                pygame.draw.rect(self.display_surface, (0,255,0), sprite.rect.move(-self.offset.x, -self.offset.y), 1)
                pygame.draw.rect(self.display_surface, (255,0,0), sprite.hitbox.move(-self.offset.x, -self.offset.y), 1)
                
