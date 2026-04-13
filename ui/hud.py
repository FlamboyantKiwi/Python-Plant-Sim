from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from settings import SHOP_BUTTON, MONEY_RECT
from ui.ui_elements import Button, TextBox
from groups.ui_group import UIGroup

if TYPE_CHECKING:
    from entities.player import Player
    from custom_types import Pos


class HUD:
    def __init__(self, player:Player):
        self.player = player
        self.ui_group = UIGroup()
        self.ui_group.add(
            Button.create_bordered_button(
                rect=SHOP_BUTTON, 
                text="SHOP", 
                function=lambda: "OPEN_SHOP",
                bg_colour="ButtonBG",
                border_colour="ButtonBorder",
                hover_colour="ButtonHover"
            )
        )
        
        self.ui_group.add(
            TextBox(
                rect=MONEY_RECT,
                text_getter=lambda: f"Money: {self.player.money}",
                config="HUD"
            )
        )
    def draw(self, screen:pygame.Surface):
        for element in self.ui_group:
            element.draw(screen)

        self.player.inventory_ui.draw(screen)

    def update(self, mouse_pos:Pos):
        for element in self.ui_group:
            element.update(mouse_pos)
        self.player.inventory_ui.update(mouse_pos)

    def handle_click(self, pos:Pos):
        for element in self.ui_group:
            if element.is_click(pos):
                return element.handle_click() 
            
        if self.player.handle_click(pos):
            return True
        return None
            