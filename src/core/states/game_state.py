from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Type
import pygame

from src.core.types import StateID

# Type-Only Imports (Breaks circular loops)
if TYPE_CHECKING:
    from src.custom_types import Game, Pos

STATE_REGISTRY: dict[StateID, Type["GameState"]] = {}

class GameState(ABC):
    state_id: StateID | None = None
    def __init__(self, game:Game):
        self.game = game
        # Flags control how the Game stack behaves
        self.transparent: bool = False  # If True, the state below will draw first
        self.back_button:bool = False
        self.suppress_update: bool = True # If True, the state below freezes logic
        # Event Mapping Dict
        self.key_binds: dict[int, Callable] = {} # e.g. pygame.K_ESCAPE: self.func
        self.mouse_binds: dict[int, Callable[[Pos], None]] = {
            1: self.on_left_click,
            2: self.on_middle_click,
            3: self.on_right_click}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.state_id is not None:
            STATE_REGISTRY[cls.state_id] = cls

    @abstractmethod
    def update(self, dt:float, is_paused: bool = False) -> None: pass

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
