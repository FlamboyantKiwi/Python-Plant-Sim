from __future__ import annotations
import pygame
from core.assets import ASSETS
from ui.ui_elements import ProgressBar, UIElement, TextBox, Button, Slot
from ui.wrappers import BorderWrapper, ImageSwapWrapper, ShadowWrapper, FlashWrapper, Tooltip
from core.ui_utils import get_grid_pos 
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from typing import Callable, Any
    from custom_types import Inventory
    from ui.InventoryUI import InventoryUI
    from ui.ui_ghosts import BorderButton, BorderSlot, BorderTextBox, FlashButton, FlashSlot, FlashTextBox, ShadowButton, ShadowSlot, ShadowTextBox  # noqa: F401

class UIFactory:
    """A collection of static methods to build and arrange UI assemblies."""
    
    # ----- Internal Helper -----
    @staticmethod
    def _create_solid_surf(size: tuple[int, int], colour_name: str) -> pygame.Surface:
        """Internal helper to generate a solid colored surface."""
        surf = pygame.Surface(size)
        surf.fill(ASSETS.colour(colour_name))
        return surf
    
    # ----- Raw Base Varieties -----
    @staticmethod
    def button(rect: pygame.Rect, text: str, function: Callable, config: str = "default") -> Button:
        """Creates a completely standard, unwrapped interactive button."""
        text_element = TextBox(rect=rect, text=text, config=config, align="center")
        return Button(rect, function=function, content=text_element)

    @staticmethod
    def text(rect: pygame.Rect, text: str = "", text_getter: Callable[[], str] | None = None, 
                  config: str = "default", align: str = "center") -> TextBox:
        """Creates a standard unwrapped text block that can track static or dynamic text values."""
        return TextBox(rect=rect, text=text, text_getter=text_getter, config=config, align=align)
    
    @staticmethod
    def slot(rect: pygame.Rect, index: int, bg_colour: str ="SlotBG", image_file: str | None = None) -> Slot:
        """ Creates a raw inventory slot. 
        Pass 'image_file' for a textured sprite, or 'bg_colour' for a solid background."""
        # If an image file is provided, use the sprite asset
        if image_file is not None:
            v_base = UIFactory.image_element(rect, image_file)
            
        # Otherwise, fall back to a solid color (using your default if none specified)
        else:
            v_base = UIFactory.solid_element(rect, bg_colour)
            
        # Hand the visual base right to the Slot constructor
        return Slot(rect, index=index, base_visual=v_base)
    
    @staticmethod
    def inventory_ui(rect: pygame.Rect, inventory_data: Inventory, 
                     columns: int = 4, slot_size: int = 40, padding: int = 5) -> InventoryUI:
        """Assembles a composite grid layer panel connected directly to a backend Inventory structure."""
        from ui.InventoryUI import InventoryUI
        return InventoryUI(
            rect=rect, 
            inventory_data=inventory_data, 
            columns=columns, 
            slot_size=slot_size, 
            padding=padding
        )
    
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
    def bubble_text(rect: pygame.Rect, text: str = "", text_getter: Callable[[], str] | None = None,
                    config: str = "default", shadow_config: str = "shadow_default",
                    shadow_offset: tuple[int, int] = (2, 2), align: str = "center",
                    bg_surface: pygame.Surface | None = None) -> ShadowTextBox:
        """Creates a shadowed TextBox that handles static strings or real-time lambdas."""
        base_text = TextBox(rect=rect, text=text, text_getter=text_getter, config=config, align=align, surface=bg_surface)
        return cast("ShadowTextBox", ShadowWrapper(target=base_text, offset=shadow_offset, shadow_config=shadow_config))
    
    @staticmethod
    def flashing_text(rect: pygame.Rect, text: str = "", text_getter: Callable[[], str] | None = None,
                      interval: float = 0.5, config: str = "default", align: str = "center",
                      auto_start: bool = True) -> FlashTextBox:
        """Creates a TextBox that blinks on and off."""
        base_text = TextBox(rect=rect, text=text, text_getter=text_getter, config=config, align=align)
        flashing_text = FlashWrapper(target=base_text, interval=interval)
        if auto_start:
            flashing_text.start_flash()
        return cast("FlashTextBox", flashing_text)
    
    # ----- Button Varieties -----
    @staticmethod
    def bordered_text_button(rect: pygame.Rect, text: str, function: Callable, 
                             config: str = "default",
                             bg_colour: str = "ButtonBG", border_colour: str = "ButtonBorder", 
                             hover_colour: str = "ButtonHover", active_colour: str = "ButtonActive", 
                             thickness: int = 2) -> BorderButton:
        """Creates a button with a solid background and a dynamic hover/active border."""
        v_normal = UIFactory.solid_element(rect, bg_colour)
        text_element = TextBox(rect=rect, text=text, config=config, align="center")
        
        base_button = Button(rect, function=function, base_visual=v_normal, content=text_element)
        
        return cast("BorderButton", BorderWrapper(target=base_button, normal_colour=border_colour, 
            hover_colour=hover_colour, active_colour=active_colour, thickness=thickness))

    @staticmethod
    def bubble_text_button(rect: pygame.Rect, text: str, function: Callable, 
                           config: str = "default", shadow_config: str = "shadow_default",
                           shadow_offset: tuple[int, int] = (2, 2),
                           bg_colour: str = "ButtonBG", border_colour: str = "ButtonBorder", 
                           hover_colour: str = "ButtonHover", active_colour: str = "ButtonActive", 
                           thickness: int = 2) -> BorderButton:
        """Creates a bordered button containing shadowed text."""
        v_normal = UIFactory.solid_element(rect, bg_colour)
        shadow_text = UIFactory.bubble_text(
            rect=rect, text=text, config=config, 
            shadow_config=shadow_config, shadow_offset=shadow_offset
        )
        
        base_button = Button(rect, function=function, base_visual=v_normal, content=shadow_text)
        
        return cast("BorderButton", BorderWrapper(
            target=base_button, normal_colour=border_colour, 
            hover_colour=hover_colour, active_colour=active_colour, thickness=thickness))

    @staticmethod
    def color_swap_text_button(rect: pygame.Rect, text: str, function: Callable, 
                               config: str = "default",
                               bg_normal: str = "ButtonNormal", 
                               bg_hover: str = "ButtonHover", 
                               bg_active: str = "ButtonActive") -> Button:
        """Creates a button that entirely replaces its background color on hover/click."""
        surf_normal = UIFactory._create_solid_surf(rect.size, bg_normal)
        surf_hover = UIFactory._create_solid_surf(rect.size, bg_hover)
        surf_active = UIFactory._create_solid_surf(rect.size, bg_active)

        text_element = TextBox(rect=rect, text=text, config=config, align="center")
        base_button = Button(rect, function=function, base_visual=UIElement(rect), content=text_element)
        
        # Note: Kept as standard Button because ImageSwapWrapper isn't in our current generation matrix
        return cast(Button, ImageSwapWrapper(target=base_button, 
            surf_normal=surf_normal, surf_hover=surf_hover, surf_active=surf_active))
     
    # ----- Slot Varieties -----
    @staticmethod
    def bordered_slot(rect: pygame.Rect, index: int) -> BorderSlot:
        """Builder for an inventory slot with dynamic borders."""
        base_slot = UIFactory.slot(rect, index)


        
        return cast("BorderSlot", BorderWrapper(
            target=base_slot, normal_colour="SLOT_BORDER", 
            hover_colour="HOVER_COLOUR", active_colour="ACTIVE_COLOUR",
            thickness=2
        ))

    # ----- Progress Bar Varieties -----
    @classmethod
    def progress_bar(cls, rect: pygame.Rect, percentage: float = 1.0,
                   value_getter: Callable[[], float] | None = None,
                   fill_colour: Any = (56, 220, 245),
                   bg_colour: Any = (30, 30, 30),
                   alignment: str = "midleft",
                   is_horizontal: bool | None = None) -> ProgressBar:
        """Assembles a HealthBar using standard solid_element blocks with dynamic anchoring."""
        
        bg_element = cls.solid_element(rect=rect.copy(), colour=bg_colour)
        fill_element = cls.solid_element(rect=rect.copy(), colour=fill_colour)
        
        return ProgressBar(
            rect=rect,
            bg_element=bg_element,
            fill_element=fill_element,
            percentage=percentage,
            value_getter=value_getter,
            alignment=alignment,
            is_horizontal=is_horizontal
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
            
        total_height = (total_items * item_size[1]) + ((total_items - 1) * gap)
        
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
    
    @staticmethod
    def inventory_with_tooltip(rect: pygame.Rect, inventory_data: 'Inventory',
        columns: int = 4, slot_size: int = 40, padding: int = 5,
        tooltip_config: str = "HUD", tooltip_offset: tuple[int, int] = (15, 12)) -> 'Tooltip':
        """Builder for an InventoryUI automatically wrapped with a mouse-following tooltip."""
        
        # Create the base grid
        base_inventory_ui = InventoryUI(
            rect=rect,
            inventory_data=inventory_data,
            columns=columns,
            slot_size=slot_size,
            padding=padding
        )

        # Create the empty TextBox that will act as the tooltip
        tooltip_box = UIFactory.text(
            rect=pygame.Rect(0, 0, 0, 0),
            text="",
            config=tooltip_config, 
            align="topleft" 
        )

        # Wrap them together and return the wrapper
        return Tooltip(
            target=base_inventory_ui, 
            tooltip_box=tooltip_box, 
            offset=tooltip_offset
        )