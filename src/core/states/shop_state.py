from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.types import StateID

# Runtime Imports (Essential for logic/inheritance)
from src.ui import ShopMenu
from src.utils import Log

from .base_ui_state import BaseUIState

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from src.custom_types import Game, Item, Player, Pos, ShopData



class ShopState(BaseUIState):
    state_id = StateID.SHOP
    def __init__(self, game:Game, player: Player, shop_data: ShopData):
        super().__init__(game, "OVERLAY", back_button=False, click_exit=True)
        self.player = player
        self.key_binds[pygame.K_p] = self.game.pop
        self.key_binds[pygame.K_ESCAPE] = self.game.pop

        self.shop_menu = ShopMenu(
            buy_callback=self._handle_purchase,
            money_getter=lambda: self.player.money,
            data=shop_data
        )
        self.shop_menu.is_open = True
        self.panel = self.shop_menu
        self.ui_group.add(self.shop_menu)        
        
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
