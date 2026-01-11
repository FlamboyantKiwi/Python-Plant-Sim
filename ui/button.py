import pygame
from settings import  SLOT_FONT
from core.helper import get_image, get_colour
class Button(pygame.sprite.Sprite):
    def __init__(self, rect, text=None, font = SLOT_FONT, image_filename=""):
        super().__init__()
        self.rect = rect
        self.text = text
        self.font = font
        self.is_hovered = False

        self.image = get_image(image_filename, (self.rect.width, self.rect.height), "SHOP_BUTTON")
        self.hover_border = get_colour("SHOP_HOVER", "HIGHLIGHT")
        # Pre-render text for efficiency
        if self.text:
            self.text_surface = self.font.render(self.text, True, (255, 255, 255))
            self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, mouse_pos):
        """Checks for hover state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Draws the button surface and applies a border if hovered."""
        
        # Draw the main button surface (image or colored rect fallback)
        screen.blit(self.image, self.rect)

        # Draw a thin colored outline for hover feedback
        if self.is_hovered:
            # Use the stored hover_color for the border
            pygame.draw.rect(screen, self.hover_border, self.rect, 2) 
        
        # Draw the text overlay
        if self.text_surface:
            screen.blit(self.text_surface, self.text_rect)
    def is_click(self, mouse_pos):
        """Checks if the mouse position is inside the button."""
        return self.rect.collidepoint(mouse_pos)
        