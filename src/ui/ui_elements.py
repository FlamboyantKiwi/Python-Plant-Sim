from __future__ import annotations
from typing import TYPE_CHECKING

import pygame
from src.core import align_rect

if TYPE_CHECKING:
    from typing import Callable, Any
    from src.custom_types import Pos, Item, UIElement


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

    def copy_image(self) -> pygame.Surface:
        """ Safely returns a copy of the element's surface. 
        Satisfies type checkers and prevents runtime crashes if the image is missing."""
        if self.image is not None:
            return self.image.copy()
        
        # Fallback: Return a blank, transparent surface matching the rect's dimensions
        return pygame.Surface(self.rect.size, pygame.SRCALPHA)
    
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

class StateElement(UIElement):
    """Base class for anything that reacts to hovers or clicks."""
    def __init__(self, rect: pygame.Rect, base_visual: UIElement | None = None) -> None:
        super().__init__(rect) 
        self.is_hovered = False
        self.is_active = False
        self.image = base_visual.copy_image() if base_visual else pygame.Surface(rect.size, pygame.SRCALPHA)
        
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
   
class ProgressBar(UIElement):
    """A reusable progress controller that scales and aligns injected UIElements."""
    def __init__(self, rect: pygame.Rect, 
                 bg_element: UIElement,
                 fill_element: UIElement,
                 percentage: float = 1.0, 
                 value_getter: Callable[[], float] | None = None,
                 alignment: str = "left", is_horizontal: bool|None = None) -> None:
        super().__init__(rect)
        self.bg_element = bg_element
        self.fill_element = fill_element
        self.alignment = alignment.lower()
        
        self.percentage = max(0.0, min(1.0, percentage))
        self.value_getter = value_getter

        # Cache the original surface so we can scale it dynamically without distortion
        self._fill_surface_base = self.fill_element.copy_image()

        # Deduce scaling axis based on proportions, unless explicitly overridden
        self.is_horizontal = is_horizontal if is_horizontal is not None else (self.rect.width >= self.rect.height)
        # Track the dynamic size (width or height depending on alignment) to prevent redundant scaling
        self._cached_size: int = -1
        self._update_fill_rect()

    def _update_fill_rect(self) -> None:
        """Recalculates dimensions, scales the surface, and anchors it based on alignment."""
        ratio = max(0.0, min(1.0, self.percentage))
        
        # Determine dimensions based on axis (deduced or overriden)
        if self.is_horizontal:
            new_w = int(self.rect.width * ratio)
            new_h = self.rect.height
            dynamic_size = new_w
        else:
            new_w = self.rect.width
            new_h = int(self.rect.height * ratio)
            dynamic_size = new_h

        # Only mutate the surface and rect if the pixel size actually changed
        if dynamic_size != self._cached_size:
            self._cached_size = dynamic_size
            
            if dynamic_size > 0:
                # Scale the original surface to the new dimensions
                self.fill_element.image = pygame.transform.scale(
                    self._fill_surface_base, 
                    (new_w, new_h)
                )
                self.fill_element.rect.size = (new_w, new_h)
                
                # Dynamic Anchoring: grabs the point from the background rect and applies it to the fill rect
                try:
                    anchor_point = getattr(self.rect, self.alignment)
                    setattr(self.fill_element.rect, self.alignment, anchor_point)
                except AttributeError:
                    # Fallback if an invalid Pygame anchor string was provided
                    self.fill_element.rect.topleft = self.rect.topleft

    def update(self, mouse_pos: Pos | None = None) -> None:
        """Polls the value getter and updates the fill block only when data changes."""
        if self.value_getter:
            val = max(0.0, min(1.0, self.value_getter()))
            if val != self.percentage:
                self.percentage = val
                self._update_fill_rect()

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_visible:
            return
            
        self.bg_element.draw(screen)
        
        # Only draw the fill if its dynamic dimension is greater than 0
        if self._cached_size > 0:
            self.fill_element.draw(screen)