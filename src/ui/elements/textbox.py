from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from src.core import align_rect
from .base_element import UIElement

if TYPE_CHECKING:
    from typing import Callable, Any
    from src.custom_types import Pos

class TextBox(UIElement):
    def __init__(self, rect: pygame.Rect, text: str = " ", 
                 text_getter: Callable[[], Any] | None = None, 
                 config: str = "default", align: str = "center",
                 surface: pygame.Surface | None = None) -> None:
        
        super().__init__(rect, surface)
        self.align = align
        self._text = str(text)
        self.text_getter = text_getter
        
        from src.core.assets import ASSETS
        self.config = ASSETS.text.get_config(config)

        # Initial Render
        self.text_surf: pygame.Surface | None = None
        self.text_rect: pygame.Rect | None = None
        self._render_text()

    def set_text(self, new_text:Any) -> None:
        new_text = str(new_text) 
        if new_text != self._text:
            self._text = new_text
            self._render_text()

    def _render_text(self) -> None:
        """Generates the text surface."""
        if self.config is None: 
            return

        # No text to render
        if not self._text.strip():
            self.text_surf = None
            if self.image is None: # No background or text: Don't render at all
                self.is_visible = False
            # No text, but is a background: keep visible
            return 
        
        # Text exists
        self.is_visible = True # show if previously hidden
        self.text_surf = self.config.render(self._text)
        self.text_rect = self.text_surf.get_rect() 
        
        # Dynamic Alignment: Matches the specific anchor (e.g. "center", "topleft")
        # of the text rect to the same anchor on the target container.
        try:
            anchor_point = getattr(self.rect, self.align)
        except AttributeError:
            anchor_point = self.rect.center
        align_rect(self.text_rect, *anchor_point, align=self.align)

    def update(self, mouse_pos: Pos | None = None) -> None:
        """ If a getter exists, run it. If the result changed, re-render. """
        if self.text_getter:
            # Call the function to get the current value
            current_val = str(self.text_getter())
            
            # Only render if different
            if current_val != self._text:
                self.set_text(current_val)
    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_visible: 
            return

        # Draw BG/border
        super().draw(screen)

        #draw text on top
        if self.text_surf and self.text_rect:
            screen.blit(self.text_surf, self.text_rect)
