import pygame
from settings import WIDTH, HEIGHT, FPS

# Import your new Managers
from core.asset_loader import AssetLoader
from core.states import MenuState
from core.state_manager import StateManager


class Game:
    def __init__(self):
        # 1. Pygame Setup
        pygame.init()
        pygame.display.set_caption("Freddy's Python Plant Sim")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.tick = 0

        # 2. Load Assets + States
        AssetLoader()
        self.state_manager = StateManager(self)
        #start with playing - will change later to main menu
        self.state_manager.push(MenuState(self))
        
    def run(self):
        while self.running:
            self.tick += 1
            current_state = self.state_manager.current()
            if not current_state: 
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # Pass event to the Current State
                current_state.handle_event(event)

            current_state.update()
            current_state.draw(self.screen)
        
            pygame.display.update()
            self.clock.tick(FPS)