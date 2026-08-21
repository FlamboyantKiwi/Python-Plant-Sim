from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

# Runtime Imports (Essential for logic/inheritance)
from src.ui import UIFactory
from src.config import WIDTH, HEIGHT
from ..types import StateID, PlayerType
from .. import Log

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from src.custom_types import PlayerType

from .base_ui_state import BaseUIState

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
