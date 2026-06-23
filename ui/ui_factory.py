from __future__ import annotations
import pygame
from core.assets import ASSETS
from ui.ui_elements import UIElement, TextBox, Button, Slot
from ui.wrappers import BorderWrapper, ImageSwapWrapper, ShadowWrapper, FlashWrapper
from core.ui_utils import get_grid_pos 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, Any

class UIFactory:
    """A collection of static methods to build and arrange UI assemblies."""
    
    # ----- Internal Helper -----
    @staticmethod
    def _create_solid_surf(size: tuple[int, int], colour_name: str) -> pygame.Surface:
        """Internal helper to generate a solid colored surface."""
        surf = pygame.Surface(size)
        surf.fill(ASSETS.colour(colour_name))
        return surf
    
    # ----- UIElement Varieties -----
    @staticmethod
    def solid_element(rect: pygame.Rect, colour: str) -> UIElement:
        """Creates a UIElement with a solid colored background."""
        return UIElement(rect, surface=UIFactory._create_solid_surf(rect.size, colour))
    
    @staticmethod
    def image_element(rect: pygame.Rect, image_file: str) -> UIElement:
        """Creates a UIElement from a loaded sprite."""
        surf = ASSETS.load_image(image_file, scale=rect.size).copy()
        return UIElement(rect, surface=surf)

    @staticmethod
    def static_border_element(rect: pygame.Rect, colour: str, border_colour: str, thickness: int = 2) -> UIElement:
        """Creates a UIElement with a baked-in, non-changing border."""
        surf = pygame.Surface(rect.size)
        surf.fill(ASSETS.colour(colour))
        pygame.draw.rect(surf, ASSETS.colour(border_colour), surf.get_rect(), thickness)
        return UIElement(rect, surface=surf)
    
    # ----- Text Varieties -----
    @staticmethod
    def bubble_text(rect: pygame.Rect, text: str, 
                       config: str = "default", shadow_config: str = "shadow_default",
                       shadow_offset: tuple[int, int] = (2, 2), align: str = "center",
                       bg_surface: pygame.Surface | None = None) -> ShadowWrapper:
        """Creates a TextBox with a drop shadow."""
        base_text = TextBox(rect=rect, text=text, config=config, align=align, surface=bg_surface)
        return ShadowWrapper(target=base_text, offset=shadow_offset, shadow_config=shadow_config)

    @staticmethod
    def flashing_text(rect: pygame.Rect, text: str, interval: float = 0.5,
                         config: str = "default", align: str = "center",
                         auto_start: bool = True) -> FlashWrapper:
        """Creates a TextBox that blinks on and off."""
        base_text = TextBox(rect=rect, text=text, config=config, align=align)
        flashing_text = FlashWrapper(target=base_text, interval=interval)
        if auto_start:
            flashing_text.start_flash()
        return flashing_text
    
    # ----- Button Varieties -----
    @staticmethod
    def bordered_text_button(rect: pygame.Rect, text: str, function: Callable, 
                             config: str = "default",
                             bg_colour: str = "ButtonBG", border_colour: str = "ButtonBorder", 
                             hover_colour: str = "ButtonHover", active_colour: str = "ButtonActive", 
                             thickness: int = 2) -> BorderWrapper:
        """Creates a button with a solid background and a dynamic hover/active border."""
        # Build the base components
        v_normal = UIFactory.solid_element(rect, bg_colour)
        text_element = TextBox(rect=rect, text=text, config=config, align="center")
        
        # Assemble the Button
        base_button = Button(rect, function=function, base_visual=v_normal, content=text_element)
        
        # Add wrapper
        return BorderWrapper(
            target=base_button, 
            normal_colour=border_colour, 
            hover_colour=hover_colour, 
            active_colour=active_colour, 
            thickness=thickness
        )

    @staticmethod
    def bubble_text_button(rect: pygame.Rect, text: str, function: 'Callable', 
                           config: str = "default", shadow_config: str = "shadow_default",
                           shadow_offset: tuple[int, int] = (2, 2),
                           bg_colour: str = "ButtonBG", border_colour: str = "ButtonBorder", 
                           hover_colour: str = "ButtonHover", active_colour: str = "ButtonActive", 
                           thickness: int = 2) -> BorderWrapper:
        """Creates a bordered button containing shadowed text."""
        v_normal = UIFactory.solid_element(rect, bg_colour)
        
        # Generate the text and wrap it in a shadow
        shadow_text = UIFactory.bubble_text(
            rect=rect, text=text, config=config, 
            shadow_config=shadow_config, shadow_offset=shadow_offset
        )
        
        # Pass the wrapped text as the button's content
        base_button = Button(rect, function=function, base_visual=v_normal, content=shadow_text)
        
        # Wrap the whole button in dynamic borders
        return BorderWrapper(
            target=base_button, normal_colour=border_colour, 
            hover_colour=hover_colour, active_colour=active_colour, thickness=thickness
        )

    @staticmethod
    def color_swap_text_button(rect: pygame.Rect, text: str, function: Callable, 
                               config: str = "default",
                               bg_normal: str = "ButtonNormal", 
                               bg_hover: str = "ButtonHover", 
                               bg_active: str = "ButtonActive") -> ImageSwapWrapper:
        """Creates a button that entirely replaces its background color on hover/click."""
        # Create the solid color surfaces
        surf_normal = UIFactory._create_solid_surf(rect.size, bg_normal)
        surf_hover = UIFactory._create_solid_surf(rect.size, bg_hover)
        surf_active = UIFactory._create_solid_surf(rect.size, bg_active)

        # Build the base button
        text_element = TextBox(rect=rect, text=text, config=config, align="center")
        base_button = Button(rect, function=function, base_visual=UIElement(rect), content=text_element)
        # Add wrapper
        return ImageSwapWrapper(
            target=base_button, 
            surf_normal=surf_normal, 
            surf_hover=surf_hover, 
            surf_active=surf_active
        )
     
    # ----- Slot Varieties -----
    @staticmethod
    def bordered_slot(rect: pygame.Rect, index: int) -> BorderWrapper:
        """Builder for an inventory slot with dynamic borders."""
        
        # Build the base color element using factory helper
        v_normal = UIFactory.solid_element(rect, "SLOT")
        # Create slot
        base_slot = Slot(rect, index=index, base_visual=v_normal)
        
        # Wrap it with borders
        return BorderWrapper(
            target=base_slot, normal_colour="SLOT_BORDER", 
            hover_colour="HOVER_COLOUR", active_colour="ACTIVE_COLOUR",
            thickness=2
        )
    
    # ----- Layout Factories -----
    @staticmethod
    def create_grid(factory: Callable, start_pos: tuple[int, int], columns: int, 
                    item_size: tuple[int, int], gap: tuple[int, int],
                    data: int | list[dict[str, Any]], **shared_kwargs) -> list[Any]:
        """Universal grid generator for any UI Element."""
        elements = []
        items_kwargs = [{"index": i} for i in range(data)] if isinstance(data, int) else data
            
        for i, item_kwargs in enumerate(items_kwargs):
            x, y = get_grid_pos(index=i, cols=columns, start=start_pos, size=item_size, gap=gap)
            rect = pygame.Rect(x, y, item_size[0], item_size[1])
            
            merged_kwargs = {"rect": rect, **shared_kwargs, **item_kwargs}
            elements.append(factory(**merged_kwargs))
            
        return elements

    @staticmethod
    def create_vertical_stack(factory: Callable, center_pos: tuple[int, int],
                              item_size: tuple[int, int], gap: int,
                              data: list[dict[str, Any]], **shared_kwargs) -> list[Any]:
        """Convenience method for a 1-column grid centered vertically."""
        total_items = len(data)
        if total_items == 0:
            return []
            
        # Calculate total height: (height of all items) + (height of all gaps)
        total_height = (total_items * item_size[1]) + ((total_items - 1) * gap)
        
        # Determine the true top-left starting position to keep it perfectly centered
        start_x = center_pos[0] - (item_size[0] // 2)
        start_y = center_pos[1] - (total_height // 2)
        
        return UIFactory.create_grid(
            factory=factory,
            start_pos=(start_x, start_y),
            columns=1,
            item_size=item_size,
            gap=(0, gap),
            data=data,
            **shared_kwargs
        )   
        
        