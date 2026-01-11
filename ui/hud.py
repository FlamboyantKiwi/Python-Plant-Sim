import pygame
from settings import WIDTH, HUD_FONT, SHOP_BUTTON
from core.helper import get_colour
from ui.button import Button


class HUD:
    def __init__(self, player):
        self.player = player
        self.all_buttons = pygame.sprite.Group()
        self.shop_button = Button(
            rect=SHOP_BUTTON, 
            text="SHOP", 
            image_filename="SHOP_ICON",
            font=HUD_FONT)
        self.all_buttons.add(self.shop_button)
        #self.shop_menu = ShopMenu(player, 4, 16)
    def draw(self, screen):
        text = f"Money: {self.player.money}"
        
        text_surface = HUD_FONT.render(text, True, get_colour("Gold","Money"))
        
        text_rect = text_surface.get_rect(
            centerx=WIDTH // 2,
            top=10
        )
        screen.blit(text_surface, text_rect)
        self.all_buttons.draw(screen)

        self.player.inventory.draw(screen)
        
        #self.shop_menu.draw(screen)
    def update(self, mouse_pos):
        self.all_buttons.update(mouse_pos)
        self.player.inventory.update(mouse_pos)
        #if self.shop_menu.is_open:
        #    self.shop_menu.update(mouse_pos)
    def handle_click(self, pos):
        # Open/Close shop menu
        if self.shop_button.is_click(pos):
            print("HUD: Shop Button Clicked")
            return "OPEN_SHOP"
        if self.player.inventory.handle_click(pos):
            return "INVENTORY_CLICK"
            
        
        """self.shop_menu.toggle_open(self)
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
            self.all_buttons.add(self.shop_button)"""
