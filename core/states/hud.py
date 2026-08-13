from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from settings import HUD_BUTTON_SIZE, MONEY_RECT
from ui.ui_factory import UIFactory, TextBox
from .base import BaseUIState
from core.types import StateID
from core.debug_logger import Log

if TYPE_CHECKING:
    from entities.player import Player
    from custom_types import Pos, Game


class HUD(BaseUIState):
    state_id = StateID.HUD
    def __init__(self, game:Game, player:Player):
        super().__init__(game, back_button=False)
        self.player = player
        self.transparent = True
        self.suppress_update = False
        self.key_binds[pygame.K_ESCAPE] = self.escape

        button_data = [
            {"text": "SHOP", "function": self.player_open_shop},
            {"text": "*",  "function": self.open_settings}
        ]
        hud_buttons = UIFactory.create_grid(
            factory=UIFactory.bordered_text_button,
            start_pos=(HUD_BUTTON_SIZE // 2, HUD_BUTTON_SIZE // 2),
            columns=1,
            item_size=(HUD_BUTTON_SIZE, HUD_BUTTON_SIZE),
            gap=(0, 10),
            data=button_data,
            # Shared kwargs applied to every button automatically
            bg_colour="ButtonBG",
            border_colour="ButtonBorder",
            hover_colour="ButtonHover"
        )
        self.ui_group.add(*hud_buttons)
       
        self.ui_group.add(UIFactory.bubble_text(
            rect=MONEY_RECT,
            text_getter=lambda: f"Money: {self.player.money}",
            config="HUD"))
    def escape(self):
        Log.info("Add pause menu")
    def player_open_shop(self):
        """Helper to trigger the shop transition through the game mediator."""
        from core.assets import ASSETS
        shop_data = ASSETS.shop("general_store")
        self.game.open_shop(self.player, shop_data)
    def open_settings(self): 
        """Pushes the settings overlay onto the state stack."""
        self.game.open_settings()

    def draw(self, screen:pygame.Surface) -> None:
        # Draw the buttons/text boxes
        super().draw(screen)
        # Draw the inventory UI
        self.player.inventory.draw(screen)
        mouse_pos = pygame.mouse.get_pos()
        self.player.inventory_manager.draw_cursor_item(screen, mouse_pos)

    def update(self, dt: float, is_paused: bool = False) -> None:
        # Update the buttons and text boxes
        super().update(dt, is_paused)
        # Update the inventory slots
        self.player.inventory.update(pygame.mouse.get_pos())

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Pass events to the HUD elements and the inventory."""
        # Check if a HUD button was clicked
        if super().handle_event(event):
            return True
        
        # Pass mouse press, motion, and release events to the inventory drag/drop manager
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
            if getattr(event, 'button', 1) == 1:
                if self.player.inventory_manager.handle_event(event):
                    return True
                
        return False