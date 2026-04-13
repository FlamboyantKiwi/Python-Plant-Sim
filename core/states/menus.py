from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame

# Runtime Imports (Essential for logic/inheritance)
from entities.player import Player
from ui.ui_elements import Button
from ui.InventoryUI import ShopMenu
from settings import WIDTH, HEIGHT
from core.ui_utils import draw_text
from core.assets import ASSETS
from core.types import ShopData

from .base import BaseUIState

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from custom_types import Game, Pos

class ShopState(BaseUIState):
    def __init__(self, game:Game, player: Player, shop_data: ShopData):
        super().__init__(game)
        self.player = player
       
        self.key_binds = {
            pygame.K_ESCAPE: self.close_menu,
            pygame.K_p: self.close_menu
        }

        self.shop_menu = ShopMenu(self.player, data=shop_data) 
        self.shop_menu.is_open = True

        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128)) # Black with 50% alpha
    def update(self)-> None:
        # Update Buttons
        super().update()
        
        # Update Shop Menu explicitly
        mouse_pos = pygame.mouse.get_pos()
        self.shop_menu.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        # Draw the game behind the menu (Transparent look)
        self.game.draw_previous()
        
        # Blit the pre-calculated overlay (Dim the background)
        screen.blit(self.overlay, (0, 0))

        self.shop_menu.draw(screen)
        
        # Draw Buttons
        super().draw(screen)

    def on_left_click(self, pos: Pos) -> None:
        # Check if we clicked inside the shop menu (slots/buying)
        if self.shop_menu.rect.collidepoint(pos):
            self.shop_menu.handle_click(pos)
        
        # Clicked OUTSIDE the shop menu -> Close Shop
        else:
            self.close_menu()
    def on_right_click(self, pos: Pos) -> None:
        self.close_menu()
    def close_menu(self, *args:Any) -> None:
        self.game.pop()

class MenuState(BaseUIState):
    def __init__(self, game: Game):
        super().__init__(game)
        self.menu_actions = {
            "New Game": self.game.start_new_game,
            "Continue": self.game.load_save_game,
            "Credits": self.game.open_credits,
            "Quit": self.game.quit
        }
        self.create_buttons()
    
    def create_buttons(self)-> None:
        # Calculate Layout
        center_x = WIDTH // 2
        start_y = HEIGHT // 2 - 50
        gap = 60
        btn_width, btn_height = 200, 50

        for i, (text, func) in enumerate(self.menu_actions.items()):
            rect = pygame.Rect(0, 0, btn_width, btn_height)
            rect.center = (center_x, start_y + (i * gap))
            
            btn = Button.create_bordered_button(rect=rect, text=text, function=func)
            self.ui_group.add(btn)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(ASSETS.colour("MenuBG"))

        draw_text(screen, "Python Plant Sim", "TITLE", x=WIDTH//2, y=HEIGHT//4, 
                  colour="MenuTitle", align="center")
        
        super().draw(screen)

