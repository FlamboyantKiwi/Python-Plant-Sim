from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame

# Runtime Imports (Essential for logic/inheritance)
from src.ui import UIFactory, ShopMenu
from src.settings import WIDTH, HEIGHT, SETTINGS_MENU
from src.core.types import StateID, PlayerType
from src.core import Log

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from src.custom_types import Game, Pos, PlayerType, Player, ShopData, Item

from .base import BaseUIState

class ShopState(BaseUIState):
    state_id = StateID.SHOP
    def __init__(self, game:Game, player: Player, shop_data: ShopData):
        super().__init__(game, "OVERLAY", back_button=False)
        self.player = player
        self.key_binds[pygame.K_p] = self.game.pop
        self.key_binds[pygame.K_ESCAPE] = self.game.pop

        self.shop_menu = ShopMenu(
            buy_callback=self._handle_purchase,
            money_getter=lambda: self.player.money,
            data=shop_data
        )
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

    def _handle_purchase(self, item: Item) -> bool:
        """Validates and executes the purchase logic for the shop."""
        cost = item.data.buy_price
        if self.player.money < cost:
            Log.error(f"Cannot afford {item.name}! (Cost: {cost}, Have: {self.player.money})")
            return False
        
        player_item = item.copy_one()
        if self.player.inventory.data.add_item(player_item):
            self.player.money -= cost
            Log.info(f"Bought {player_item.name} for {cost}g.")
            return True
        
        Log.error("Transaction failed (Inventory full).")
        return False

class MenuState(BaseUIState):
    state_id = StateID.MENU
    def __init__(self, game: Game):
        super().__init__(game, "MenuBG", back_button=False)   
        self.suppress_update = True
        self.menu_actions = {
            "New Game": lambda: self.game.open_state(StateID.CHAR_SELECT),
            "Continue": self.game.load_save_game,
            "Settings": lambda: self.game.push(SettingsState(self.game)),
            #"Credits": self.game.open_credits,
            "Quit": self.game.quit
        }
        btns = UIFactory.create_vertical_stack(
            factory=UIFactory.bordered_text_button,
            center_pos=(WIDTH // 2, HEIGHT // 2),
            item_size=(220, 55),
            gap=70,
            data=[{"text": k, "function": v} for k, v in self.menu_actions.items()],
            # Shared across all buttons in this specific stack
            thickness=3 
        )
        self.ui_group.add(*btns)
        
        title_rect = pygame.Rect(0, 0, 600, 100) 
        title_rect.center = (WIDTH // 2, HEIGHT // 4)   
        self.ui_group.add(UIFactory.bubble_text(
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
     
        char_data = [{
                "text": p.value, 
                "function": lambda t=p: self.select_character(t)
            } for p in PlayerType]
        
        btns = UIFactory.create_vertical_stack(
            factory=UIFactory.bordered_text_button,
            center_pos=(WIDTH // 2, HEIGHT // 2),
            item_size=(250, 50), 
            gap=60,             
            data=char_data
        )
        
        self.ui_group.add(*btns)
        self.add_back_button()
        
        title_rect = pygame.Rect(0, 0, 600, 100) 
        title_rect.center = (WIDTH // 2, 100)   
        self.ui_group.add(UIFactory.bubble_text(
            rect=title_rect,
            text="Select Character",
            config="MenuTitle",
            shadow_config="MenuTitleShadow", 
            shadow_offset=(4, 4),
            align="center"
        ))
        
    def select_character(self, character_type: PlayerType):
        """Passes the chosen character to the Game mediator to start the session."""
        Log.success(f"Character selected: {character_type}")
        self.game.start_new_game(character_type)

class SettingsState(BaseUIState):
    state_id = StateID.SETTINGS

    def __init__(self, game: Game):
        # Uses the translucent overlay and automatically adds a Back button
        super().__init__(game, "OVERLAY", back_button=True)
        
        # Freezes the game logic running underneath it
        self.suppress_update = True 

        # Draw the Main Window Panel
        panel = UIFactory.static_border_element(
            rect=SETTINGS_MENU,
            colour="MenuBG",              # Dark grey background
            border_colour="ButtonBorder", # Lighter grey rim
            thickness=3
        )
        self.ui_group.add(panel)

        # Title (Anchored to the top of the settings menu)
        title_rect = pygame.Rect(0, 0, SETTINGS_MENU.width, 80)
        title_rect.midtop = (SETTINGS_MENU.centerx, SETTINGS_MENU.top + 20)
        
        self.ui_group.add(UIFactory.bubble_text(
            rect=title_rect,
            text="Settings",
            config="MenuTitle",
            shadow_config="MenuTitleShadow",
            shadow_offset=(4, 4),
            align="center"
        ))
        
        # Placeholder Text (Anchored to the dead center of the settings menu)
        placeholder_rect = pygame.Rect(0, 0, SETTINGS_MENU.width, 50)
        placeholder_rect.center = SETTINGS_MENU.center
        
        self.ui_group.add(UIFactory.text(
            rect=placeholder_rect,
            text="Options coming soon...",
            config="HUD",
            align="center"
        ))
