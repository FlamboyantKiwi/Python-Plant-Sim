from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

# Runtime Imports (Essential for logic/inheritance)
from src.ui import UIFactory
from src.config import SETTINGS_MENU
from ..types import StateID
#from src.core import Log

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from src.custom_types import Game

from .base_ui_state import BaseUIState

class SettingsState(BaseUIState):
    state_id = StateID.SETTINGS

    def __init__(self, game: Game):
        # Uses the translucent overlay and automatically adds a Back button
        super().__init__(game, "OVERLAY", back_button=False, click_exit=True)
        
        # Freezes the game logic running underneath it
        self.suppress_update = True 

        # Draw the Main Window Panel
        self.panel = UIFactory.static_border_element(
            rect=SETTINGS_MENU,
            colour="MenuBG",              # Dark grey background
            border_colour="ButtonBorder", # Lighter grey rim
            thickness=3
        )
        self.ui_group.add(self.panel)

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
