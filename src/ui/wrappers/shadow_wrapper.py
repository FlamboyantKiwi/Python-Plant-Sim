from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from src.core.asset_loaders import ASSETS
from .base_wrapper import BaseWrapper

if TYPE_CHECKING:
    from src.ui.elements import TextBox
    from src.custom_types import Pos

class ShadowWrapper(BaseWrapper):
    def __init__(self, target: TextBox, offset: tuple[int, int] = (2, 2), shadow_config: str = "shadow_default"):
        super().__init__(target)
        self.offset = offset
        self.shadow_config_data = ASSETS.text.get_config(shadow_config)
        self.cached_shadow_surf: pygame.Surface | None = None
        
        self._last_getter_text = self.target._text
        self._render_shadow(self.target._text)

    def _render_shadow(self, text: str) -> None:
        """Helper to render and cache the shadow surface."""
        if text.strip() and self.shadow_config_data:
            self.cached_shadow_surf = self.shadow_config_data.render(text)
        else:
            self.cached_shadow_surf = None
    
    def set_text(self, new_text: Any) -> None:
        """INTERCEPTOR: Catches manual text updates, updates the target, and rebuilds the shadow."""
        new_text_str = str(new_text)
        
        if new_text_str != self.target._text:
            self.target.set_text(new_text_str)
            # rebuild shadow 
            self._render_shadow(new_text_str)
            
            self._last_getter_text = new_text_str
    
    def update(self, mouse_pos: Pos | None = None) -> None:
        self.target.update(mouse_pos)

        if self.target.text_getter is None:
            return
        current_text = self.target._text
        if self._last_getter_text != current_text:
            self._last_getter_text = current_text
            self._render_shadow(current_text)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.target.is_visible:
            return

        if self.target.image:
            screen.blit(self.target.image, self.target.rect)

        if self.cached_shadow_surf and self.target.text_rect:
            shadow_rect = self.cached_shadow_surf.get_rect()
            shadow_rect.centerx = self.target.text_rect.centerx + self.offset[0]
            shadow_rect.centery = self.target.text_rect.centery + self.offset[1]
            screen.blit(self.cached_shadow_surf, shadow_rect)

        if self.target.text_surf and self.target.text_rect:
            screen.blit(self.target.text_surf, self.target.text_rect)
