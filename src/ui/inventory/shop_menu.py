from __future__ import annotations
import pygame
from typing import TYPE_CHECKING, Callable
from ..ui_factory import UIFactory
from ..elements import UIElement
from src.entities import Item, create_item
from src.config import SHOP_GRID_OFFSET_Y, SHOP_MENU
from src.entities.inventory_data import Inventory

if TYPE_CHECKING:
    from src.custom_types import Pos, ShopData


class ShopMenu(UIElement):
    """Controller for the Shop. Decoupled from the Player via callbacks."""
    def __init__(self, buy_callback: Callable[[Item], bool], money_getter: Callable[[], int], data: ShopData | None, columns: int = 4, max_size: int = 16) -> None:
        super().__init__(rect=SHOP_MENU)
        self.buy_callback = buy_callback
        self.money_getter = money_getter
        self.shop_data: ShopData | None = data
        self.is_open: bool = False
        
        # Background visual
        self.background = UIFactory.static_border_element(
            rect=self.rect, 
            colour="MenuBG", 
            border_colour="ButtonBorder", 
            thickness=3
        )
        
        # The Pure Data
        self.inventory_data: Inventory = Inventory(max_size=max_size)
        grid_rect = self.rect.copy()
        grid_rect.y += SHOP_GRID_OFFSET_Y
        
        # The Visual Grid
        self.ui_grid = UIFactory.inventory_ui(
            rect=grid_rect, 
            inventory_data=self.inventory_data, 
            columns=columns, 
            slot_size=70, 
            padding=20
        )
        
        title_string = self.shop_data.store_name if self.shop_data else "Shop"
        self.title_box: UIElement = UIFactory.text(
            rect=pygame.Rect(self.rect.centerx, self.rect.top + 10, 0, 0),
            text=title_string,
            config="HUD", 
            align="midtop"
        )
        self.populate_shop()

    def try_buy_item(self, item: Item) -> bool:
        """Delegates the transaction purchase request upward via callback."""
        return self.buy_callback(item)

    def populate_shop(self) -> None:
        """ Reads IDs from shop_data and fills the backend data structure. """
        if not self.shop_data: 
            return

        for i, item_id in enumerate(self.shop_data.items_ids):
            if i >= self.inventory_data.max_size: 
                break

            # Create the item and insert it straight into the pure data list
            new_item = create_item(item_id, count=1)
            self.inventory_data.items[i] = new_item
            
            self.ui_grid.slots[i].set_price(new_item.data.buy_price)

    def update(self, mouse_pos:Pos|None=None) -> None:
        """ Runs the UI updates and re-applies price tags. """
        if not self.is_open: 
            return
        
        # This syncs the UI with the data (and normally sets text to stack count)
        self.ui_grid.update(mouse_pos)
        self.title_box.update()

    def draw(self, screen:pygame.Surface) ->None:
        if not self.is_open: 
            return
        
        # Draw Background Image
        self.background.draw(screen)

        # Draw Title
        self.title_box.draw(screen)
        
        # Draw the Grid UI
        self.ui_grid.draw(screen)
  
    def handle_click(self, pos:Pos|None = None) -> bool:
        """Handles interaction. Returns a string action code if the State needs to react."""
        if not self.is_open: 
            return False
        if pos is None:
            pos = pygame.mouse.get_pos()

        # Let the UI grid tell us the index of what was clicked
        clicked_index = self.ui_grid.click(pos)
        
        if clicked_index is not None:
            # Grab the actual item object from the data layer using the index
            item = self.inventory_data.items[clicked_index]
            if item:
                return self.try_buy_item(item)
                
        return False
    
    def is_click(self, mouse_pos: Pos) -> bool:
        """Conforms to UIElement interface to verify interaction bounds."""
        return self.is_open and self.rect.collidepoint(mouse_pos)
