import pygame

class Shop(pygame.sprite.Sprite):
    def __init__(self, screen, font, items, rect):
        super().__init__()
        self.screen = screen
        self.font = font
        self.items = items
        self.rect = rect
        self.image = pygame.Surface(rect.size, pygame.SRCALPHA)
        
        # Animation states
        self.is_open = False
        self.is_animating = False
        self.animation_speed = 15
        
        # Store positions
        self.hidden_y = screen.get_height()  # Fully off-screen bottom
        self.shown_y = (screen.get_height() - self.rect.height) // 2  # Perfect vertical center
        
        # Start hidden
        self.rect.y = self.hidden_y

    def draw(self, coin_count):
        # Clear and redraw the overlay
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, (30, 30, 30, 200), self.image.get_rect(), border_radius=20)

        # Draw shop content
        y_offset = 50
        for index, (item, details) in enumerate(self.items.items()):
            text = f"{index + 1}. {item}: ${details['price']} - {details['effect']}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.image.blit(text_surface, (20, y_offset))
            y_offset += 40

        # Display coins
        coins_text = self.font.render(f"Coins: {coin_count}", True, (255, 255, 0))
        self.image.blit(coins_text, (20, 10))

    def toggle(self):
        if not self.is_animating:
            self.is_open = not self.is_open
            self.is_animating = True

    def update_animation(self):
        if self.is_animating:
            if self.is_open:
                # Moving up to show (smoothly)
                self.rect.y = max(self.shown_y, self.rect.y - self.animation_speed)
                if self.rect.y == self.shown_y:
                    self.is_animating = False
            else:
                # Moving down to hide (smoothly)
                self.rect.y = min(self.hidden_y, self.rect.y + self.animation_speed)
                if self.rect.y == self.hidden_y:
                    self.is_animating = False

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self.toggle()

    def update(self, coin_count):
        self.update_animation()
        self.draw(coin_count)