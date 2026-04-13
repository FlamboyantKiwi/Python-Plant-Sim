from __future__ import annotations
from typing import TYPE_CHECKING, Callable

import pygame
from core.ui_utils import align_rect, get_grid_pos 
from core.assets import ASSETS
from core.types import TextConfig


if TYPE_CHECKING:
    from custom_types import Pos, Item, Any

# --- PARENT CLASS ---
class UIElement(pygame.sprite.Sprite):
    """ A smart Container that handles: 
        Rect: Position and Size
        Background: Image or Solid Colour
        Borders: Baked in"""
    def __init__(self, rect: pygame.Rect, image_file: str | None = None, 
                 colour: str | None = None, border_colour: str | None = None, 
                 border_width: int = 2) -> None:
        super().__init__()
        self.rect = rect
        self.is_visible = True
        self.image: pygame.Surface | None = None

        # Create Background
        if image_file: # Load and scale sprite
            self.image = ASSETS.load_image(image_file, scale=rect.size).copy()
        elif colour: # Solid Colour
            self.image = pygame.Surface(rect.size)
            self.image.fill(ASSETS.colour(colour))
        elif border_colour: # Transparent container
            self.image = pygame.Surface(rect.size, pygame.SRCALPHA)

        # Create Borders
        if self.image and border_colour:
            # Draw border inside the existing surface
            col = ASSETS.colour(border_colour)
            pygame.draw.rect(self.image, col, self.image.get_rect(), border_width)

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
                 bg_colour: str | None = None, border_colour: str | None = None) -> None:
        super().__init__(rect, colour=bg_colour, border_colour=border_colour)
        self.align = align
        self._text = str(text)
        self.text_getter = text_getter
        
        from core.assets.asset_data import TEXT 
        self.config =TEXT.get(config, TEXT.get("default"))
        if self.config is None:
            print(f"Error with text config: {config}")
            self.config = TextConfig()

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
        self.is_visible=True # show if previously hidden
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
    """Automatically swaps between Normal, Hover, and Active visuals.
    Does NOT handle text or click functions (Button does that)."""
    def __init__(self, rect: pygame.Rect, 
                 base_visual: UIElement|None = None, 
                 hover_visual: UIElement|None = None, 
                 active_visual: UIElement|None = None) -> None:
        super().__init__(rect) # Init generic sprite
        
        self.is_hovered = False
        self.is_active = False

        # --- SETUP SURFACES ---
        # Normal: Must exist. If None, create transparent.
        self.surf_normal = base_visual.image if base_visual else UIElement(rect).image

        # Hover: If None, fallback to Normal
        self.surf_hover = hover_visual.image if hover_visual else self.surf_normal

        # Active: If None, fallback to Hover (or Normal)
        self.surf_active = active_visual.image if active_visual else self.surf_hover

        # Start State
        self.image = self.surf_normal

    def update(self, mouse_pos: Pos | None = None) -> None:
        """Standard State Switching Logic"""
        if mouse_pos:
            self.is_hovered = self.rect.collidepoint(mouse_pos)

        # PRIORITY: Active > Hover > Normal
        if self.is_active and self.surf_active:
            self.image = self.surf_active
        elif self.is_hovered and self.surf_hover:
            self.image = self.surf_hover
        else:
            self.image = self.surf_normal

class Button(StateElement):
    def __init__(self, rect: pygame.Rect, text: str = "", config: str = "default", 
                 function: Callable | None = None,
                 base_visual: UIElement | None = None, 
                 hover_visual: UIElement | None = None, 
                 active_visual: UIElement | None = None) -> None:
        # Pass visuals to the State Manager
        super().__init__(rect, base_visual, hover_visual, active_visual)

        self.function = function

        # Create  Child TextBox
        # Pass button rect as container, so text centers automatically.
        self.text_box = TextBox(rect=rect, text=text, config=config)

    def update(self, mouse_pos: Pos | None = None) -> None:
        # Run State Logic (Swap Images)
        super().update(mouse_pos)
        
        # Update Text
        self.text_box.update()

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_visible: 
            return
         # Draw the current image state 
        super().draw(screen)
        # Draw text
        self.text_box.draw(screen) 

    def set_text(self, new_text: str) -> None:
        self.text_box.set_text(new_text)

    def is_click(self, mouse_pos: Pos) -> bool:
        return self.is_visible and self.rect.collidepoint(mouse_pos)
    
    def handle_click(self) -> Any:
        if self.function:   
            return self.function()
    @classmethod
    def create_bordered_button(cls, rect: pygame.Rect, text: str, function: Callable, 
                               bg_colour: str = "ButtonBG", border_colour: str = "ButtonBorder", 
                               hover_colour: str = "ButtonHover", active_colour: str = "ButtonActive", 
                               thickness: int = 2) -> Button:
        """Factory: Creates a button with a solid background and a changing border."""
        v_normal = UIElement(rect, colour=bg_colour, border_colour=border_colour, border_width=thickness)
        v_hover = UIElement(rect, colour=bg_colour, border_colour=hover_colour, border_width=thickness)
        v_active = UIElement(rect, colour=active_colour, border_colour=hover_colour, border_width=thickness + 1)

        # Return the fully assembled Button
        return cls(rect, text=text, function=function, 
                   base_visual=v_normal, hover_visual=v_hover, active_visual=v_active)

    @classmethod
    def create_vertical_stack(cls, 
                               center_pos: tuple[int, int], 
                               data: dict[str, Callable] | list[tuple[str, Callable]],
                               gap: int = 60,
                               width: int = 200, 
                               height: int = 50,
                               **style_kwargs) -> list[Button]:
        """ Creates a vertical list of buttons centered at center_pos.
        Style_kwargs can include bg_colour, border_colour, hover_colour, active_colour, thickness, etc."""
        buttons = []
        start_x, start_y = center_pos
        
        # Convert dict to list of tuples if necessary
        items = data.items() if isinstance(data, dict) else data

        for i, (text, func) in enumerate(items):
            rect = pygame.Rect(0, 0, width, height)
            # Offset each button by the gap
            rect.center = (start_x, start_y + (i * gap))
            
            # Create the button using our existing bordered factory
            btn = cls.create_bordered_button(rect=rect, text=text, function=func, **style_kwargs)
            buttons.append(btn)
            
        return buttons


class Slot(Button):
    def __init__(self, rect: pygame.Rect, index: int, slot_size: int) -> None:
        v_normal = UIElement(rect, colour="SLOT")
        v_hover  = UIElement(rect, colour="SLOT", border_colour="HOVER_COLOUR")
        v_active = UIElement(rect, colour="SLOT", border_colour="ACTIVE_COLOUR", border_width=3)
        
        super().__init__(rect, base_visual=v_normal, hover_visual=v_hover, active_visual=v_active)

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

    def draw(self, screen: pygame.Surface) -> None:
        # Draw Background (State managed by parent)
        super().draw(screen)

        # Draw Item Content
        if self.item:
            # Center the item image
            # We assume self.item.image is already a Surface
            item_rect = self.item.image.get_rect(center=self.rect.center)
            screen.blit(self.item.image, item_rect)

            self.info_text.draw(screen)
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
            self.info_text.set_text(f"${self.price}")
            self.info_text.is_visible = True
            
        # PRIORITY 2: Stack Count
        elif self.item.max_stack > 1:
            self.info_text.set_text(self.item.count)
            self.info_text.is_visible = True
            
        # PRIORITY 3: Nothing (Unstackable item in a normal inventory)
        else:
            self.info_text.set_text("") 
            self.info_text.is_visible = False
        
    @classmethod
    def create_grid(cls, max_size: int, columns: int, start_pos: Pos, slot_size: int, padding: int) -> list[Slot]:
        """Factory method: Generates a list of Slot objects arranged in a grid."""
        slots: list[Slot] = []
        for i in range(max_size):
            x, y = get_grid_pos(
                index=i, 
                cols=columns, 
                start=start_pos, 
                size=(slot_size, slot_size), 
                gap=(padding, padding)
            )
            
            slot_rect = pygame.Rect(x, y, slot_size, slot_size)
            # Create a new instance of the class (Slot) and append it
            slots.append(cls(slot_rect, i, slot_size))
            
        return slots