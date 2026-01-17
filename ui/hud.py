import pygame
from settings import WIDTH, SHOP_BUTTON
from core.helper import get_colour
from core.types import FontType
from core.asset_loader import AssetLoader
from ui.button import Button


class HUD:
    def __init__(self, player):
        self.player = player
        self.all_buttons = pygame.sprite.Group()
        self.shop_button = Button(
            rect=SHOP_BUTTON, 
            text="SHOP", 
            image_filename="SHOP_ICON",
            font_type=FontType.HUD)
        self.all_buttons.add(self.shop_button)

    def draw(self, screen):
        text = f"Money: {self.player.money}"
        
        font = AssetLoader.get_font(FontType.HUD)
        text_surface = font.render(text, True, get_colour("Gold","Money"))
        
        text_rect = text_surface.get_rect(
            centerx=WIDTH // 2,
            top=10
        )
        screen.blit(text_surface, text_rect)
        self.all_buttons.draw(screen)

        self.player.inventory.draw(screen)

    def update(self, mouse_pos):
        self.all_buttons.update(mouse_pos)
        self.player.inventory.update(mouse_pos)

    def handle_click(self, pos):
        # Open/Close shop menu
        if self.shop_button.is_click(pos):
            print("HUD: Shop Button Clicked")
            return "OPEN_SHOP"
        if self.player.inventory.handle_click(pos):
            return "INVENTORY_CLICK"
        return None
            