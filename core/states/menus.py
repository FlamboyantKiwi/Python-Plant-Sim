from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame

# Runtime Imports (Essential for logic/inheritance)
from ui.ui_elements import Button, BubbleText
from ui.InventoryUI import ShopMenu
from settings import WIDTH, HEIGHT
from core.types import StateID, PlayerType
from .base import BaseUIState

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from custom_types import Game, Pos, PlayerType
    from entities.player import Player
    from core.types import ShopData

class ShopState(BaseUIState):
    state_id = StateID.SHOP
    def __init__(self, game:Game, player: Player, shop_data: ShopData):
        super().__init__(game, "OVERLAY", back_button=False)
        self.player = player
        self.key_binds[pygame.K_p] = self.game.pop
        self.key_binds[pygame.K_ESCAPE] = self.game.pop

        self.shop_menu = ShopMenu(self.player, data=shop_data) 
        self.shop_menu.is_open = True
    
    def update(self, dt, is_paused: bool = False) -> None:
        # Update Buttons
        super().update(is_paused)
        
        # Update Shop Menu explicitly
        self.shop_menu.update(pygame.mouse.get_pos())

    def draw(self, screen: pygame.Surface) -> None:
        # Draw the bright shop menu on top of default overlay
        super().draw(screen) # Draw BG+Buttons
        self.shop_menu.draw(screen)
        

    def on_left_click(self, pos: Pos) -> None:
        # Check if we clicked inside the shop menu (slots/buying)
        if self.shop_menu.rect.collidepoint(pos):
            self.shop_menu.handle_click(pos)
        
        # Clicked OUTSIDE the shop menu -> Close Shop
        else:
            self.game.pop()
    def on_right_click(self, pos: Pos) -> None:
        self.game.pop()

class MenuState(BaseUIState):
    state_id = StateID.MENU
    def __init__(self, game: Game):
        super().__init__(game, "MenuBG", back_button=False)   
        self.suppress_update = True
        self.menu_actions = {
            "New Game": lambda: self.game.open_state(StateID.CHAR_SELECT),
            "Continue": self.game.load_save_game,
            #"Credits": self.game.open_credits,
            "Quit": self.game.quit
        }
        btns = Button.create_vertical_stack(
            center_pos=(WIDTH // 2, HEIGHT // 2),
            data=self.menu_actions,gap=70,
            width=220,
            height=55,
            thickness=3)
        self.ui_group.add(*btns)
        
        title_rect = pygame.Rect(0, 0, 600, 100) 
        title_rect.center = (WIDTH // 2, HEIGHT // 4)   
        self.ui_group.add(BubbleText(
            rect=title_rect,
            text="Python Plant Sim",
            config="MenuTitle",
            shadow_config="MenuTitleShadow", 
            shadow_offset=(4, 4),
            align="center"
        ))

class CharacterSelectState(BaseUIState):
    state_id = StateID.CHAR_SELECT
    def __init__(self, game):
        super().__init__(game, "MenuBG", back_button=True)
        self.key_binds[pygame.K_ESCAPE] = self.game.pop
     
        char_data = [
            (p.value, lambda t=p: self.select_character(t)) 
            for p in PlayerType
        ]

        btns = Button.create_vertical_stack(
            center_pos=(WIDTH // 2, HEIGHT // 2),
            data=char_data,
            width=250 
        )
        
        self.ui_group.add(*btns)
        self.add_back_button()
        
        title_rect = pygame.Rect(0, 0, 600, 100) 
        title_rect.center = (WIDTH // 2, 100)   
        self.ui_group.add(BubbleText(
            rect=title_rect,
            text="Select Character",
            config="MenuTitle",
            shadow_config="MenuTitleShadow", 
            shadow_offset=(4, 4),
            align="center"
        ))
        
    def select_character(self, character_type: PlayerType):
        """Passes the chosen character to the Game mediator to start the session."""
        print(f"Character selected: {character_type}")
        self.game.start_new_game(character_type)


