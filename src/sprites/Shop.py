import pygame
import os

def round_image(image, radius):
    """Rounds the corners of an image using a mask."""
    size = image.get_size()
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, *size), border_radius=radius)
    rounded_image = image.copy()
    rounded_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return rounded_image

class Shop(pygame.sprite.Sprite):
    def __init__(self, screen, font, turtle, crab, rect):
        super().__init__()
        self.screen = screen
        self.font = font
        self.turtle = turtle
        self.crab = crab
        
        # Define shop items
        self.items = {
            "turtle_health": {
                "price": 20,
                "effect": "Add +1 health to Turtle",
                "action": self.upgrade_turtle_health,
                "icon": "turtle_health"  # Will look for assets/shop/turtle_health.png
            },
            "crab_health": {
                "price": 20,
                "effect": "Add +1 health to Crab",
                "action": self.upgrade_crab_health,
                "icon": "crab_health"  # Will look for assets/shop/crab_health.png
            }
        }
        
        self.title_font = pygame.font.Font(None, 40)
        self.desc_font = pygame.font.Font(None, 24)
        self.rect = rect
        self.image = pygame.Surface(rect.size, pygame.SRCALPHA)
        
        # Animation states
        self.is_open = False
        self.is_animating = False
        self.animation_speed = 15
        self.hidden_y = screen.get_height()
        self.shown_y = (screen.get_height() - self.rect.height) // 2
        self.rect.y = self.hidden_y
        
        # Shop display variables
        self.current_page = 0
        self.items_per_page = 3
        self.hovered_item = None
        self.icon_size = 80
        self.icon_padding = 30
        self.total_pages = (len(self.items) + self.items_per_page - 1) // self.items_per_page
        
        # Load assets
        self.icons = self._load_icons()
        self.arrow_left, self.arrow_right = self._load_arrows()
        self.arrow_rect_left = pygame.Rect(20, rect.height//2 - 25, 50, 50)
        self.arrow_rect_right = pygame.Rect(rect.width - 70, rect.height//2 - 25, 50, 50)
        
        # Visual effects
        self.hovering_left = False
        self.hovering_right = False
        self.last_hovered = None
        
    def upgrade_turtle_health(self, coin_count):
        if coin_count >= 20:
            self.turtle.health += 1
            return 20  # Return coins to deduct
        return 0
    
    def upgrade_crab_health(self, coin_count):
        if coin_count >= 20:
            self.crab.health += 1
            return 20  # Return coins to deduct
        return 0
    
    def _load_icons(self):
        """Load all item icons from assets"""
        icons = {}
        for item_key, item in self.items.items():
            try:
                icon_path = f"assets/shop/{item['icon']}.png"
                icon = pygame.image.load(icon_path).convert_alpha()
                icon = round_image(icon, 20)  # Round the corners
                icons[item_key] = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
            except:
                # Fallback if image missing
                icons[item_key] = self._create_fallback_icon(item_key)
        return icons
    
    def _load_arrows(self):
        """Load navigation arrows with fallbacks"""
        try:
            left = pygame.image.load('assets/shop/arrow_left.png').convert_alpha()
            right = pygame.image.load('assets/shop/arrow_right.png').convert_alpha()
            return pygame.transform.scale(left, (50, 50)), pygame.transform.scale(right, (50, 50))
        except:
            # Create simple arrows if images missing
            left = pygame.Surface((50, 50), pygame.SRCALPHA)
            right = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.polygon(left, (200,200,200), [(35,15), (15,25), (35,35)])
            pygame.draw.polygon(right, (200,200,200), [(15,15), (35,25), (15,35)])
            return left, right
    
    def _create_fallback_icon(self, name):
        """Create placeholder icon if image missing"""
        icon = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        color = (100,200,100) if "health" in name else (200,100,100)
        pygame.draw.rect(icon, (*color, 150), (0,0,self.icon_size,self.icon_size), border_radius=10)
        text = self.font.render(name[:4], True, (255,255,255))
        icon.blit(text, (self.icon_size//2 - text.get_width()//2, self.icon_size//2 - text.get_height()//2))
        return icon
    
    # [Keep all other methods (draw, handle_input, etc.) the same as in your original code]
    
    def handle_input(self, event, coin_count):
        """Handle shop input and return coins spent"""
        coins_spent = 0
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_LEFT and self.current_page > 0:
                self.current_page -= 1
            elif event.key == pygame.K_RIGHT and self.current_page < self.total_pages - 1:
                self.current_page += 1
            elif event.key == pygame.K_RETURN and self.hovered_item:
                # Purchase selected item
                item = self.items[self.hovered_item]
                coins_spent = item["action"](coin_count)
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            shop_pos = (self.rect.x, self.rect.y)
            
            if self.hovering_left and self.current_page > 0:
                self.current_page -= 1
            elif self.hovering_right and self.current_page < self.total_pages - 1:
                self.current_page += 1
            elif self.hovered_item:
                # Purchase hovered item
                item = self.items[self.hovered_item]
                coins_spent = item["action"](coin_count)
        
        return coins_spent