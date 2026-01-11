#main.py - Now a Launcher
import sys
import pygame
from core.game import Game 

# Setup and Start Game Loop
game = Game()
game.run()

# Exit
pygame.quit()
sys.exit()
