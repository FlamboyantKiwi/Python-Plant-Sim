from __future__ import annotations
from ui.timer import Timer
from typing import TYPE_CHECKING
import pygame
from core.assets import ASSETS

if TYPE_CHECKING:
    from typing import Any
    from ui.ui_elements import StateElement, TextBox
    from custom_types import Pos, UIElement
    
class BaseWrapper:
    """Base class for all UI wrappers. Automatically delegates missing attributes to the target."""
    def __init__(self, target: UIElement):
        self.target:Any = target

    def __getattr__(self, attr: str) -> Any:
        # Safety check to prevent infinite recursion if target isn't set yet
        if attr == "target":
            raise AttributeError(f"'{type(self).__name__}' has no target initialized.")
        return getattr(self.target, attr)

    def __setattr__(self, attr: str, value: Any) -> None:
        """Intelligently routes variable assignments to either the Wrapper or the Target."""
        # Allow the wrapper to set its own variables (like 'target', 'interval', 'surf_normal')
        if attr == "target" or attr in self.__dict__:
            super().__setattr__(attr, value)
        # If the target owns the attribute (like 'is_active' or 'is_hovered'), forward it down!
        elif hasattr(self, "target") and hasattr(self.target, attr):
            setattr(self.target, attr, value)
        # Fallback
        else:
            super().__setattr__(attr, value)
    
    def update(self, *args, **kwargs) -> None:
        """Default pass-through for the update loop."""
        self.target.update(*args, **kwargs)

    def draw(self, screen: pygame.Surface) -> None:
        """Default pass-through for the draw loop."""
        self.target.draw(screen)
    
class FlashWrapper(BaseWrapper):
    """ Wraps any object that has an update() and draw() method 
    to provide flashing/blinking functionality without altering the original class."""
    def __init__(self, target: Any, interval: float = 0.25):
        super().__init__(target)
        self.interval = interval
        
        self.flash_timer = Timer(interval)
        self.is_flashing = False
        self.is_blank = False # True means the object is currently "invisible" in the blink

    def start_flash(self) -> None:
        """Begins the flashing effect."""
        self.is_flashing = True
        self.is_blank = False
        self.flash_timer.start()

    def stop_flash(self) -> None:
        """Stops the flashing and ensures the object is visible."""
        self.is_flashing = False
        self.is_blank = False

    def update(self, *args, **kwargs) -> None:
        """Updates the underlying target and handles blink timing."""
        # Always update the target object first (passing along any arguments like mouse_pos)
        self.target.update(*args, **kwargs)

        # Handle the flash timer logic
        if self.is_flashing:
            # If the timer hits 0 (update returns False)
            if not self.flash_timer.update():
                self.is_blank = not self.is_blank  # Toggle visibility
                self.flash_timer.start()        # Reset the timer for the next blink

    def draw(self, screen: Any) -> None:
        """Draws the underlying target only if it isn't in a blank flash frame."""
        if not self.is_blank:
            self.target.draw(screen)
    
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
    
class ImageSwapWrapper(BaseWrapper):
    """Dynamically swaps the underlying image of a StateElement based on state."""
    def __init__(self, target: StateElement, 
                 surf_normal: pygame.Surface, 
                 surf_hover: pygame.Surface | None = None, 
                 surf_active: pygame.Surface | None = None):
        super().__init__(target)
        self.surf_normal = surf_normal
        # Fallbacks
        self.surf_hover = surf_hover if surf_hover else surf_normal
        self.surf_active = surf_active if surf_active else self.surf_hover

    def update(self, mouse_pos: Pos | None = None) -> None:
        # Update the target so it calculates its state
        self.target.update(mouse_pos)

        # Swap the target's image surface based on new state
        if self.target.is_active:
            self.target.image = self.surf_active
        elif self.target.is_hovered:
            self.target.image = self.surf_hover
        else:
            self.target.image = self.surf_normal
 
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

    
class Tooltip(BaseWrapper):
    """Wraps an InventoryUI to display a tooltip that follows the mouse for hovered items."""
    def __init__(self, target: Any, tooltip_box: 'TextBox', offset: tuple[int, int] = (15, 15)) -> None:
        super().__init__(target)
        self.tooltip = tooltip_box
        self.offset = offset  # Distance from the cursor to draw the tooltip

    def update(self, mouse_pos: Pos | None = None) -> None:
        # Update the underlying inventory UI (syncs slots and handles their hover states)
        self.target.update(mouse_pos)

        # Check for hovered items
        hovered_item_name = ""
        if mouse_pos:
            for slot in self.target.slots:
                if slot.is_hovered and slot.item:
                    hovered_item_name = slot.item.name
                    break  # Found the hovered item, no need to keep checking

        # Update the tooltip text and state
        self.tooltip.set_text(hovered_item_name)
        self.tooltip.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        # Draw the main inventory grid first
        self.target.draw(screen)
        
        # Draw the tooltip on top
        self.tooltip.draw(screen)