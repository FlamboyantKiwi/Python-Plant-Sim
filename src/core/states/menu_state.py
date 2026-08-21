from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

# Runtime Imports (Essential for logic/inheritance)
from src.ui import UIFactory
from src.settings import WIDTH, HEIGHT
from src.core.types import StateID
from src.core import Log

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from src.custom_types import Game

from .base_ui_state import BaseUIState
from .settings_state import SettingsState

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
