from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from settings import SHOP_BUTTON, MONEY_RECT
from ui.ui_elements import Button, TextBox
from .base import BaseUIState
from core.types import StateID

if TYPE_CHECKING:
    from entities.player import Player
    from custom_types import Pos, Game


class HUD(BaseUIState):
    state_id = StateID.HUD
    def __init__(self, game:Game, player:Player):
        super().__init__(game)
        self.player = player
        self.transparent = True
        self.suppress_update = False
        self.ui_group.add(
            Button.create_bordered_button(
                rect=SHOP_BUTTON, 
                text="SHOP", 
                function=self.player_open_shop,
                bg_colour="ButtonBG",
                border_colour="ButtonBorder",
                hover_colour="ButtonHover"))
        self.ui_group.add(
            TextBox(
                rect=MONEY_RECT,
                text_getter=lambda: f"Money: {self.player.money}",
                config="HUD"))
    def player_open_shop(self):
        """Helper to trigger the shop transition through the game mediator."""
        from core.assets import ASSETS
        shop_data = ASSETS.shop("general_store")
        self.game.open_shop(self.player, shop_data)

    def draw(self, screen:pygame.Surface) -> None:
        # Draw the buttons/text boxes
        super().draw(screen)
        # Draw the inventory UI
        self.player.inventory_ui.draw(screen)

    def update(self, dt: float, is_paused: bool = False) -> None:
        # Update the buttons and text boxes
        super().update(dt, is_paused)
        # Update the inventory slots
        self.player.inventory_ui.update(pygame.mouse.get_pos())

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Pass events to the HUD elements and the inventory."""
        # Check if a HUD button was clicked
        if super().handle_event(event):
            return True
        
        # Check if the Inventory slots were clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.player.handle_click(event.pos):
                return True
                
        return False