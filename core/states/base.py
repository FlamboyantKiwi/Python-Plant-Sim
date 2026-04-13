
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Any
import pygame

# Runtime Imports (Essential for logic/inheritance)
from groups.ui_group import UIGroup

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from custom_types import Game, Pos

class GameState(ABC):
    def __init__(self, game:Game):
        self.game = game
        # Event Mapping Dict
        self.key_binds: dict[int, Callable] = {} # e.g. pygame.K_ESCAPE: self.func
        self.mouse_binds: dict[int, Callable[[Pos], None]] = {
            1: self.on_left_click,
            2: self.on_middle_click,
            3: self.on_right_click}
        
    @abstractmethod
    def update(self)-> None: pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None: pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if action := self.key_binds.get(event.key): 
                action()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if action := self.mouse_binds.get(event.button): 
                action(event.pos)
        return False

    def enter_state(self) -> None: pass
    def exit_state(self) -> None: pass

    #Click actions - override in child classes
    def on_left_click(self, pos: Pos) -> None: pass
    def on_right_click(self, pos: Pos) -> None: pass
    def on_middle_click(self, pos: Pos) -> None: pass

class BaseUIState(GameState):
    """"Parent class managing a list of UI elements via the UIElementProtocol.
    (Menu, Shop, Inventory, Credits, etc)."""
    def __init__(self, game: Game):
        super().__init__(game)
        self.ui_group = UIGroup()

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.ui_group.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        self.ui_group.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        # Handle UI Clicks
        if self.ui_group.handle_event(event):
            return True
        return super().handle_event(event)
