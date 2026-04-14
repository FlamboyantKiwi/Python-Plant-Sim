from __future__ import annotations
import sys
import pygame
from typing import TYPE_CHECKING

from settings import WIDTH, HEIGHT, FPS
from core.assets import ASSETS
from core.types import StateStack, StateID
from core.states import (GameState, PlayingState, ShopState, STATE_REGISTRY)

if TYPE_CHECKING:
    from core.types import ShopData

class Game:
    def __init__(self) -> None:
        # Pygame Setup 
        pygame.init()
        pygame.display.set_caption("Freddy's Python Plant Sim")
        self.screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.tick: int = 0
        self.dt = 0.0 # Delta time

        # Load Assets
        ASSETS.load_all()
        
        # State Management
        self.stack: StateStack[GameState] = StateStack()

        # Aliases
        self.push = self.stack.push
        self.pop = self.close_menu = self.stack.pop
        self.change = self.stack.change
        self.peek = self.stack.peek

        # Start the game using the Enum
        self.open_state(StateID.MENU)

    def run(self) -> None:
        """The main game loop."""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.tick += 1
            
            current_state = self.stack.peek()
            # Safety check: If the stack is empty, shut down
            if not current_state: 
                self.quit()
                break
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                current_state.handle_event(event)

            # Update & Draw 
            self.stack.update(self.dt)
            self.stack.draw(self.screen)
            
            pygame.display.update()
  
    def open_state(self, state_id: StateID, *args, **kwargs):
        """The brain of the transition logic."""
        state_class = STATE_REGISTRY.get(state_id)
        
        if not state_class:
            print(f"State {state_id} not found in registry!")
            return

        # Initialize the state
        instance = state_class(self, *args, **kwargs)
        
        # Layering Logic
        if instance.transparent:
            self.stack.push(instance)
        else:
            self.stack.change(instance)

    def start_new_game(self, character_type):
        self.change(PlayingState(self, character_type))

    def load_save_game(self):
        self.change(PlayingState(self))

    def open_shop(self, player_ref, shop_data: ShopData):
        self.push(ShopState(self, player_ref, shop_data))

    def quit(self) -> None:
        """Safely shuts down the game, cleans assets, and exits."""
        print("Initiating shutdown sequence...")
        self.running = False
        ASSETS.clean_up()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
    
    