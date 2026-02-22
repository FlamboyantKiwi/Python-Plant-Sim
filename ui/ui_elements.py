import pygame
from core.helper import align_rect
from core.asset_loader import AssetLoader
from core.types import TextConfig

# --- PARENT CLASS ---
class UIElement(pygame.sprite.Sprite):
    """ A smart Container that handles: 
        Rect: Position and Size
        Background: Image or Solid Colour
        Borders: Baked in"""
    def __init__(self, rect, image_file=None, colour=None, border_colour=None, border_width=2):
        super().__init__()
        self.rect = rect
        self.is_visible = True

        # Create Background
        if image_file: # Load and scale sprite
            self.image = AssetLoader.load_image(image_file, scale=rect.size).copy()
        elif colour: # Solid Colour
            self.image = pygame.Surface(rect.size)
            self.image.fill(AssetLoader.get_colour(colour))
        elif border_colour: # Transparent container
            self.image = pygame.Surface(rect.size, pygame.SRCALPHA)
        else: # Invisible / Container only
            self.image = None

        # Create Borders
        if self.image and border_colour:
            # Draw border inside the existing surface
            col = AssetLoader.get_colour(border_colour)
            pygame.draw.rect(self.image, col, self.image.get_rect(), border_width)

    def draw(self, screen):
        # Only draw if we have a valid surface
        if self.is_visible and self.image:
            screen.blit(self.image, self.rect)

    def update(self, mouse_pos=None):
        pass

    def is_click(self, mouse_pos):
        return False # not clickable by default

    def handle_click(self):
        return None

# --- TEXTBOX CLASS ---
class TextBox(UIElement):
    def __init__(self, rect, text:str=" ", text_getter=None, config:str = "default", align="center", 
                 bg_colour=None, border_colour=None):
        super().__init__(rect, colour=bg_colour, border_colour=border_colour)
        self.align = align
        self._text = str(text)
        self.text_getter = text_getter
        
        from Assets.asset_data import TEXT 
        self.config =TEXT.get(config, TEXT.get("default"))
        if self.config is None:
            print(f"Error with text config: {config}")
            self.config = TextConfig()

        # Initial Render
        self.text_surf = None
        self.text_rect = None
        self._render_text()

    def set_text(self, new_text):
        new_text = str(new_text) 
        if new_text != self._text:
            self._text = new_text
            self._render_text()

    def _render_text(self):
        """Generates the text surface."""
        if self.config is None: return

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

    def update(self, mouse_pos=None):
        """ If a getter exists, run it. If the result changed, re-render. """
        if self.text_getter:
            # Call the function to get the current value
            current_val = str(self.text_getter())
            
            # Only render if different
            if current_val != self._text:
                self.set_text(current_val)
    def draw(self, screen):
        if not self.is_visible: return

        # Draw BG/border
        super().draw(screen)

        #draw text on top
        if self.text_surf:
            screen.blit(self.text_surf, self.text_rect)

class StateElement(UIElement):
    """Automatically swaps between Normal, Hover, and Active visuals.
    Does NOT handle text or click functions (Button does that)."""
    def __init__(self, rect, base_visual: UIElement|None = None, 
                 hover_visual: UIElement|None = None, 
                 active_visual: UIElement|None = None):
        super().__init__(rect) # Init generic sprite
        
        self.is_hovered = False
        self.is_active = False

        # --- SETUP SURFACES ---
        # 1. Normal: Must exist. If None, create transparent.
        self.surf_normal = base_visual.image if base_visual else UIElement(rect).image

        # 2. Hover: If None, fallback to Normal
        self.surf_hover = hover_visual.image if hover_visual else self.surf_normal

        # 3. Active: If None, fallback to Hover (or Normal)
        self.surf_active = active_visual.image if active_visual else self.surf_hover

        # Start State
        self.image = self.surf_normal

    def update(self, mouse_pos=None):
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
    def __init__(self, rect:pygame.rect.Rect, text:str="", config:str = "default", function=None,
                base_visual=None, hover_visual=None, active_visual=None):
        # Pass visuals to the State Manager
        super().__init__(rect, base_visual, hover_visual, active_visual)

        self.function = function

        # Create  Child TextBox
        # Pass button rect as container, so text centers automatically.
        self.text_box = TextBox(rect=rect, text=text, config=config)

    def update(self, mouse_pos=None):
        # Run State Logic (Swap Images)
        super().update(mouse_pos)
        
        # Update Text
        self.text_box.update()

    def draw(self, screen):
        if not self.is_visible: return
         # Draw the current image state 
        super().draw(screen)
        # Draw text
        self.text_box.draw(screen) 

    def set_text(self, new_text):
        self.text_box.set_text(new_text)

    def is_click(self, mouse_pos):
        return self.is_visible and self.rect.collidepoint(mouse_pos)
    
    def handle_click(self):
        if self.function:   return self.function()
    @classmethod
    def create_bordered_button(cls, rect, text, function, bg_colour="dark_grey", 
            border_colour="light_grey", hover_colour="gold", active_colour="white", thickness=2):
        """Factory: Creates a button with a solid background and a changing border."""
        # 1. Base Visual (Dark BG + Grey Border)
        v_normal = UIElement(rect, colour=bg_colour, border_colour=border_colour, border_width=thickness)
        
        # Hover Visual (Same BG + Gold Border)
        v_hover = UIElement(rect, colour=bg_colour, border_colour=hover_colour, border_width=thickness)
        
        # Active Visual (Lighter BG + Gold Border)
        v_active = UIElement(rect, colour=active_colour, border_colour=hover_colour, border_width=thickness + 1)

        # Return the fully assembled Button
        return cls(rect, text=text, function=function, 
                   base_visual=v_normal, hover_visual=v_hover, active_visual=v_active)


class Slot(Button):
    def __init__(self, rect, index, slot_size):
        # 1. DEFINE VISUALS
        colour = "SLOT"
        hover_colour = "HOVER_COLOUR"
        active_colour = "ACTIVE_COLOUR"

        v_normal = UIElement(rect, colour=colour)
        v_hover  = UIElement(rect, colour=colour, border_colour=hover_colour)
        v_active = UIElement(rect, colour=colour, border_colour=active_colour, border_width=3)

        # INIT BUTTON (Which Inits StatefulElement)
        super().__init__(rect, base_visual=v_normal, hover_visual=v_hover, active_visual=v_active)

        self.index = index
        self.item = None 
        
        # COMPONENT: Stack Count
        self.info_text = TextBox(
            rect=self.rect.inflate(-4, -4), 
            text="", config="SLOT", align="bottomright"
        )
        self.info_text.is_visible = False

    def set_item(self, item):
        """Updates the slot's data."""
        self.item = item

        if self.item and self.item.stack_size > 1:
            self.info_text.set_text(self.item.count)
        else:
            self.info_text.set_text("") # Auto-hide

    def draw(self, screen):
        # Draw Background (State managed by parent)
        super().draw(screen)

        # Draw Item Content
        if self.item:
            # Center the item image
            # We assume self.item.image is already a Surface
            item_rect = self.item.image.get_rect(center=self.rect.center)
            screen.blit(self.item.image, item_rect)

            self.info_text.draw(screen)
    def set_price(self, price: int):
        """Shop Mode: Overrides the text to show price."""
        self.info_text.set_text(f"${price}")
