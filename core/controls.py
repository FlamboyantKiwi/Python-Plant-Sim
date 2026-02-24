import pygame
from core.types import  DOWN, RIGHT, LEFT, UP
class KeyBindings:
    def __init__(self):
        # Action Keys
        self.interact = pygame.K_SPACE
        self.run = pygame.K_LSHIFT

        # Movement Keys (Stored as lists to allow primary/secondary bindings)
        self.up = [pygame.K_w, pygame.K_UP]
        self.down = [pygame.K_s, pygame.K_DOWN]
        self.left = [pygame.K_a, pygame.K_LEFT]
        self.right = [pygame.K_d, pygame.K_RIGHT]

        # Inventory Slots
        self.slots = {
            pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
            pygame.K_5: 4, pygame.K_6: 5, pygame.K_7: 6, pygame.K_8: 7
        }

        self.facing_map = {
            (-1, 0): LEFT,
            (1, 0):  RIGHT,
            (0, -1): UP,
            (0, 1):  DOWN,
            (-1, -1): LEFT,  
            (1, -1):  RIGHT, 
            (-1, 1):  LEFT,  
            (1, 1):   RIGHT, 
        }
        
    @property
    def direction_keys(self):
        """ Dynamically builds the vector dictionary. 
        Automatically updates if changed during runtime"""
        binds = {}
        for key in self.up:    
            binds[key] = (0, -1)
        for key in self.down:  
            binds[key] = (0, 1)
        for key in self.left:  
            binds[key] = (-1, 0)
        for key in self.right: 
            binds[key] = (1, 0)
        return binds

    def rebind(self, action: str, new_key: int):
        """Helper method we can use later for a Settings menu."""
        if hasattr(self, action):
            setattr(self, action, new_key)
            print(f"Rebound {action} to {pygame.key.name(new_key)}")

# Create a global instance that the rest of your game can import
controls = KeyBindings()