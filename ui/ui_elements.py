from __future__ import annotations
from typing import TYPE_CHECKING

import pygame
from core.ui_utils import align_rect

if TYPE_CHECKING:
    from typing import Callable, Any
    from custom_types import Pos, Item, UIElement


# --- PARENT CLASS ---
class UIElement(pygame.sprite.Sprite):
    """ Base class for all UI components. Represents a physical space and an optional static visual. """
    def __init__(self, rect: pygame.Rect, surface: pygame.Surface | None = None) -> None:
        super().__init__()
        self.rect = rect
        self.is_visible = True
        self.image = surface
        
    def draw(self,screen: pygame.Surface) -> None:
        # Only draw if we have a valid surface
        if self.is_visible and self.image:
            screen.blit(self.image, self.rect)

    def update(self, mouse_pos: Pos | None = None) -> None:
        pass

    def is_click(self, mouse_pos: Pos) -> bool:
        return False 

    def handle_click(self) -> Any:
        return None
    
# --- TEXTBOX CLASS ---
class TextBox(UIElement):
    def __init__(self, rect: pygame.Rect, text: str = " ", 
                 text_getter: Callable[[], Any] | None = None, 
                 config: str = "default", align: str = "center",
                 surface: pygame.Surface | None = None) -> None:
        
        super().__init__(rect, surface)
        self.align = align
        self._text = str(text)
        self.text_getter = text_getter
        
        from core.assets import ASSETS
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

class StateElement(UIElement):
    """Base class for anything that reacts to hovers or clicks."""
    def __init__(self, rect: pygame.Rect, base_visual: UIElement | None = None) -> None:
        super().__init__(rect) 
        self.is_hovered = False
        self.is_active = False
        self.image = base_visual.image if base_visual else UIElement(rect).image

    def update(self, mouse_pos: Pos | None = None) -> None:
        if mouse_pos:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
            
class Button(StateElement):
    def __init__(self, rect: pygame.Rect, 
                 function: Callable | None = None,
                 base_visual: UIElement | None = None, 
                 content: UIElement | None = None) -> None:
        super().__init__(rect, base_visual)
        self.function = function
        self.content = content 

    def update(self, mouse_pos: Pos | None = None) -> None:
        super().update(mouse_pos)
        if self.content:
            self.content.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_visible: 
            return
        super().draw(screen)
        if self.content:
            self.content.draw(screen)

    def is_click(self, mouse_pos: Pos) -> bool:
        return self.is_visible and self.rect.collidepoint(mouse_pos)
    
    def handle_click(self) -> Any:
        if self.function:   
            return self.function()
        
    def __getattr__(self, attr: str) -> Any:
        if self.content is None:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attr}'")
        return getattr(self.content, attr)
        
class Slot(Button):
    def __init__(self, rect: pygame.Rect, index: int, base_visual: UIElement) -> None:
        super().__init__(rect, base_visual=base_visual)
        
        self.index = index
        self.item: Item | None = None 
        self.last_count = 0
        self.price: int | None = None
        
        # COMPONENT: Stack Count
        self.info_text = TextBox(
            rect=self.rect.inflate(-4, -4), 
            text="", config="SLOT", align="bottomright"
        )
        self.info_text.is_visible = False

    def set_item(self, item: Item | None) -> None:
        """Updates the slot's data."""
        current_count = item.count if item else 0
        
        # Check if it's a completely new item, OR if the existing item's count changed
        if self.item != item or self.last_count != current_count:
            self.item = item
            self.last_count = current_count
            self._update_text()
            
    def set_price(self, price: int) -> None:
        """Sets the slot to Shop Mode and remembers the price."""
        self.price = price
        self._update_text()
        
    def _update_text(self) -> None:
        """Internal helper to figure out what text to display."""
        if self.item is None:
            self.info_text.set_text("")
            self.info_text.is_visible = False
            return

        # PRIORITY 1: Shop Price
        if self.price is not None:
            self.info_text.set_text(f"£{self.price}")
            self.info_text.is_visible = True
            
        # PRIORITY 2: Stack Count
        elif self.item.max_stack > 1:
            self.info_text.set_text(self.item.count)
            self.info_text.is_visible = True
            
        # PRIORITY 3: Nothing (Unstackable item in a normal inventory)
        else:
            self.info_text.set_text("") 
            self.info_text.is_visible = False
    
    def update(self, mouse_pos: Pos | None = None) -> None:
        """Update states and the child text box."""
        super().update(mouse_pos)
        self.info_text.update()
       
    def draw(self, screen: pygame.Surface) -> None:
        # Draw Background (Managed by parent: Button)
        super().draw(screen)

        # Draw Item Content
        if self.item:
            # Center the item image
            item_rect = self.item.image.get_rect(center=self.rect.center)
            screen.blit(self.item.image, item_rect)
            #draw text on top of item 
            self.info_text.draw(screen)
   
 