import pygame

class Crosshair(pygame.sprite.Sprite):
    def __init__(self, size=(40, 40), smoothness=0.1):
        super().__init__()
        self.original_image = pygame.image.load("assets/images/crosshair.png").convert_alpha()
        self.image = pygame.transform.scale(self.original_image, size)
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2(pygame.mouse.get_pos())
        self.smoothness = smoothness  # Lower = more lag (0.05-0.2 works well)
        
    def update(self):
        target_pos = pygame.Vector2(pygame.mouse.get_pos())
        # Smooth movement with linear interpolation
        self.pos += (target_pos - self.pos) * self.smoothness
        self.rect.center = self.pos