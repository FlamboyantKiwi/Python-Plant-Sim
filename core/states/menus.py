from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame

# Runtime Imports (Essential for logic/inheritance)
from ui.ui_elements import Button
from ui.InventoryUI import ShopMenu
from settings import WIDTH, HEIGHT
from core.ui_utils import draw_text
from core.assets import ASSETS
from core.types import StateID
from .base import BaseUIState

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from custom_types import Game, Pos, PlayerType
    from entities.player import Player
    from core.types import ShopData

class ShopState(BaseUIState):
    state_id = StateID.SHOP
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
    
    def update(self, dt, is_paused: bool = False) -> None:
        # Update Buttons
        super().update(is_paused)
        
        # Update Shop Menu explicitly
        self.shop_menu.update(pygame.mouse.get_pos())

    def draw(self, screen: pygame.Surface) -> None:
        # Dim the entire screen (including the HUD below us)
        screen.blit(self.overlay, (0, 0))
        
        # Draw the bright shop menu on top
        self.shop_menu.draw(screen)
        super().draw(screen) # Draw Buttons

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
    state_id = StateID.MENU
    def __init__(self, game: Game):
        super().__init__(game)
        self.transparent = False     
        self.suppress_update = True
        self.menu_actions = {
            "New Game": lambda: self.game.open_state(StateID.CHAR_SELECT),
            "Continue": self.game.load_save_game,
            #"Credits": self.game.open_credits,
            "Quit": self.game.quit
        }
        self.create_buttons()
    
    def create_buttons(self)-> None:
        # Calculate Layout
        btns = Button.create_vertical_stack(center_pos=(WIDTH // 2, HEIGHT // 2),
            data=self.menu_actions,gap=60)
        self.ui_group.add(*btns)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(ASSETS.colour("MenuBG"))

        draw_text(screen, "Python Plant Sim", "TITLE", x=WIDTH//2, y=HEIGHT//4, 
                  colour="MenuTitle", align="center")
        
        super().draw(screen)

class CharacterSelectState(BaseUIState):
    state_id = StateID.CHAR_SELECT
    def __init__(self, game):
        super().__init__(game)
        self.key_binds[pygame.K_ESCAPE] = self.game.pop
        # Create a dimming overlay for the background
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150)) # Slightly darker than the shop
        self.create_ui()

    def create_ui(self):
        # We can iterate through our PlayerType Enum to auto-generate buttons!
        from core.types import PlayerType
        
        char_data = [
            (p.value, lambda t=p: self.select_character(t)) 
            for p in PlayerType
        ]

        btns = Button.create_vertical_stack(
            center_pos=(WIDTH // 2, HEIGHT // 3),
            data=char_data,
            width=250 # Custom width for names
        )
        
        self.ui_group.add(*btns)
        self.add_back_button()

    def select_character(self, character_type: PlayerType):
        """Passes the chosen character to the Game mediator to start the session."""
        print(f"Character selected: {character_type}")
        self.game.start_new_game(character_type)

    def draw(self, screen: pygame.Surface) -> None:
        # The Dimming Overlay (Middle)
        screen.blit(self.overlay, (0, 0))
        
        draw_text(screen, "Select Character", "TITLE", WIDTH//2, 100, colour="MenuTitle")
        super().draw(screen)

"""

class CharacterSelectState(BaseUIState):
    def __init__(self, game):
        super().__init__(game)
        self.ui_elements = self.create_buttons()
        
    # --- Button Actions ---
    def start_game_with_character(self, character_type):
        print(f"Selected: {character_type}")
        # Pass the chosen character type into the PlayingState
        self.game.change(PlayingState(self.game, character_type))
        
    def go_back(self):
        # Return to main menu
        self.game.change(MenuState(self.game))
"""