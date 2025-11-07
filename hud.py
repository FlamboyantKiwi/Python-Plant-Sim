import pygame
from button import Button
from settings import SHOP_BUTTON, WIDTH, HUD_FONT
from inventory import ShopMenu
from helper import get_colour


class HUD:
    def __init__(self, player):
        self.player = player
        self.all_buttons = pygame.sprite.Group()
        self.shop_button = Button(SHOP_BUTTON, text="SHOP", image_filename="SHOP_ICON")
        self.all_buttons.add(self.shop_button)
        self.shop_menu = ShopMenu(player, 4, 16)
    def draw(self, screen):
        text = f"Money: {self.player.money}"
        
        text_surface = HUD_FONT.render(text, True, get_colour("Gold","Money"))
        
        text_rect = text_surface.get_rect(
            centerx=WIDTH // 2,
            top=10
        )
        screen.blit(text_surface, text_rect)

        self.player.inventory.draw(screen)
        self.all_buttons.draw(screen)
        self.shop_menu.draw(screen)
    def update(self, mouse_pos):
        self.player.inventory.update(mouse_pos)
        self.all_buttons.update(mouse_pos)
        if self.shop_menu.is_open:
            self.shop_menu.update(mouse_pos)
    def handle_click(self, pos):
        # Open/Close shop menu
        if self.shop_button.is_click(pos):
            self.shop_menu.toggle_open(self)
            return
        
        # Handle Clicks for shop menu (if open)
        if self.shop_menu.is_open:
            self.shop_menu.handle_click(pos)
        else:
            self.player.inventory.handle_click(pos)


    def toggle_shop_buttons(self, is_open):
        if is_open:
            self.all_buttons.remove(self.shop_button)
            self.all_buttons.add(self.exit_button)
        else:
            self.all_buttons.remove(self.exit_button)
            self.all_buttons.add(self.shop_button)
