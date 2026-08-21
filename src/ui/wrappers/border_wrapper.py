from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from src.core.asset_loaders import ASSETS
from .base_wrapper import BaseWrapper

if TYPE_CHECKING:
    from src.ui.elements import StateElement


class BorderWrapper(BaseWrapper):
    """Dynamically draws a border around any StateElement based on its current state.""" 
    def __init__(self, target: StateElement, 
                 normal_colour: str = "ButtonBorder", 
                 hover_colour: str = "ButtonHover", 
                 active_colour: str = "ButtonActive", 
                 thickness: int = 2):
        
        super().__init__(target)
        self.surf_normal = self._create_border_surf(normal_colour, thickness)
        self.surf_hover = self._create_border_surf(hover_colour, thickness)
        self.surf_active = self._create_border_surf(active_colour, thickness + 1)

    def _create_border_surf(self, colour_name: str, thickness: int) -> pygame.Surface:
        """Helper to generate a transparent image with a baked-in border."""
        # Create a transparent surface exactly the size of the target
        surf = pygame.Surface(self.target.rect.size, pygame.SRCALPHA)
        col = ASSETS.colour(colour_name)
        
        # Draw the coloured border onto transparent surface
        pygame.draw.rect(surf, col, surf.get_rect(), thickness)
        return surf

    def draw(self, screen: pygame.Surface) -> None:
        if not self.target.is_visible:
            return

        # Draw the underlying target first
        self.target.draw(screen)

        if self.target.is_active:
            screen.blit(self.surf_active, self.target.rect)
        elif self.target.is_hovered:
            screen.blit(self.surf_hover, self.target.rect)
        else:
            screen.blit(self.surf_normal, self.target.rect)
    